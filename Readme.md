# VocalTask 🎙️

A voice-first task management app where you speak naturally and AI figures out the rest.

> *"Remind me to submit the quarterly report by next Friday"* → Task created with title, description, and due date extracted automatically.

---

## Features

### Core
- **Voice input** — Speak tasks naturally using your browser's mic (Web Speech API)
- **AI parsing** — Gemini 1.5 Flash extracts title, description, and due date from natural language
- **Ambiguity handling** — Confidence scoring flags uncertain parses; user can review before saving
- **Task states** — Pending → Completed / Cancelled / Delayed (with delay counter)
- **Authentication** — Register, login, logout with Django's auth system

### Standout
- **Voice feedback** — App speaks back *"Got it! Report due Friday"* after creating a task
- **Waveform animation** — Live visual feedback while recording
- **Push notifications** — Browser alerts for tasks due in 1 hour and overdue tasks
- **Confetti** — Fires when you complete a task ✨
- **Analytics dashboard** — 5 charts covering all required KPIs plus productivity score, streak, and best day of week

### Analytics KPIs
| KPI | Why it matters |
|-----|---------------|
| Tasks completed on time | Core productivity signal |
| Tasks currently pending | Workload awareness |
| Tasks delayed | Habit pattern — chronic delayers vs occasional |
| On time vs late ratio | Honest view of planning accuracy |
| Day streak | Engagement and consistency |
| Weekly productivity score | At-a-glance health metric |
| Best day of week | Tells you when you're most effective |

---

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Backend | Django 5 + PostgreSQL |  strongest stack; battle-tested |
| NLP | Gemini 1.5 Flash API | Best accuracy/cost ratio; free tier sufficient |
| Voice capture | Web Speech API | Browser-native, no cost, no library |
| Voice feedback | Web Speech Synthesis API | Browser-native, zero setup |
| Charts | Chart.js | Lightweight, beautiful defaults |
| Deployment | Railway | Native Django + Postgres support |
| Static files | WhiteNoise | Zero-config static serving |

### Why Gemini over a custom parser?
Building a custom NLP date parser would reinvent the wheel poorly. The engineering value here is in the **prompt design** and the **confidence-check layer** — if the model isn't certain, the app flags it and asks the user to confirm. That's the ambiguity-handling logic.

---

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL running locally
- A free Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### 1. Clone & install

```bash
git clone https://github.com/yourusername/vocaltask.git
cd vocaltask
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(50))">
DEBUG=True
DB_NAME=vocaltask
DB_USER=postgres
DB_PASSWORD=your_postgres_password
GEMINI_API_KEY=your_gemini_key_here
```

### 3. Set up the database

```bash
# Create the database in psql
psql -U postgres -c "CREATE DATABASE vocaltask;"

# Run migrations
python manage.py migrate
```

### 4. Run

```bash
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000), register an account, and start speaking.

> **Note:** Voice input requires Chrome or Edge (Web Speech API). Firefox has limited support.

---

## Deployment (Railway)

1. Push your repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add a PostgreSQL plugin
4. Set environment variables in Railway dashboard (same as `.env` but `DEBUG=False`, `ALLOWED_HOSTS=yourdomain.railway.app`)
5. Railway auto-runs `python manage.py migrate` via the `Procfile`

---

## Project Structure

```
vocaltask/
├── vocaltask/          # Django project config
│   ├── settings.py
│   └── urls.py
├── tasks/              # Core app
│   ├── models.py       # Task model with all states
│   ├── views.py        # API + page views
│   ├── parser.py       # Gemini NLP parser
│   └── urls.py
├── accounts/           # Auth app
├── templates/          # HTML templates
│   ├── base.html
│   ├── tasks/
│   └── accounts/
├── static/
│   ├── css/main.css    # Full design system
│   └── js/main.js      # Voice, notifications, confetti
├── requirements.txt
├── Procfile
└── .env.example
```

---

## Design Decisions

**Voice-first UX** — The mic is the hero element, centered above the fold. Typing is available as a fallback but never the primary path.

**Confirm before save** — Parsed results are shown editably before creating the task. Low-confidence parses are flagged in amber. This prevents silent errors from bad transcriptions.

**Delay ≠ Cancel** — These are meaningfully different states. A delayed task gets its due date pushed and a delay counter incremented — so analytics can distinguish "I postponed this intentionally" from "I abandoned this."

**Analytics that actually help** — The best day of week chart tells you *when* you work best. The streak counter builds habit. The productivity score is honest — it's tasks completed / tasks created this week, not a vanity metric.

---

Built by Nakul 
