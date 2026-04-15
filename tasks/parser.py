import json
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import re
from dateutil import parser as date_parser


# ---------- CLEAN TRANSCRIPT ----------
def clean_transcript(text: str) -> str:
    # Fix "20 26th" → "2026"
    text = re.sub(r'(\d{2})\s+(\d{2})(st|nd|rd|th)', r'\1\2', text)

    # Fix "20 april 20 26" → "20 april 2026"
    text = re.sub(r'(\d{1,2}\s+\w+)\s+(\d{2})\s+(\d{2})', r'\1 \2\3', text)

    return text.strip().capitalize()


# ---------- FALLBACK DATE EXTRACT ----------
def extract_date_fallback(text: str):
    try:
        match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', text)
        if match:
            dt = datetime.strptime(match.group(1), "%d %B %Y")
            return dt.strftime("%Y-%m-%d 23:59")
    except:
        pass
    return None


def parse_voice_transcript(transcript: str) -> dict:
    transcript = clean_transcript(transcript)
    now = timezone.localtime(timezone.now())

    today = now.strftime('%Y-%m-%d')
    tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')

    # ---------- SYSTEM PROMPT ----------
    system_prompt = f"""
You are an AI that extracts structured task data from user voice input.

CURRENT DATE: {today}

RULES:
- Return ONLY valid JSON (no markdown, no explanation)
- Keys:
  - title (string)
  - description (string)
  - due_date (string in "YYYY-MM-DD HH:MM" or null)
  - parsed_action (create | complete | cancel | delay)
  - confidence (0.0 to 1.0)
  - confidence_note (string)
  - delay_days (integer or null)

DATE RULES:
- "today" → {today}
- "tomorrow" → {tomorrow}
- Convert ALL dates (e.g., "20 April 2026") into "YYYY-MM-DD HH:MM"
- If date exists but time is missing → use 23:59
- If NO date mentioned → return null

TIME RULES:
- morning → 09:00
- afternoon → 14:00
- evening → 18:00
- night → 21:00
- Convert 12hr times to 24hr

TITLE RULE:
- Remove phrases like "remind me to", "i need to"
- Keep it short and action-based

EXAMPLES:

Input: "remind me to submit report next friday"
Output:
{{"title":"Submit report","description":"","due_date":"2026-04-18 23:59","parsed_action":"create","confidence":0.95,"confidence_note":"","delay_days":null}}

Input: "call mom tomorrow morning"
Output:
{{"title":"Call mom","description":"","due_date":"{tomorrow} 09:00","parsed_action":"create","confidence":0.95,"confidence_note":"","delay_days":null}}

Input: "meeting on 20 April 2026"
Output:
{{"title":"Meeting","description":"","due_date":"2026-04-20 23:59","parsed_action":"create","confidence":0.95,"confidence_note":"","delay_days":null}}
"""

    # ---------- GEMINI API ----------
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    params = {"key": settings.GEMINI_API_KEY}

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": transcript}]}
        ],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 300,
        }
    }

    try:
        response = requests.post(url, json=payload, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        raw_text = data['candidates'][0]['content']['parts'][0]['text'].strip()

        # Clean markdown if any
        raw_text = re.sub(r'^```json\s*', '', raw_text)
        raw_text = re.sub(r'\s*```$', '', raw_text)

        parsed = json.loads(raw_text)

        # ---------- DEBUG ----------
        print("Transcript:", transcript)
        print("Gemini raw:", raw_text)
        print("Parsed:", parsed)

        # ---------- DATE HANDLING ----------
        due = parsed.get('due_date')

        if due and due not in ['null', '', None]:
            try:
                dt = date_parser.parse(due)
                aware_dt = timezone.make_aware(dt, timezone.get_current_timezone())

                parsed['due_date_iso'] = aware_dt.isoformat()
                parsed['due_date'] = aware_dt.strftime('%Y-%m-%d %H:%M')

            except Exception:
                parsed['due_date'] = None
                parsed['due_date_iso'] = None
        else:
            # Try fallback extraction
            fallback_date = extract_date_fallback(transcript)

            if fallback_date:
                dt = date_parser.parse(fallback_date)
                aware_dt = timezone.make_aware(dt, timezone.get_current_timezone())

                parsed['due_date'] = aware_dt.strftime('%Y-%m-%d %H:%M')
                parsed['due_date_iso'] = aware_dt.isoformat()
            else:
                parsed['due_date'] = None
                parsed['due_date_iso'] = None

        parsed['success'] = True
        parsed['transcript'] = transcript

        return parsed

    except Exception as e:
        return fallback_parser(transcript, str(e))


# ---------- FALLBACK ----------
def fallback_parser(transcript: str, error: str) -> dict:
    now = timezone.localtime(timezone.now())
    transcript_lower = transcript.lower()

    due_date = None

    if "tomorrow" in transcript_lower:
        due_date = (now + timedelta(days=1)).strftime('%Y-%m-%d') + " 23:59"
    elif "today" in transcript_lower:
        due_date = now.strftime('%Y-%m-%d') + " 23:59"

    return {
        'success': False,
        'error': error,
        'title': transcript[:60],
        'description': '',
        'due_date': due_date,
        'due_date_iso': None,
        'confidence': 0.4,
        'confidence_note': 'Fallback parser used',
        'parsed_action': 'create',
        'delay_days': None,
        'transcript': transcript,
    }