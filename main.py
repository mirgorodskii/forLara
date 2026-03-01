import os
import httpx
import resend
# from openai import OpenAI  # готово к использованию если понадобится
from datetime import datetime
from prompts import PROMPTS

# --- CONFIG ---
# client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
resend.api_key = os.environ["RESEND_API_KEY"]

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]

# Дата начала отсчёта — день когда запустили систему
START_DATE = datetime(2026, 3, 1)

def get_todays_prompt():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    day_index = (today - START_DATE).days  # 0, 1, 2, 3...
    index = day_index % len(PROMPTS)       # зацикливается если кончатся
    return PROMPTS[index], day_index + 1   # возвращаем текст и номер дня

# --- ЕСЛИ ЗАХОЧЕШЬ ДОБАВИТЬ GPT ОБРАБОТКУ ---
# def enhance_with_gpt(prompt):
#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": "Your system prompt here"},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=200,
#         temperature=0.9
#     )
#     return response.choices[0].message.content

def send_telegram(text):
    httpx.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
    )
    print("✅ Telegram sent")

def send_email(text):
    now = datetime.now()
    resend.Emails.send({
        "from": EMAIL_FROM,
        "to": [EMAIL_TO],
        "subject": f"✨ {now.strftime('%B %d')}",
        "html": f"""
        <div style="font-family: Georgia, serif; max-width: 480px; margin: 0 auto; padding: 40px 20px; color: #222;">
            <p style="font-size: 18px; line-height: 1.8; margin-bottom: 32px; white-space: pre-line;">{text}</p>
            <p style="font-size: 12px; color: #999;">
                {now.strftime('%A, %B %d')}
            </p>
            <p style="font-size: 13px; color: #bbb; margin-top: 32px;">— V</p>
        </div>
        """
    })
    print("✅ Email sent")

if __name__ == "__main__":
    thought, day_num = get_todays_prompt()

    # если захочешь пропустить через GPT — раскомментируй:
    # thought = enhance_with_gpt(thought)

    print(f"\n📝 Day #{day_num}:\n{thought}\n")
    send_telegram(thought)
    send_email(thought)
    print("✨ Done")
