# VocalTask 🎙️

> *Speak naturally. AI does the rest.*

A voice-first task management app where you describe tasks in plain English and AI extracts everything — title, description, and due date — automatically.

**"Remind me to submit the quarterly report by next Friday"**
→ Task created. Due date set. Done.

---

## 📸 Screenshots

<img width="1338" height="521" alt="image" src="https://github.com/user-attachments/assets/999a1f7b-c695-4c4b-82cc-c9d63f84f301" />
<img width="1322" height="524" alt="image" src="https://github.com/user-attachments/assets/53b29e9d-123d-455c-93fb-f4af5ea4b85f" />
<img width="1349" height="539" alt="image" src="https://github.com/user-attachments/assets/d21ddd22-ebe6-460a-9a20-636e604e88a6" />

---

## ✨ Features

### Core
- **Voice input** — Speak tasks naturally via browser mic (Web Speech API — no library needed)
- **AI-powered parsing** — Gemini 1.5 Flash extracts title, description, and due date from natural language
- **Confirm before save** — Parsed results are editable before storing; low-confidence parses are flagged in amber
- **Task lifecycle** — Pending → Completed / Cancelled / Delayed (with delay counter per task)
- **Authentication** — Register, login, logout via Django's built-in auth system

### Intelligent Behaviour
- **Voice feedback** — App speaks back *"Got it! Report due Friday"* after task creation (Web Speech Synthesis)
- **Waveform animation** — Live visual indicator while recording
- **Confetti on completion** — Because small wins deserve celebration ✨
- **Delay ≠ Cancel** — Delayed tasks get their due date pushed and a delay counter incremented, preserving intent in analytics

### Analytics Dashboard

| KPI | Why it matters |
|-----|----------------|
| Tasks completed on time | Core productivity signal |
| Tasks pending | Workload awareness |
| Tasks delayed | Chronic delayers vs occasional slip-ups |
| On-time vs late ratio | Honest view of planning accuracy |
| Weekly productivity score | Tasks completed / tasks created this week |
| Day streak | Consistency and habit building |
| Best day of week | When you're actually most effective |

---

## 🧠 How It Works

```
User speaks
    ↓
Browser → speech-to-text (Web Speech API)
    ↓
Text sent to Django backend
    ↓
Gemini 1.5 Flash parses into structured fields (title, description, due date)
    ↓
Confidence score evaluated → low confidence flagged for user review
    ↓
User confirms / edits parsed result
    ↓
Task saved to PostgreSQL
    ↓
Voice feedback + UI update
```

---

## 🛠️ Tech Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| Backend | Django 5 | Battle-tested, batteries-included |
| Database | PostgreSQL | Production-ready relational DB |
| NLP | Gemini 1.5 Flash (Google AI Studio) | Best accuracy/cost ratio; free tier sufficient |
| Voice Input | Web Speech API | Browser-native, zero cost, zero setup |
| Voice Output | Web Speech Synthesis API | Browser-native TTS, no library needed |
| Charts | Chart.js | Lightweight, beautiful defaults |
| Deployment | Railway | Native Django + PostgreSQL support |
| Static Files | WhiteNoise | Zero-config static file serving |

### Why Gemini over a custom NLP parser?

Building a custom date/intent parser would reinvent the wheel poorly. The real engineering here is the **prompt design** and the **confidence-check layer**: if the model isn't certain about a parse, the app flags it and asks the user to confirm rather than silently creating a wrong task.

---

## ⚙️ Setup

### Prerequisites

- Python 3.11+
- PostgreSQL running locally
- Gemini API key from [aistudio.google.com](https://aistudio.google.com) (free tier works)

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/vocaltask.git
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

```env
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_urlsafe(50))">
DEBUG=True

DB_NAME=vocaltask
DB_USER=postgres
DB_PASSWORD=your_postgres_password

GEMINI_API_KEY=your_gemini_key_here
```

> ⚠️ Never commit `.env` to version control. It's already in `.gitignore`.

### 3. Create the database & run migrations

```bash
psql -U postgres -c "CREATE DATABASE vocaltask;"
python manage.py migrate
```

### 4. Start the development server

```bash
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000), register an account, and start speaking.

> **Note:** Voice input requires Chrome or Edge. Firefox has limited Web Speech API support.


## 📁 Project Structure

```
vocaltask/
├── vocaltask/          # Django project config
│   ├── settings.py
│   └── urls.py
├── tasks/              # Core app
│   ├── models.py       # Task model with all states
│   ├── views.py        # API + page views
│   ├── parser.py       # Gemini NLP integration & confidence layer
│   └── urls.py
├── accounts/           # Auth (register, login, logout)
├── templates/
│   ├── base.html
│   ├── tasks/
│   └── accounts/
├── static/
│   ├── css/main.css    # Full design system
│   └── js/main.js      # Voice capture, notifications
├── requirements.txt
├── manage.py
├── Procfile
└── .env
```

---

## 🎨 Design Decisions

**Voice-first UX** — The mic is the hero element, centered above the fold. Typing is a fallback, never the primary path.

**Human-in-the-loop validation** — AI output is never blindly trusted. Parsed results are shown editably before the task is created. Uncertain parses are highlighted so users catch errors before they matter.

**Delay ≠ Cancel** — These are meaningfully different signals. Delaying pushes the due date and increments a delay counter, so analytics can distinguish intentional postponement from abandonment.

**Analytics that actually help** — The best-day-of-week chart tells you *when* you work best. The streak counter reinforces habits. The productivity score is honest: tasks completed / tasks created this week — not a vanity metric.

---

## ⚠️ Known Limitations

- Voice input works best in Chromium-based browsers (Chrome, Edge)
- Requires an internet connection for speech recognition and AI parsing
- NLP accuracy depends on microphone quality and speech clarity
- No mobile app — browser-only for now

---

## 🚧 Planned Improvements

- [ ] Background task scheduling for reminders (Celery + Redis)
- [ ] Mobile-responsive UI improvements
- [ ] Offline fallback for text-based task entry
- [ ] Smarter confidence calibration with user feedback loop
- [ ] Recurring task support (*"every Monday morning"*)
- [ ] Export tasks to CSV / calendar (`.ics`)
- [ ] Dark mode

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request




Built by [Nakul Sachdeva](https://github.com/nakulsachdeva)
