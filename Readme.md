# VocalTask 🎙️

> **Speak naturally. AI does the rest.**

A voice-first task management app where you describe tasks in plain English and AI extracts everything — title, description, and due date — automatically.

**"Remind me to submit the quarterly report by next Friday"** → *Task created. Due date set. Done.*

---

## 🌐 Live Demo

🚀 **Try it here:** [voicetask-4.onrender.com](https://voicetask-4.onrender.com)

> [!NOTE]
> The app may take ~30–60 seconds to load if inactive (free hosting cold start).

---

## 📸 Screenshots

![Screenshot 1](https://github.com/user-attachments/assets/999a1f7b-c695-4c4b-82cc-c9d63f84f301)
![Screenshot 2](https://github.com/user-attachments/assets/53b29e9d-123d-455c-93fb-f4af5ea4b85f)
![Screenshot 3](https://github.com/user-attachments/assets/d21ddd22-ebe6-460a-9a20-636e604e88a6)

---

## ✨ Features

### Core
* **Voice input** — Speak tasks naturally via browser mic (Web Speech API).
* **AI-powered parsing** — Gemini 1.5 Flash extracts structured task data.
* **Confirm before save** — Editable parsed results before storing.
* **Task lifecycle** — Pending → Completed / Cancelled / Delayed.
* **Authentication** — Secure Register, login, and logout.

### Intelligent Behavior
* **Voice feedback** — App speaks confirmation after task creation.
* **Waveform animation** — Live recording indicator.
* **Confetti on completion** ✨
* **Delay tracking** — Keeps analytics meaningful.

---

## 📊 Analytics Dashboard

| KPI | Why it matters |
| :--- | :--- |
| **Tasks completed on time** | Productivity signal |
| **Tasks pending** | Workload awareness |
| **Tasks delayed** | Delay patterns |
| **Weekly productivity score** | Real performance metric |
| **Day streak** | Habit building |
| **Best day of week** | Peak efficiency |

---

## 🧠 How It Works

1. **Input:** User speaks into the microphone.
2. **Processing:** Browser converts Speech-to-Text.
3. **AI Extraction:** Django backend sends text to Gemini AI to extract JSON data.
4. **Validation:** User confirms or edits the parsed data.
5. **Storage:** Data is saved to a PostgreSQL database.
6. **Output:** User receives voice feedback and the UI updates.

---

## 🛠️ Tech Stack

* **Backend:** Django 5
* **Database:** PostgreSQL
* **AI:** Gemini 1.5 Flash
* **Voice Input:** Web Speech API
* **Voice Output:** Web Speech Synthesis
* **Charts:** Chart.js
* **Deployment:** Render
* **Static Files:** WhiteNoise

---

## ⚙️ Local Setup

### Prerequisites
* Python 3.11+
* PostgreSQL
* Gemini API Key

### 1. Clone & Install
```bash
git clone [https://github.com/sachdevanakul/VoiceTask.git](https://github.com/sachdevanakul/VoiceTask.git)
cd vocaltask
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

### 2. Configure Environment
Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secret_key
DEBUG=True

DB_NAME=vocaltask
DB_USER=postgres
DB_PASSWORD=your_password

GEMINI_API_KEY=your_api_key
# Run migrations
python manage.py migrate

# Start server
python manage.py runserver

vocaltask/
├── vocaltask/          # Core settings
├── tasks/              # Task management logic
├── accounts/           # Auth and users
├── templates/          # HTML views
├── static/             # CSS & JS
├── requirements.txt
├── manage.py
└── .env


## ⚠️ Known Limitations
* **Browser Compatibility:** Optimized specifically for **Chrome** and **Edge** to ensure stable Web Speech API performance.
* **Connectivity:** Requires a stable internet connection for real-time AI parsing and speech recognition.
* **Platform:** Currently a web-only application; no native mobile app is available yet.

---

## 🚧 Future Improvements
* **Reminders:** Implementing background task notifications using **Celery** and **Redis**.
* **Responsive Design:** Enhancing the UI for a more seamless mobile-first experience.
* **Calendar Integrations:** Syncing tasks directly to **Google Calendar**.
* **Themes:** Adding a native **Dark Mode** for better low-light usability.

---

## 👨‍💻 Author
**Nakul Sachdeva** — [GitHub Profile](https://github.com/sachdevanakul)

⭐ **If you like this project, give it a star on GitHub — it helps!**