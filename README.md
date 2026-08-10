# SahayakBot

SahayakBot is a text-only English, Hindi, and Marathi welfare-scheme navigator for rural and semi-urban India. Gemini provides cautious, plain-language next steps; urgent or complex cases can be handed to a real volunteer.

## Why it fits Caspian Buildathon

- One `@client.on_message` handler serves every connected channel.
- Email and Telegram are connected and verified through that same handler.
- Urgent or complex cases trigger a real Email handoff to a configured volunteer. Nothing is simulated.
- Eligibility-related questions receive a direct link to [Janyojana](https://jan-yojna.vercel.app/), the project's scheme-finder website.

## Safety stance

SahayakBot provides guidance, not official eligibility decisions, emergency response, or medical advice. It does not guarantee benefits or outcomes. It links to official verification sites and does not persist transcripts or sender identifiers.

## Setup

Use Python 3.11+.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
caspian init
caspian connect email --name "SahayakBot"
# Create a Telegram bot via @BotFather, then paste its token only at the prompt.
caspian connect telegram --name "SahayakBot"
Copy-Item .env.example .env
```

Create a Gemini API key in Google AI Studio and add it as `GEMINI_API_KEY` in `.env`. Set `EMAIL_CONNECTION_ID` to Caspian's Email connection ID and set `VOLUNTEER_EMAIL` to the consenting volunteer's Email address. Then run:

```powershell
python app.py
```

## Live demo script

1. Start `app.py`, showing that SahayakBot listens on all Caspian channels.
2. Send a Marathi Telegram message: `माझे वडील 70 वर्षांचे आहेत. त्यांना वृद्धापकाळ पेन्शन मिळू शकते का?`
3. Show the real Telegram reply with cautious guidance, documents, and an official place to verify.
4. Send a genuinely urgent test Email with the volunteer's consent, then show both the user reply and the actual volunteer handoff.
5. Show that the same handler also answers a normal Email message.

Never present a test escalation as a real emergency, and obtain the volunteer's consent before recording.

## Gemini free-tier privacy note

Gemini's free tier can have rate limits and Google states that submitted content may be used to improve its products. Use only consenting test participants in the demo; do not send real identity documents, Aadhaar numbers, medical records, or other sensitive information.

## Before public submission

- Verify every scheme fact against the official scheme portal and record the verification date.
- Keep `.env` private and scan the repository for secrets before submission.
- Record a continuous live demo showing messages arriving on both Email and Telegram.
