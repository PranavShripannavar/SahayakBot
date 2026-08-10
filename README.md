# SahayakBot

Text-only English/Hindi/Marathi welfare-scheme guidance and crisis handoff for rural and semi-urban India. Gemini produces cautious, plain-language next steps; urgent cases route to a real volunteer.

## Why it fits Caspian Buildathon

- One `@client.on_message` handler serves every connected channel.
- Connect WhatsApp for citizen-facing English/Hindi/Marathi chat and Email for volunteer handoffs. The same handler can also answer an Email message, proving inbound multi-channel support.
- The handoff is real: a configured Telegram recipient receives an actual Caspian message. No simulated alerts.

## Safety stance

SahayakBot is guidance, not a government authority or emergency service. It does not guarantee eligibility, benefits, or medical outcomes. It keeps scheme claims in `data/schemes.json`, links to official verification sites, and does not store transcripts or sender identifiers.

## Setup

Use Python 3.11+.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
caspian init
caspian connect email --name "SahayakBot"
# WhatsApp is a paid Caspian channel; request Buildathon starter credit before connecting it.
caspian connect whatsapp --name "SahayakBot"
Copy-Item .env.example .env
```

Create a free-tier Gemini key in Google AI Studio, add it as `GEMINI_API_KEY` in `.env`, then fill in the Email connection ID and volunteer email emitted/used by Caspian. Then run:

```powershell
python app.py
```

## Live demo script

1. Send a Hindi WhatsApp message: “मेरे पिता 70 वर्ष के हैं। क्या उन्हें पेंशन मिल सकती है?”
2. Show the WhatsApp reply with cautious eligibility guidance, documents, and the official place to verify.
3. Send a genuinely urgent test message with your volunteer’s consent. Show the real Email handoff.
4. Send a normal Email message to the same bot and show it responding from the same `on_message` function.

Never present a test escalation as a real emergency, and obtain the volunteer's consent before recording the demo.

## Gemini free-tier privacy note

Gemini's free tier has limited availability/rate limits and Google states that submitted content may be used to improve its products. Use only consenting test participants in the demo; do not send real identity documents, Aadhaar numbers, medical records, or other sensitive information.

## Before public submission

- Verify every scheme fact against the official scheme portal and record the verification date.
- Keep `.env` private and make the repository public only after secret scanning.
- Record a continuous demo video that shows actual messages arriving on both connected channels.
