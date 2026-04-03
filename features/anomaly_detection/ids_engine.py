from scapy.all import IP, TCP, UDP, ICMP
from features.anomaly_detection.rule_engine import rule_based_detection
from features.anomaly_detection.prevention_engine import block_ip, unblock_expired_ips
from core.utils.logger import log_event, log_alert

def extract_features(packet):
    return {
        "packet_size": len(packet),
        "protocol": packet.proto if IP in packet else 0
    }

def process_packet(packet):
    if IP not in packet:
        return

    src_ip = packet[IP].src
    features = extract_features(packet)

    alert = rule_based_detection(features, src_ip)

    if alert:
        block_ip(src_ip)
        

        log_alert(
            alert_type=alert,
            source="IDS",
            src_ip=src_ip,
            action="BLOCKED"
        )

        print(f"[ALERT] {alert} | {src_ip} | BLOCKED")
    else:
        log_event("normal", src_ip)

    unblock_expired_ips()
