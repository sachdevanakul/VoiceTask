import json
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import re
from dateutil import parser as date_parser


# ---------- CLEAN TRANSCRIPT ----------
def clean_transcript(text: str) -> str:
    text = re.sub(r'(\d{2})\s+(\d{2})(st|nd|rd|th)', r'\1\2', text)
    text = re.sub(r'(\d{1,2}\s+\w+)\s+(\d{2})\s+(\d{2})', r'\1 \2\3', text)
    return text.strip().capitalize()


# ---------- FALLBACK DATE ----------
def extract_date_fallback(text: str, now):
    text = text.lower()

    if "tomorrow" in text:
        dt = now + timedelta(days=1)
        return dt.replace(hour=23, minute=59)

    if "today" in text:
        return now.replace(hour=23, minute=59)

    if "next friday" in text:
        days_ahead = (4 - now.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        dt = now + timedelta(days=days_ahead)
        return dt.replace(hour=23, minute=59)

    # Generic date like "20 April 2026"
    try:
        match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', text)
        if match:
            return date_parser.parse(match.group(1)).replace(hour=23, minute=59)
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
Extract structured task data from user input.

Return ONLY JSON with:
title, description, due_date, parsed_action, confidence, confidence_note, delay_days

RULES:
- Always extract due_date if any date phrase exists (e.g., tomorrow, next Friday)
- Convert all dates to "YYYY-MM-DD HH:MM"
- If time missing → use 23:59
- If no date → null
- Remove phrases like "remind me to", "i need to" from title
- parsed_action = create unless specified otherwise

Examples:

"submit report next friday" →
{{"title":"Submit report","description":"","due_date":"2026-04-18 23:59","parsed_action":"create","confidence":0.95,"confidence_note":"","delay_days":null}}

"call mom tomorrow" →
{{"title":"Call mom","description":"","due_date":"{tomorrow} 23:59","parsed_action":"create","confidence":0.95,"confidence_note":"","delay_days":null}}
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
            "response_mime_type": "application/json"
        }
    }

    try:
        response = requests.post(url, json=payload, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        raw_text = data['candidates'][0]['content']['parts'][0]['text'].strip()

        parsed = json.loads(raw_text)

        # ---------- DEBUG ----------
        print("Transcript:", transcript)
        print("Gemini raw:", raw_text)

        # ---------- CLEAN TITLE ----------
        parsed['title'] = re.sub(
            r'^(remind me to|i need to|please|can you)\s+',
            '',
            parsed.get('title', ''),
            flags=re.IGNORECASE
        ).strip().capitalize()

        # ---------- DATE HANDLING ----------
        due = parsed.get('due_date')

        if due and due not in ['null', '', None]:
            try:
                dt = date_parser.parse(due)
            except:
                dt = None
        else:
            dt = None

        # ---------- FALLBACK ----------
        if not dt:
            dt = extract_date_fallback(transcript, now)

        if dt:
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


# ---------- FINAL FALLBACK ----------
def fallback_parser(transcript: str, error: str) -> dict:
    now = timezone.localtime(timezone.now())
    dt = extract_date_fallback(transcript, now)

    return {
        'success': False,
        'error': error,
        'title': transcript[:60],
        'description': '',
        'due_date': dt.strftime('%Y-%m-%d %H:%M') if dt else None,
        'due_date_iso': None,
        'confidence': 0.4,
        'confidence_note': 'Fallback parser used',
        'parsed_action': 'create',
        'delay_days': None,
        'transcript': transcript,
    }