# lara-daily

Daily personal thought generator — sends a warm, personalized message every morning via Telegram and Email.

## How it works

Every day at 8am NY time the script:
1. Picks a random theme from 40 options
2. Gets the current moon phase
3. Generates a personal thought via GPT-4o
4. Sends it to Telegram and Email

## Deploy on Railway

1. Push this repo to GitHub
2. Create a new project on Railway → **Cron Job**
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set run command: `python main.py`
6. Set schedule: `0 13 * * *` (8am New York time)
7. Add environment variables (see below)

## Environment Variables

```
OPENAI_API_KEY=sk-...
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
RESEND_API_KEY=re_...
EMAIL_FROM=onboarding@resend.dev
EMAIL_TO=recipient@example.com
```
