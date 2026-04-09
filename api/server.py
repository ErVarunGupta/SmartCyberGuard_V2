import threading
import random
import time

from services.ids_service import process_packet
from fastapi import FastAPI
from pydantic import BaseModel

# from services.system_service import get_system_data
from services.ai_orchestrator import ai_response
from services.cleaner_service import scan_files, delete_files
from services.cleaner_engine import scan_system
from services.system_service import get_system_metrics
from services.auto_trainer import start_auto_trainer
from services.response_model import load_data

app = FastAPI()



# def simulate_network():
#     normal_ips = ["192.168.1.1", "10.0.0.5"]
#     attacker_ips = ["45.33.32.1", "103.21.244.1"]

#     while True:
#         # Normal traffic (slow)
#         process_packet(random.choice(normal_ips), "normal")

#         # Attack traffic (fast burst)
#         if random.random() < 0.4:
#             attacker_ip = random.choice(attacker_ips)

#             # simulate burst
#             for _ in range(random.randint(3, 6)):
#                 process_packet(attacker_ip, "attack")

#         time.sleep(1)


from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    mode: str = "GEMINI"   # default


from scapy.all import IP, TCP

def simulate_network():
    while True:
        packet = IP(src="192.168.1.100") / TCP(dport=80)
        process_packet(packet)
        time.sleep(1)

# @app.on_event("startup")
# def start_services():
#     run_sniffer()


@app.get("/")
def home():
    return {"status": "API Running"}


# =========================
# SYSTEM
# =========================




@app.get("/metrics")
def metrics():
    return get_system_metrics()


# =========================
# IDS
# =========================

from services.ids_service import get_ids_data, get_blocked_ips, block_ip

from services.ids_service import start_ids

@app.on_event("startup")
def startup_event():
    start_auto_trainer()
    load_data()
def start_ids_service():
    import threading
    threading.Thread(target=start_ids, daemon=True).start()


# =========================
# IDS MAIN API
# =========================
@app.get("/ids")
def ids_data():
    return get_ids_data()


# =========================
# BLOCKED IPS LIST
# =========================
@app.get("/ids/blocked")
def blocked_ips():
    return {
        "blocked_ips": get_blocked_ips()
    }


# =========================
# MANUAL BLOCK
# =========================
@app.post("/ids/block")
def block_ip_api(data: dict):
    return block_ip(data.get("ip"))


# =========================
# AI
# =========================
class ChatRequest(BaseModel):
    message: str
    mode: str = "GEMINI"


@app.post("/ai")
def ai_chat(req: ChatRequest):
    return {
        "response": ai_response(req.message, req.mode)
    }


## =========================
# CLEANER
# =========================

# 🔥 Helper function (NOT API)
def generate_insights(safe, junk, review):
    safe_size = sum(f["size"] for f in safe)
    junk_size = sum(f["size"] for f in junk)

    total_cleanable = round(safe_size + junk_size, 2)

    old_files = len([f for f in review if f["age_days"] > 30])

    return {
        "freeable_space_mb": total_cleanable,
        "safe_cleanup_mb": round(safe_size, 2),
        "junk_cleanup_mb": round(junk_size, 2),
        "old_files_count": old_files,
        "recommendation": "Clean SAFE files first for risk-free optimization"
    }


# ✅ MAIN SCAN API
@app.get("/cleaner/scan")
def cleaner_scan():
    files, total_size = scan_system()

    safe, junk, review, important = [], [], [], []

    for f in files:
        cat = f.get("category")

        if cat == "SAFE":
            safe.append(f)
        elif cat == "JUNK":
            junk.append(f)
        elif cat == "IMPORTANT":
            important.append(f)
        else:
            review.append(f)

    insights = generate_insights(safe, junk, review)

    return {
        "summary": {
            "total_files": len(files),
            "safe_files": len(safe),
            "junk_files": len(junk),
            "review_files": len(review),
            "important_files": len(important),
            "total_size_mb": round(total_size, 2)
        },
        "insights": insights,
        "safe": safe[:200],
        "junk": junk[:200],
        "review": review[:200],
        "important": important[:200]
    }


# =========================
# DELETE API
# =========================
class CleanRequest(BaseModel):
    paths: list


@app.post("/cleaner/clean")
def cleaner_clean(req: CleanRequest):
    deleted = delete_files(req.paths)

    return {
        "deleted_files": deleted,
        "message": f"{len(deleted)} files deleted successfully"
    }



import os
import subprocess
from fastapi import HTTPException


@app.get("/cleaner/preview")
def preview_file(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        os.startfile(path)   # Windows only
        return {"message": "File opened"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))