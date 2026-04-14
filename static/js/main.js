// ── CSRF helper ──
function getCookie(name) {
  const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : null;
}

const CSRF = getCookie('csrftoken');
const headers = { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF };

// ── VOICE RECORDER ──
class VoiceRecorder {
  constructor() {
    this.recognition = null;
    this.isRecording = false;
    this.transcript = '';
    this.init();
  }

  init() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      const btn = document.getElementById('mic-btn');
      if (btn) {
        btn.disabled = true;
        document.getElementById('voice-status').textContent = 'Voice not supported in this browser. Try Chrome.';
      }
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-IN';

    this.recognition.onresult = (e) => {
      const interim = Array.from(e.results).map(r => r[0].transcript).join('');
      this.updateTranscript(interim);
      if (e.results[e.results.length - 1].isFinal) {
        this.transcript = interim;
      }
    };

    this.recognition.onend = () => {
      this.stopRecording();
      if (this.transcript) this.parseTranscript(this.transcript);
    };

    this.recognition.onerror = (e) => {
      this.stopRecording();
      setStatus('Could not capture audio. Please try again.');
    };
  }

  startRecording() {
    if (!this.recognition) return;
    this.transcript = '';
    this.isRecording = true;
    this.recognition.start();

    const micBtn = document.getElementById('mic-btn');
    const waveform = document.getElementById('waveform');
    if (micBtn) micBtn.classList.add('recording');
    if (waveform) waveform.classList.add('active');
    setStatus('Listening... speak your task');
    hideResult();
  }

  stopRecording() {
    this.isRecording = false;
    const micBtn = document.getElementById('mic-btn');
    const waveform = document.getElementById('waveform');
    if (micBtn) micBtn.classList.remove('recording');
    if (waveform) waveform.classList.remove('active');
    setStatus('Processing...');
    if (this.recognition) {
      try { this.recognition.stop(); } catch (e) {}
    }
  }

  updateTranscript(text) {
    const preview = document.getElementById('transcript-preview');
    const textEl = document.getElementById('transcript-text');
    if (preview && textEl) {
      textEl.textContent = text;
      preview.classList.add('visible');
    }
  }

  async parseTranscript(text) {
    setStatus('Analysing with AI...');
    try {
      const res = await fetch('/tasks/api/parse-voice/', {
        method: 'POST', headers,
        body: JSON.stringify({ transcript: text })
      });
      const data = await res.json();
      showParsedResult(data, text);
    } catch (err) {
      setStatus('Failed to parse. Please try again.');
    }
  }

  toggle() {
    if (this.isRecording) this.stopRecording();
    else this.startRecording();
  }
}

function setStatus(msg) {
  const el = document.getElementById('voice-status');
  if (el) el.textContent = msg;
}

function hideResult() {
  const el = document.getElementById('parsed-result');
  if (el) el.classList.remove('visible');
}

function showParsedResult(data, transcript) {
  const el = document.getElementById('parsed-result');
  if (!el) return;

  document.getElementById('field-title').value = data.title || '';
  document.getElementById('field-description').value = data.description || '';

  if (data.due_date) {
    const dt = new Date(data.due_date_iso || data.due_date);
    if (!isNaN(dt)) {
      document.getElementById('field-due').value = dt.toISOString().slice(0, 16);
    }
  }

  const confidence = data.confidence || 0;
  const badge = document.getElementById('confidence-badge');
  badge.textContent = confidence >= 0.8 ? 'High confidence' : confidence >= 0.5 ? 'Check details' : 'Low confidence — please review';
  badge.className = 'confidence-badge ' + (confidence >= 0.8 ? 'confidence-high' : confidence >= 0.5 ? 'confidence-med' : 'confidence-low');

  el.dataset.transcript = transcript;
  el.dataset.confidence = confidence;
  el.dataset.dueIso = data.due_date_iso || '';
  el.classList.add('visible');

  // Voice feedback
  speakBack(data.title, data.due_date);
  setStatus('Ready to save — confirm or edit the details above.');
}

function speakBack(title, due) {
  if (!window.speechSynthesis) return;
  let msg = `Got it! Task: ${title}.`;
  if (due) msg += ` Due ${due}.`;
  const utt = new SpeechSynthesisUtterance(msg);
  utt.rate = 1.1; utt.pitch = 1;
  window.speechSynthesis.speak(utt);
}

// ── CREATE TASK ──
async function createTask() {
  const el = document.getElementById('parsed-result');
  const title = document.getElementById('field-title').value.trim();
  const description = document.getElementById('field-description').value.trim();
  const dueInput = document.getElementById('field-due').value;

  if (!title) { alert('Please provide a task title.'); return; }

  let due_date_iso = null;
  if (dueInput) {
    due_date_iso = new Date(dueInput).toISOString();
  } else if (el.dataset.dueIso) {
    due_date_iso = el.dataset.dueIso;
  }

  const body = {
    title, description,
    due_date_iso,
    transcript: el.dataset.transcript || '',
    confidence: parseFloat(el.dataset.confidence || 1),
  };

  try {
    const res = await fetch('/tasks/api/create/', { method: 'POST', headers, body: JSON.stringify(body) });
    const data = await res.json();
    if (data.success) {
      hideResult();
      document.getElementById('transcript-preview')?.classList.remove('visible');
      setStatus('Task created! Speak another task anytime.');
      triggerConfetti();
      addTaskToList(data.task);
      updateCounts();
    } else {
      alert('Failed to create task: ' + data.error);
    }
  } catch (err) {
    alert('Error creating task. Please try again.');
  }
}

function addTaskToList(task) {
  const list = document.getElementById('task-list');
  if (!list) return;

  const empty = list.querySelector('.empty-state');
  if (empty) empty.remove();

  const card = createTaskCard(task);
  list.insertAdjacentHTML('afterbegin', card);
}

function createTaskCard(task) {
  const due = task.due_date ? new Date(task.due_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : 'No due date';
  const overdue = task.due_date && new Date(task.due_date) < new Date() && task.status === 'pending';
  return `
  <div class="task-card status-${task.status}" id="task-${task.id}">
    <div class="task-indicator"></div>
    <div class="task-body">
      <div class="task-title">${escapeHtml(task.title)}</div>
      <div class="task-meta">
        <span class="due ${overdue ? 'overdue' : ''}">${due}</span>
        <span class="status-badge badge-${task.status}">${task.status}</span>
      </div>
    </div>
    <div class="task-actions">
      ${task.status === 'pending' || task.status === 'delayed' ? `
        <button class="btn btn-success btn-sm" onclick="updateStatus(${task.id}, 'complete')">Done</button>
        <button class="btn btn-ghost btn-sm" onclick="updateStatus(${task.id}, 'delay')">+1d</button>
        <button class="btn btn-danger btn-sm" onclick="updateStatus(${task.id}, 'cancel')">Cancel</button>
      ` : ''}
    </div>
  </div>`;
}

// ── TASK STATUS UPDATE ──
async function updateStatus(taskId, action) {
  try {
    const res = await fetch(`/tasks/api/tasks/${taskId}/status/`, {
      method: 'POST', headers,
      body: JSON.stringify({ action, days: 1 })
    });
    const data = await res.json();
    if (data.success) {
      const card = document.getElementById(`task-${taskId}`);
      if (card) {
        card.className = `task-card status-${data.status}`;
        card.querySelector('.status-badge').textContent = data.status;
        card.querySelector('.status-badge').className = `status-badge badge-${data.status}`;
        card.querySelector('.task-indicator').className = 'task-indicator';
        if (action === 'complete') triggerConfetti();
        if (action !== 'cancel' && action !== 'complete') {} else {
          card.querySelector('.task-actions').innerHTML = '';
        }
      }
      updateCounts();
    }
  } catch (err) { console.error('Status update failed', err); }
}

// ── COUNTS ──
async function updateCounts() {
  try {
    const res = await fetch('/tasks/api/tasks/');
    const data = await res.json();
    const tasks = data.tasks;
    const counts = { pending: 0, completed: 0, delayed: 0, cancelled: 0 };
    tasks.forEach(t => counts[t.status] = (counts[t.status] || 0) + 1);
    Object.entries(counts).forEach(([k, v]) => {
      const el = document.getElementById(`count-${k}`);
      if (el) el.textContent = v;
    });
  } catch (e) {}
}

// ── CONFETTI ──
function triggerConfetti() {
  const colors = ['#7c6dfa', '#22d3a5', '#fbbf24', '#f87171', '#a78bfa'];
  for (let i = 0; i < 40; i++) {
    setTimeout(() => {
      const el = document.createElement('div');
      el.className = 'confetti-piece';
      el.style.cssText = `
        left: ${Math.random() * 100}vw;
        top: -10px;
        background: ${colors[Math.floor(Math.random() * colors.length)]};
        transform: rotate(${Math.random() * 360}deg);
        animation-duration: ${1 + Math.random()}s;
        animation-delay: ${Math.random() * 0.3}s;
      `;
      document.body.appendChild(el);
      setTimeout(() => el.remove(), 2000);
    }, i * 30);
  }
}

// ── PUSH NOTIFICATIONS ──
async function requestNotifications() {
  if (!('Notification' in window)) return;
  if (Notification.permission === 'default') {
    await Notification.requestPermission();
  }
  if (Notification.permission === 'granted') {
    scheduleNotificationChecks();
  }
}

function scheduleNotificationChecks() {
  setInterval(checkDueTasks, 60 * 1000);
  checkDueTasks();
}

async function checkDueTasks() {
  if (Notification.permission !== 'granted') return;
  try {
    const res = await fetch('/tasks/api/tasks/');
    const data = await res.json();
    const now = new Date();
    data.tasks.forEach(task => {
      if (task.status !== 'pending' || !task.due_date) return;
      const due = new Date(task.due_date);
      const diff = due - now;
      const oneHour = 60 * 60 * 1000;
      if (diff > 0 && diff < oneHour) {
        const mins = Math.round(diff / 60000);
        new Notification('Task due soon!', {
          body: `"${task.title}" is due in ${mins} minutes.`,
          icon: '/static/favicon.ico',
        });
      } else if (diff < 0 && diff > -oneHour) {
        new Notification('Task overdue!', {
          body: `"${task.title}" was due ${Math.round(-diff / 60000)} minutes ago.`,
        });
      }
    });
  } catch (e) {}
}

// ── UTILS ──
function escapeHtml(text) {
  const el = document.createElement('div');
  el.textContent = text;
  return el.innerHTML;
}

// ── INIT ──
document.addEventListener('DOMContentLoaded', () => {
  const recorder = new VoiceRecorder();

  const micBtn = document.getElementById('mic-btn');
  if (micBtn) micBtn.addEventListener('click', () => recorder.toggle());

  const saveBtn = document.getElementById('save-task-btn');
  if (saveBtn) saveBtn.addEventListener('click', createTask);

  const discardBtn = document.getElementById('discard-btn');
  if (discardBtn) discardBtn.addEventListener('click', () => {
    hideResult();
    document.getElementById('transcript-preview')?.classList.remove('visible');
    setStatus('Press the mic to start');
  });

  requestNotifications();
});