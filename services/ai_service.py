from services.system_service import get_system_metrics


# =========================
# AI RESPONSE
# =========================
def generate_response(user_msg: str):
    data = get_system_metrics()

    cpu = data.get("cpu", 0)
    ram = data.get("ram", 0)
    disk = data.get("disk", 0)
    state = data.get("state", "Unknown")
    health = data.get("health_score", 0)

    msg = user_msg.lower()

    # =========================
    # SYSTEM QUESTIONS
    # =========================
    if "cpu" in msg:
        return f"Your CPU usage is {cpu}%."

    elif "ram" in msg:
        return f"Your RAM usage is {ram}%."

    elif "disk" in msg:
        return f"Disk usage is {disk}%."

    elif "battery" in msg:
        return f"Battery is at {data.get('battery', 0)}%."

    elif "state" in msg or "status" in msg:
        return f"System is currently in {state} state."

    elif "health" in msg:
        return f"System health score is {health}."

    # =========================
    # PERFORMANCE ANALYSIS
    # =========================
    elif "slow" in msg or "lag" in msg:
        if state == "High Load":
            return "Your system is under high load. Close heavy apps immediately."
        elif state == "Moderate":
            return "System is moderately loaded. Monitor usage."
        else:
            return "System looks stable."

    # =========================
    # RECOMMENDATIONS
    # =========================
    elif "recommend" in msg or "suggest" in msg:
        rec = data.get("recommendation", [])
        return "Recommendations:\n" + "\n".join(rec)

    # =========================
    # DEFAULT
    # =========================
    return f"System is {state}. CPU: {cpu}%, RAM: {ram}%."