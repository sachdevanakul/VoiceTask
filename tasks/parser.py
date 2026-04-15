import json
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime
import re


def parse_voice_transcript(transcript: str) -> dict:
    """
    Uses Gemini Flash to parse a voice transcript into structured task data.
    Returns dict with: title, description, due_date (ISO string or None), confidence, raw_response
    """
    today = timezone.localtime(timezone.now())
    today_str = today.strftime('%Y-%m-%d %H:%M')
    day_name = today.strftime('%A')

    system_prompt = f"""You are a task extraction assistant. Today is {day_name}, {today_str} (IST).

Extract task information from the user's voice input and return ONLY valid JSON.

Rules for date parsing:
- "today" = {today.strftime('%Y-%m-%d')}
- "tomorrow" = next calendar day
- "next Friday" = the coming Friday (not today if today is Friday)
- "end of week" = this Sunday 23:59
- "end of month" = last day of current month 23:59
- "in 2 hours" = current time + 2 hours
- "morning" = 09:00, "afternoon" = 14:00, "evening" = 18:00, "night" = 21:00
- If no time mentioned with a date, default to 23:59 that day

Confidence scoring:
- 1.0 = very clear input, all fields extracted with certainty
- 0.7-0.9 = mostly clear, minor ambiguity in date/description
- 0.4-0.6 = significant ambiguity, user should confirm
- below 0.4 = very unclear, only partial extraction possible

Return ONLY this JSON (no markdown, no explanation):
{{
  "title": "short clear task title (max 60 chars)",
  "description": "more detail if mentioned, else empty string",
  "due_date": "YYYY-MM-DD HH:MM or null if not mentioned",
  "confidence": 0.0 to 1.0,
  "confidence_note": "brief reason if confidence < 0.8, else empty string",
  "parsed_action": "create|complete|cancel|delay",
  "delay_days": null or integer if action is delay
}}"""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": settings.GEMINI_API_KEY}
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"System: {system_prompt}\n\nVoice input: \"{transcript}\""}]}
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 300,
        }
    }

    try:
        response = requests.post(url, json=payload, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        raw_text = data['candidates'][0]['content']['parts'][0]['text'].strip()
        raw_text = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE).strip()
        parsed = json.loads(raw_text)

        if parsed.get('due_date'):
            try:
                dt = datetime.strptime(parsed['due_date'], '%Y-%m-%d %H:%M')
                aware_dt = timezone.make_aware(dt, timezone.get_current_timezone())
                parsed['due_date_iso'] = aware_dt.isoformat()
            except ValueError:
                parsed['due_date_iso'] = None
        else:
            parsed['due_date_iso'] = None

        parsed['success'] = True
        return parsed

    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'API request failed: {str(e)}',
            'title': transcript[:60],
            'description': '',
            'due_date': None,
            'due_date_iso': None,
            'confidence': 0.3,
            'confidence_note': 'Parsed without AI — please verify details',
            'parsed_action': 'create',
            'delay_days': None,
        }
    except (json.JSONDecodeError, KeyError) as e:
        return {
            'success': False,
            'error': f'Failed to parse AI response: {str(e)}',
            'title': transcript[:60],
            'description': '',
            'due_date': None,
            'due_date_iso': None,
            'confidence': 0.3,
            'confidence_note': 'Could not parse AI response',
            'parsed_action': 'create',
            'delay_days': None,
        }