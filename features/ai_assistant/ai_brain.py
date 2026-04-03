def analyze(metrics, prediction, intrusion):

    actions = []
    message = ""

    # 🔋 Battery
    if metrics["battery"] < 20:
        message = "Battery is low, please plug charger"
        actions.append("speak")

    # ⚠️ Hang risk
    elif prediction == 2:
        message = "System may hang, closing heavy apps"
        actions.append("kill_apps")

    # 🛡️ Intrusion
    elif intrusion:
        message = "Attack detected, blocking IP"
        actions.append("block_ip")

    else:
        message = "System running normally"

    return message, actions