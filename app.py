"""SahayakBot: one Caspian handler for WhatsApp, Email, and future channels.

Text-only English/Hindi/Marathi welfare-scheme guidance with real volunteer handoff.
It is not an emergency service and never claims that someone is eligible or that
a benefit has been approved.
"""
import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from caspian_sdk import CommClient

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("sahayakbot")
# The SDK polls for new events every second; keep successful poll noise out of
# the demo terminal while preserving our own status/error messages.
logging.getLogger("httpx").setLevel(logging.WARNING)

ROOT = Path(__file__).parent
SCHEMES = json.loads((ROOT / "data" / "schemes.json").read_text(encoding="utf-8"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
VOLUNTEER_CONNECTION = os.getenv("EMAIL_CONNECTION_ID", "")
VOLUNTEER_RECIPIENT = os.getenv("VOLUNTEER_EMAIL", "")
DEMO_AUTO_ESCALATE = os.getenv("DEMO_AUTO_ESCALATE", "false").lower() == "true"

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY is required. Copy .env.example to .env first.")

ai = genai.Client()
client = CommClient()

EMERGENCY_WORDS = {
    "ambulance", "bleeding", "unconscious", "suicide", "self harm", "attack",
    "emergency", "urgent", "hospital", "accident", "खून", "आत्महत्या", "आपत्काल",
    "रुग्णवाहिका", "तातडी",
}


def obvious_emergency(text: str) -> bool:
    normalized = text.lower()
    return any(word in normalized for word in EMERGENCY_WORDS)


def assess(text: str) -> dict[str, Any]:
    """Return constrained English/Hindi/Marathi scheme guidance for text."""
    prompt = f"""You are SahayakBot, a careful welfare-scheme navigator for India.
Support exactly three languages: English, Hindi (Devanagari), and Marathi
(Devanagari). Reply in the same language used by the person. If the person
writes another language, ask them to write in English, Hindi, or Marathi. You are not a government
authority: never promise eligibility, payment, approval, or a medical outcome.
Use only the scheme facts below. If information is uncertain, say how to verify it.
If the user describes immediate danger, state that the person should contact local
emergency services and a trusted nearby person; do not claim that help was dispatched.

SCHEME FACTS:
{json.dumps(SCHEMES, ensure_ascii=False)}

USER MESSAGE: {text}

Return valid JSON only with this shape:
{{
  "urgent": true | false,
  "needs_human": true | false,
  "matched_scheme_ids": ["scheme id"],
  "reply": "same-language answer, maximum 140 words",
  "handoff_summary": "short English summary for a volunteer, no invented facts"
}}"""
    log.info("Requesting Gemini scheme guidance")
    interaction = ai.interactions.create(model=MODEL, input=prompt, store=False)
    log.info("Gemini response received")
    data = json.loads(interaction.output_text or "{}")
    data["matched_scheme_ids"] = [s["id"] for s in SCHEMES if s["id"] in data.get("matched_scheme_ids", [])]
    data["urgent"] = bool(data.get("urgent")) or obvious_emergency(text)
    data["needs_human"] = bool(data.get("needs_human")) or data["urgent"]
    return data


def escalation_text(message: Any, transcript: str, analysis: dict[str, Any]) -> str:
    # Share only what a volunteer needs. Do not persist transcripts or sender IDs.
    source = getattr(message, "channel", "unknown channel")
    return (
        "SAHAYAKBOT — volunteer handoff\n\n"
        f"Source channel: {source}\n"
        f"Urgent: {'yes' if analysis['urgent'] else 'no'}\n"
        f"Summary: {analysis.get('handoff_summary', 'User requests scheme-navigation help.')}\n"
        f"User message: {transcript}\n\n"
        "Please respond through the shared Caspian conversation; do not request unnecessary documents."
    )


def send_volunteer_handoff(message: Any, transcript: str, analysis: dict[str, Any]) -> bool:
    if not VOLUNTEER_CONNECTION or not VOLUNTEER_RECIPIENT:
        log.warning("Urgent/complex case detected but Email volunteer route is not configured")
        return False
    try:
        client.initiate(VOLUNTEER_CONNECTION, VOLUNTEER_RECIPIENT,
                        escalation_text(message, transcript, analysis))
        log.info("Volunteer handoff sent")
        return True
    except Exception:
        # A notification failure must never suppress the response to the person
        # who asked for help.
        log.exception("Volunteer handoff failed")
        return False


@client.on_message
def on_message(message: Any) -> None:
    """The only inbound handler: works for WhatsApp, Telegram, and any new channel."""
    log.info("Received a message on %s", getattr(message, "channel", "unknown"))
    try:
        transcript = (getattr(message, "text", "") or "").strip()
        if not transcript:
            message.reply("Please send a text message in English, Hindi, or Marathi describing what you need help with.")
            return
        result = assess(transcript)
        should_handoff = result["urgent"] or result["needs_human"] and DEMO_AUTO_ESCALATE
        handoff_sent = send_volunteer_handoff(message, transcript, result) if should_handoff else False
        suffix = "\n\nI have alerted a volunteer to review this." if handoff_sent else ""
        if result["urgent"] and not handoff_sent:
            suffix += "\n\nPlease contact local emergency services or a trusted person nearby now."
        message.reply((result.get("reply") or "I could not safely assess that. Please try again with a little more detail.") + suffix)
        log.info("Reply sent on %s", getattr(message, "channel", "unknown"))
    except Exception:
        log.exception("Message processing failed")
        message.reply("Sorry, I could not process that just now. Please try again shortly.")


if __name__ == "__main__":
    log.info("SahayakBot listening on all connected Caspian channels")
    client.listen()
