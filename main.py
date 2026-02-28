import os
import json
import httpx
import resend
from openai import OpenAI
from datetime import datetime
from pathlib import Path
import ephem

# --- CONFIG ---
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
resend.api_key = os.environ["RESEND_API_KEY"]

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]

COUNTERS_FILE = Path("/app/data/counters.json")
HISTORY_FILE = Path("/app/data/history.json")

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

CONSTRUCTOR = {
    "A_genre": [
        "observation — notice something small and precise",
        "question — one question that hangs in the air unanswered",
        "micro-story — tiny narrative with a beginning and end",
        "paradox — two opposite things that are both true",
        "image without conclusion — a picture, no explanation",
        "journal entry — as if Lara wrote it to herself",
        "prediction — something that might happen today",
        "memory — something past as a point of anchor",
        "letter — directly to her, intimate",
        "manifesto — a small statement about how the world works"
    ],
    "B_tone": [
        "melancholic — quiet sadness without drama",
        "playful — light, with a wink",
        "sharp — precise and slightly unexpected",
        "tender — warmth without sentimentality",
        "curious — as if the world just became interesting",
        "dry — minimum words, maximum meaning",
        "solemn — something important said simply",
        "ironic — smiling at yourself or the world",
        "dreamy — slightly not here",
        "grounded — very concrete, very now"
    ],
    "C_actor": [
        "Bubbles the dog",
        "coffee",
        "morning in Hunters Point",
        "work at the UN / the big world",
        "her journal",
        "meditation / breath",
        "music",
        "running / body movement",
        "travel / another place",
        "season / weather / light",
        "Sasha — her partner and love",
        "theater",
        "Sex and the City — the series she loves",
        "singing",
        "her elegance — the way she looks and carries herself",
        "Jung's archetypes — the inner figures she knows"
    ],
    "D_wish": [
        "direct and simple (e.g. 'have a slow morning')",
        "embedded in metaphor — the wish is hidden",
        "question as wish (e.g. 'what if today was just yours?')",
        "one word at the end ('rest.' / 'run.' / 'stay.')",
        "through permission ('you're allowed to...')",
        "through action — wish as a verb",
        "through the nature of the moment — 'the day already has it'",
        "through opposite — what NOT to do today",
        "addressed to the day / city / dog, not to Lara",
        "no wish — the text itself is the gift"
    ],
    "E_entry": [
        "a specific concrete detail",
        "an abstract idea immediately",
        "a question from the first word",
        "a paradox in the first sentence",
        "a physical sensation",
        "a movement or action",
        "a very specific place",
        "a moment in time — time of day or year",
        "a sound or smell",
        "direct 'you' — address Lara immediately"
    ],
    "F_length": [
        "one sentence — that's it",
        "two sentences — contrast or development",
        "three — escalation",
        "four — with a twist at the end",
        "very short + one word separately on its own line",
        "one long complex sentence",
        "three short punchy lines",
        "question + answer",
        "statement + its negation + resolution",
        "fragment — as if torn from the middle of a thought"
    ],
    "G_address": [
        "name at the very start ('Lara,')",
        "name in the middle",
        "no name — universal",
        "'you know that feeling...' — no name but very personal",
        "'hey' — informal",
        "through her role ('the one who keeps a journal knows...')",
        "through her action ('when you run tomorrow...')",
        "second person but distanced ('one notices...')",
        "third person — a small story about her",
        "silent address — text just exists, no address"
    ]
}

SYSTEM_PROMPT = """You write a daily personal thought for Lara.

Lara lives in New York, in Hunters Point, Long Island City.
She works at the UN. She loves spiritual practices and meditation, keeps a journal.
Goes hiking, travels, runs, dances, does sports.
Loves coffee, loves to sleep. Listens to music. Loves theater and singing.
She has a dog named Bubbles. Her partner is Sasha.
Loves Sex and the City. Interested in Jung's archetypes.
She carries herself with elegance.

The thought is sent by her friend Vadim.
Occasionally the thought can feel like it comes from someone who knows her personally —
a subtle warmth, like a wink, without being explicit.

RULES:
- No advice, no lecturing
- NEVER use: "gentle", "quiet", "whisper", "hushed", "soft magic"
- No pathos, no grand words
- Language: English, warm, alive, specific"""


def load_json(path):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return {} if "counters" in str(path) else []

def save_json(path, data):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
    except Exception as e:
        print(f"⚠️ Could not save {path.name}: {e}")


def pick_constructor():
    counters = load_json(COUNTERS_FILE)
    picked = {}
    for key, arr in CONSTRUCTOR.items():
        idx = counters.get(key, 0) % len(arr)
        picked[key] = arr[idx]
        counters[key] = idx + 1
    save_json(COUNTERS_FILE, counters)
    return picked


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

    # Sequential theme
    counters = load_json(COUNTERS_FILE)
    theme_idx = counters.get("theme", 0) % len(THEMES)
    theme = THEMES[theme_idx]
    counters["theme"] = theme_idx + 1
    save_json(COUNTERS_FILE, counters)

    # Constructor combo
    combo = pick_constructor()
    combo_lines = "\n".join([
        f"GENRE: {combo['A_genre']}",
        f"TONE: {combo['B_tone']}",
        f"ACTOR (anchor the thought in this): {combo['C_actor']}",
        f"WISH APPROACH: {combo['D_wish']}",
        f"OPENING (start with): {combo['E_entry']}",
        f"LENGTH: {combo['F_length']}",
        f"ADDRESS: {combo['G_address']}"
    ])

    # Previous 7 for context
    history = load_json(HISTORY_FILE)
    prev_context = ""
    if history:
        prev7 = history[:7]
        lines = "\n".join([f"{i+1}. [{h['date']} · {h['theme']}] {h['thought']}" for i, h in enumerate(prev7)])
        prev_context = f"\n\nPREVIOUS {len(prev7)} THOUGHTS (avoid repeating themes, formats, images, conclusions):\n{lines}"

    user_prompt = f"""Today: {day_of_week}, {date_str}
Moon phase: {moon_phase}
Theme: {theme}

TODAY'S CONSTRUCTION PARAMETERS — follow all precisely:
{combo_lines}{prev_context}

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

    history.insert(0, {
        "thought": thought,
        "theme": theme,
        "moon": moon_phase,
        "date": now.strftime("%B %d"),
        "combo": {k: v.split("—")[0].strip() for k, v in combo.items()}
    })
    save_json(HISTORY_FILE, history[:30])

    return thought, theme, moon_phase, combo


def send_telegram(text):
    httpx.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
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
    thought, theme, moon_phase, combo = generate_thought()
    print(f"\n📝 Thought:\n{thought}\n")
    print(f"🎯 Theme: {theme} | 🌕 Moon: {moon_phase}")
    print(f"🔧 Combo: { {k: v.split('—')[0].strip() for k, v in combo.items()} }\n")
    send_telegram(thought)
    send_email(thought, theme, moon_phase)
    print("✨ Done")
