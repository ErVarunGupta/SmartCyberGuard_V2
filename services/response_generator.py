def generate_smart_response(user_query, retrieved_response, context):
    """
    Generate improved response using:
    - Retrieved knowledge
    - Real-time system data
    """

    system = context.get("system", {})
    ids = context.get("ids", {})
    cleaner = context.get("cleaner", {})

    response = f"""
🧠 SmartGuard AI Analysis:

Query: {user_query}

🔍 System Status:
- CPU: {system.get('cpu')}%
- RAM: {system.get('ram')}%
- State: {system.get('state')}

🛡 Security:
- Alerts: {ids.get('alerts')}
- Blocked IPs: {ids.get('blocked_ips')}

🧹 Storage:
- Junk Files: {cleaner.get('junk')}

💡 Insight:
{retrieved_response}

⚡ Recommendation:
- Optimize running applications
- Monitor suspicious activity
- Clean unnecessary files
"""

    return response.strip()