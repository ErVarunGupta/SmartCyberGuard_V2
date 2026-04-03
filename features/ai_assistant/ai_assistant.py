import psutil
import time
from google import genai
# from core.monitor import collect_system_metrics
from features.monitoring.monitor import collect_system_metrics
from core.config.api_keys import GEMINI_API_KEY

# ✅ Initialize client
client = genai.Client(api_key=GEMINI_API_KEY)

# 🧠 Memory
conversation_history = []


def get_ai_response(user_query):

    metrics = collect_system_metrics()

    # 🔥 Top processes
    processes = sorted(
        [(p.info['name'], p.info['cpu_percent']) 
         for p in psutil.process_iter(['name', 'cpu_percent'])],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    # 🔁 Conversation memory
    conversation_history.append(f"User: {user_query}")
    history_text = "\n".join(conversation_history[-5:])

    # 🧠 Smart prompt
    prompt = f"""
You are an advanced AI system assistant.

Conversation History:
{history_text}

System Data:
CPU: {metrics['cpu']}%
RAM: {metrics['ram']}%
Disk: {metrics['disk']}%
Battery: {metrics['battery']}%

Top CPU Processes:
{processes}

User Question:
{user_query}

Rules:
- Answer based on real system data
- Be specific
- Keep it short and practical
"""

    # 🔁 Retry logic
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",   
                contents=prompt
            )

            text = response.text

            if text:
                conversation_history.append(f"AI: {text}")
                return text

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", e)
            time.sleep(2)

    return "AI assistant is busy. Try again."