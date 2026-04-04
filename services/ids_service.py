import time
import joblib
import os
import threading
from queue import Queue
from collections import defaultdict, deque

from scapy.all import sniff, IP, TCP, UDP
import pandas as pd

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ISO_MODEL_PATH = os.path.join(BASE_DIR, "models", "ids_iso_model.pkl")
RF_MODEL_PATH = os.path.join(BASE_DIR, "models", "ids_rf_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "ids_scaler.pkl")

iso_model = joblib.load(ISO_MODEL_PATH)
rf_model = joblib.load(RF_MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# =========================
# GLOBAL STATE
# =========================
blocked_ips_set = set()
logs = []
packets_count = 0
alerts_count = 0
unique_ips = set()

# =========================
# QUEUE SYSTEM (CRITICAL)
# =========================
packet_queue = Queue(maxsize=10000)

# =========================
# FLOW BUFFER
# =========================
flow_buffer = defaultdict(lambda: {
    "timestamps": deque(maxlen=50),
    "sizes": [],
    "ports": set(),
    "tcp": 0,
    "udp": 0
})

WINDOW_SECONDS = 5

# =========================
# DETECTION CONTROL
# =========================
last_detection_time = {}
DETECTION_INTERVAL = 3  # seconds


# =========================
# FEATURE EXTRACTION
# =========================
def extract_features(ip_data):
    timestamps = list(ip_data["timestamps"])

    if len(timestamps) < 2:
        return None

    duration = timestamps[-1] - timestamps[0]
    packet_count = len(timestamps)
    byte_count = sum(ip_data["sizes"])

    avg_packet_size = byte_count / packet_count if packet_count else 0
    packet_rate = packet_count / duration if duration > 0 else 0

    tcp_ratio = ip_data["tcp"] / packet_count if packet_count else 0
    udp_ratio = ip_data["udp"] / packet_count if packet_count else 0

    unique_ports = len(ip_data["ports"])

    return [
        packet_count,
        byte_count,
        avg_packet_size,
        packet_rate,
        tcp_ratio,
        udp_ratio,
        unique_ports
    ]


# =========================
# ML DECISION ENGINE
# =========================
def detect_attack(features):
    if features is None:
        return "normal", 0

    # features_scaled = scaler.transform([features])


    cols = [
        "packet_count", "byte_count", "avg_packet_size",
        "packet_rate", "tcp_ratio", "udp_ratio", "unique_ports"
    ]

    df = pd.DataFrame([features], columns=cols)
    features_scaled = scaler.transform(df)

    iso_pred = iso_model.predict(features_scaled)[0]
    rf_pred = rf_model.predict(features_scaled)[0]
    rf_probs = rf_model.predict_proba(features_scaled)[0]

    attack_prob = rf_probs[1]  # probability of attack

    # =========================
    # 🎯 STRICT REAL ATTACK LOGIC
    # =========================

    # 🔴 HIGH CONFIDENCE ATTACK
    if rf_pred == 1 and attack_prob > 0.85:
        return "attack", attack_prob

    # 🟡 SUSPICIOUS (DON'T BLOCK)
    elif iso_pred == -1 or attack_prob > 0.6:
        return "suspicious", attack_prob

    # 🟢 NORMAL
    return "normal", attack_prob


# =========================
# BLOCK SYSTEM
# =========================
def block_ip(ip):
    if ip in blocked_ips_set:
        return

    blocked_ips_set.add(ip)

    try:
        os.system(
            f'netsh advfirewall firewall add rule name="Block_{ip}" dir=in action=block remoteip={ip}'
        )
    except:
        pass


# =========================
# HANDLE PACKET (WORKER)
# =========================
def handle_packet(packet):
    global packets_count, alerts_count

    if IP not in packet:
        return

    src_ip = packet[IP].src
    packets_count += 1
    unique_ips.add(src_ip)

    now = time.time()

    # =========================
    # DETECTION RATE LIMIT
    # =========================
    last = last_detection_time.get(src_ip, 0)
    if now - last < DETECTION_INTERVAL:
        return

    last_detection_time[src_ip] = now

    # =========================
    # FLOW UPDATE
    # =========================
    data = flow_buffer[src_ip]

    data["timestamps"].append(now)
    data["sizes"].append(len(packet))

    if TCP in packet:
        data["tcp"] += 1
        data["ports"].add(packet[TCP].dport)

    elif UDP in packet:
        data["udp"] += 1
        data["ports"].add(packet[UDP].dport)

    if len(data["timestamps"]) < 5:
        return

    if now - data["timestamps"][0] > WINDOW_SECONDS:

        features = extract_features(data)
        label, confidence = detect_attack(features)

        action = "allowed"

        if label == "attack" and confidence > 0.9:
            alerts_count += 1
            action = "blocked"
            block_ip(src_ip)

        elif label == "suspicious":
            alerts_count += 1
            action = "allowed"

        # =========================
        # 🧠 INTELLIGENCE LAYER
        # =========================
        attack_type = classify_attack(features)
        risk_score = calculate_risk(label, confidence, features)
        reasons = explain_detection(features)
        country = get_geo(src_ip)

        log = {
            "time": time.strftime("%H:%M:%S"),
            "label": label,
            "src_ip": src_ip,
            "traffic_type": "TCP/UDP",
            "action": action,
            "confidence": round(confidence, 2),

            "attack_type": attack_type,
            "risk_score": risk_score,
            "reasons": reasons,

            # 🌍 NEW
            "country": country
        }

        logs.append(log)

        if len(logs) > 100:
            logs.pop(0)

        # RESET FLOW
        flow_buffer[src_ip] = {
            "timestamps": deque(maxlen=50),
            "sizes": [],
            "ports": set(),
            "tcp": 0,
            "udp": 0
        }


# =========================
# QUEUE WORKER
# =========================
def packet_worker():
    while True:
        packet = packet_queue.get()
        try:
            handle_packet(packet)
        except Exception as e:
            print("Worker Error:", e)


# =========================
# SNIFFER (FAST)
# =========================
def process_packet(packet):
    try:
        packet_queue.put_nowait(packet)
    except:
        pass


# =========================
# START IDS
# =========================
def start_ids():
    threading.Thread(target=packet_worker, daemon=True).start()
    sniff(prn=process_packet, store=False)


# =========================
# API FUNCTIONS
# =========================
def get_ids_data():
    return {
        "packets": packets_count,
        "alerts": alerts_count,
        "blocked_ips": len(blocked_ips_set),
        "unique_ips": len(unique_ips),
        "logs": logs
    }


def get_blocked_ips():
    return list(blocked_ips_set)


def classify_attack(features):
    packet_count, byte_count, avg_size, rate, tcp_ratio, udp_ratio, ports = features

    # 🚨 DDoS
    if packet_count > 150 and rate > 40:
        return "DDoS Attack"

    # 🚨 Port Scan
    if ports > 30 and packet_count < 100:
        return "Port Scan"

    # 🚨 Bot / Script Traffic
    if tcp_ratio > 0.95 and rate > 20:
        return "Bot Traffic"

    return "Unknown"



def calculate_risk(label, confidence, features):
    packet_count, byte_count, avg_size, rate, tcp_ratio, udp_ratio, ports = features

    score = 0

    # Base score
    if label == "attack":
        score += 60
    elif label == "suspicious":
        score += 30

    # ML confidence
    score += int(confidence * 30)

    # Behavior factors
    if rate > 50:
        score += 10
    if ports > 50:
        score += 10

    return min(score, 100)



def explain_detection(features):
    packet_count, byte_count, avg_size, rate, tcp_ratio, udp_ratio, ports = features

    reasons = []

    if rate > 30:
        reasons.append("High traffic rate")

    if packet_count > 100:
        reasons.append("Too many packets")

    if ports > 30:
        reasons.append("Multiple ports targeted")

    if tcp_ratio > 0.9:
        reasons.append("TCP flood pattern")

    return reasons if reasons else ["Normal behavior"]


def get_geo(ip):
    try:
        import requests
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        data = res.json()
        return data.get("country", "Unknown")
    except:
        return "Unknown"