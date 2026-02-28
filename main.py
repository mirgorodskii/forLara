import os
import random
import httpx
import resend
from openai import OpenAI
from datetime import datetime
import ephem

# --- CONFIG ---
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
resend.api_key = os.environ["RESEND_API_KEY"]

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]

# --- THEMES ---
THEMES = [
    "boundary", "light", "movement", "pause", "connection",
    "time", "trust", "wonder", "acceptance", "risk",
    "return", "chance", "memory", "horizon", "loss",
    "finding", "transition", "breath", "waiting", "simplicity",
    "silence", "rhythm", "emptiness", "warmth", "growth",
    "repetition", "discovery", "tiredness", "play", "farewell",
    "threshold", "trace", "pattern", "beginning", "reflection",
    "depth", "contrast", "balance", "infinity", "presence"
]

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """You write a daily personal thought for Lara.

Lara lives in New York, in Hunters Point, Long Island City.
She works at the UN. She loves spiritual practices and meditation, keeps a journal.
Goes hiking, travels, runs, dances, does sports.
Loves coffee, loves to sleep. Listens to music.
She has a dog named Bubbles who she adores.

The thought is sent by her friend Vadim.
Occasionally (not every day) the thought can feel like it comes from someone
who knows her personally — a subtle warmth, like a wink, without being explicit.

Each day you receive: date, day of week, moon phase, and a theme.
Based on this you write one thought — warm, slightly poetic, 2-4 sentences.

RULES:
- No advice, no lecturing
- Don't mention all details at once — each day focus on one thing
- Occasionally mention Bubbles, Hunters Point, coffee — but rarely, to stay unpredictable
- No pathos, no grand words
- Feeling: like a close friend wrote it just for her on this particular morning
- Language: English, warm, alive"""


def get_moon_phase():
    moon = ephem.Moon(datetime.now())
    phase = moon.phase
    if phase < 7: return "new moon"
    elif phase < 14: return "waxing crescent"
    elif phase < 21: return "first quarter"
    elif phase < 28: return "waxing gibbous"
    elif phase < 35: return "full moon"
    elif phase < 42: return "waning gibbous"
    elif phase < 49: return "last quarter"
    else: return "waning crescent"


def generate_thought():
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    day_of_week = now.strftime("%A")
    moon_phase = get_moon_phase()
    theme = random.choice(THEMES)

    user_prompt = f"""Today: {day_of_week}, {date_str}
Moon phase: {moon_phase}
Theme: {theme}

Write one morning thought for Lara."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=200,
        temperature=0.9
    )

    thought = response.choices[0].message.content
    return thought, theme, moon_phase


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


def send_email(text, theme, moon_phase):
    now = datetime.now()
    resend.Emails.send({
        "from": EMAIL_FROM,
        "to": [EMAIL_TO],
        "subject": f"✨ {now.strftime('%B %d')}",
        "html": f"""
        <div style="font-family: Georgia, serif; max-width: 480px; margin: 0 auto; padding: 40px 20px; color: #222;">
            <p style="font-size: 18px; line-height: 1.8; margin-bottom: 32px;">{text}</p>
            <p style="font-size: 12px; color: #999;">
                {now.strftime('%A, %B %d')} &nbsp;·&nbsp; {moon_phase} &nbsp;·&nbsp; {theme}
            </p>
            <p style="font-size: 13px; color: #bbb; margin-top: 32px;">— V</p>
        </div>
        """
    })
    print("✅ Email sent")


if __name__ == "__main__":
    print("🌙 Generating thought for Lara...")
    thought, theme, moon_phase = generate_thought()
    print(f"\n📝 Thought:\n{thought}\n")
    print(f"🎯 Theme: {theme} | 🌕 Moon: {moon_phase}\n")
    send_telegram(thought)
    send_email(thought, theme, moon_phase)
    print("✨ Done")
