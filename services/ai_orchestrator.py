import time
import traceback

# =========================
# INTERNAL SERVICES
# =========================
from services.system_service import get_system_metrics
from services.ids_service import get_ids_data
from services.cleaner_engine import scan_system

from services.ai_model_service import predict_intent_with_confidence
from services.ai_knowledge_base import save_knowledge

from services.response_model import get_similar_response
from services.response_generator import generate_smart_response

# Gemini
from google import genai
from core.config.api_keys import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# MEMORY
# =========================
conversation_memory = []


# =========================
# CONTEXT BUILDER
# =========================
def build_context():
    try:
        system = get_system_metrics()
    except:
        system = {}

    try:
        ids = get_ids_data()
    except:
        ids = {}

    try:
        result = scan_system()

        if isinstance(result, tuple):
            files = result[0]
        else:
            files = result

        safe_files = len([f for f in files if f.get("category") == "SAFE"])
        junk_files = len([f for f in files if f.get("category") == "JUNK"])
        review_files = len([f for f in files if f.get("category") == "REVIEW"])

    except Exception as e:
        print("Cleaner error:", e)
        safe_files = 0
        junk_files = 0
        review_files = 0

    return {
        "system": system,
        "ids": {
            "alerts": ids.get("alerts", 0),
            "blocked_ips": ids.get("blocked_ips", 0),
            "unique_ips": ids.get("unique_ips", 0)
        },
        "cleaner": {
            "safe": safe_files,
            "junk": junk_files,
            "review": review_files
        }
    }


# =========================
# PROMPT BUILDER
# =========================
def build_prompt(user_msg, context, intent):
    history = "\n".join(conversation_memory[-5:])

    return f"""
You are SmartGuard AI — advanced system + cybersecurity assistant.

USER INTENT: {intent}

SYSTEM:
CPU: {context['system'].get('cpu')}%
RAM: {context['system'].get('ram')}%
Disk: {context['system'].get('disk')}%
Battery: {context['system'].get('battery')}%
State: {context['system'].get('state')}
Health: {context['system'].get('health_score')}

IDS:
Alerts: {context['ids']['alerts']}
Blocked IPs: {context['ids']['blocked_ips']}

CLEANER:
Junk Files: {context['cleaner']['junk']}

Conversation:
{history}

User:
{user_msg}

Rules:
- Be intelligent
- Give actionable suggestions
- Be concise
"""


# =========================
# MAIN AI FUNCTION
# =========================
def ai_response(user_msg: str, mode: str = "GEMINI"):
    try:
        mode = mode.upper()
        print(f"[AI MODE]: {mode}")

        # =========================
        # CONTEXT
        # =========================
        context = build_context()

        # =========================
        # INTENT
        # =========================
        try:
            intent, confidence = predict_intent_with_confidence(user_msg)
        except:
            intent, confidence = "general", 0.0

        # =========================
        # SEMANTIC SEARCH
        # =========================
        response, score = get_similar_response(user_msg)
        print(f"[DEBUG] Similarity Score: {score}")

        # =========================
        # 🟢 SMART AI MODE
        # =========================
        if mode == "SMART":

            if response and score > 0.45:
                smart_response = generate_smart_response(
                    user_query=user_msg,
                    retrieved_response=response,
                    context=context
                )

                # 🔥 LEARNING (self + improvement)
                save_knowledge(user_msg, context, smart_response, intent)

                return f"[Smart AI]\n{smart_response}"

            return "⚠️ Smart AI is still learning. Use Gemini for better results."

        # =========================
        # 🔵 GEMINI MODE (DEFAULT)
        # =========================
        prompt = build_prompt(user_msg, context, intent)

        conversation_memory.append(f"User: {user_msg}")

        for attempt in range(3):
            try:
                res = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=prompt
                )

                text = res.text.strip()

                if text:
                    conversation_memory.append(f"AI: {text}")

                    # 🔥 LEARNING FROM GEMINI (VERY IMPORTANT)
                    save_knowledge(user_msg, context, text, intent)

                    return text

            except Exception as e:
                print(f"[Gemini Error] Attempt {attempt+1}:", e)
                time.sleep(2)

        return "AI assistant is busy. Try again."

    except Exception as e:
        print("CRITICAL AI ERROR:", e)
        traceback.print_exc()
        return "AI system error occurred."