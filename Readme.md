# VocalTask 🎙️

> *Speak naturally. AI does the rest.*

A voice-first task management app where you describe tasks in plain English and AI extracts everything — title, description, and due date — automatically.

**"Remind me to submit the quarterly report by next Friday"**
→ Task created. Due date set. Done.

---

## 🌐 Live Demo

🚀 **Try it here:**
👉 https://voicetask-4.onrender.com

> ⚠️ Note: The app may take ~30–60 seconds to load if inactive (free hosting cold start).

---

## 📸 Screenshots

<img width="1338" height="521" src="https://github.com/user-attachments/assets/999a1f7b-c695-4c4b-82cc-c9d63f84f301" />
<img width="1322" height="524" src="https://github.com/user-attachments/assets/53b29e9d-123d-455c-93fb-f4af5ea4b85f" />
<img width="1349" height="539" src="https://github.com/user-attachments/assets/d21ddd22-ebe6-460a-9a20-636e604e88a6" />

---

## ✨ Features

### Core

* **Voice input** — Speak tasks naturally via browser mic (Web Speech API)
* **AI-powered parsing** — Gemini 1.5 Flash extracts structured task data
* **Confirm before save** — Editable parsed results before storing
* **Task lifecycle** — Pending → Completed / Cancelled / Delayed
* **Authentication** — Register, login, logout

### Intelligent Behaviour

* **Voice feedback** — App speaks confirmation after task creation
* **Waveform animation** — Live recording indicator
* **Confetti on completion** ✨
* **Delay tracking** — Keeps analytics meaningful

---

## 📊 Analytics Dashboard

| KPI                       | Why it matters          |
| ------------------------- | ----------------------- |
| Tasks completed on time   | Productivity signal     |
| Tasks pending             | Workload awareness      |
| Tasks delayed             | Delay patterns          |
| Weekly productivity score | Real performance metric |
| Day streak                | Habit building          |
| Best day of week          | Peak efficiency         |

---

## 🧠 How It Works

```
User speaks
    ↓
Speech-to-text (browser)
    ↓
Django backend
    ↓
Gemini AI parses task
    ↓
User confirms/edit
    ↓
Saved to PostgreSQL
    ↓
Voice feedback + UI update
```

---

## 🛠️ Tech Stack

| Layer        | Technology           |
| ------------ | -------------------- |
| Backend      | Django 5             |
| Database     | PostgreSQL           |
| AI           | Gemini 1.5 Flash     |
| Voice Input  | Web Speech API       |
| Voice Output | Web Speech Synthesis |
| Charts       | Chart.js             |
| Deployment   | Render               |
| Static Files | WhiteNoise           |

---

## ⚙️ Local Setup

### Prerequisites

* Python 3.11+
* PostgreSQL
* Gemini API Key

---

### 1. Clone & Install

```bash
git clone https://github.com/sachdevanakul/VoiceTask.git
cd vocaltask
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your_secret_key
DEBUG=True

DB_NAME=vocaltask
DB_USER=postgres
DB_PASSWORD=your_password

GEMINI_API_KEY=your_api_key
```

---

### 3. Run Migrations

```bash
python manage.py migrate
```

---

### 4. Start Server

```bash
python manage.py runserver
```

Open: http://localhost:8000

---

## 📁 Project Structure

```
vocaltask/
├── vocaltask/
├── tasks/
├── accounts/
├── templates/
├── static/
├── requirements.txt
├── manage.py
├── Procfile
└── .env
```

---

## ⚠️ Known Limitations

* Works best on Chrome / Edge
* Requires internet for AI + speech
* No mobile app yet

---

## 🚧 Future Improvements

* Task reminders (Celery + Redis)
* Mobile responsiveness
* Recurring tasks
* Export to calendar
* Dark mode

---

## 🎯 Key Engineering Highlights

* Human-in-the-loop AI validation
* Confidence-based parsing
* Voice-first UX design
* Real-world deploy (Django + PostgreSQL + cloud)

---

## 👨‍💻 Author

**Nakul Sachdeva**
https://github.com/sachdevanakul

---

## ⭐ If you like this project

Give it a star on GitHub — it helps!
