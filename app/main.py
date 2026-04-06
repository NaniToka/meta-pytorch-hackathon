from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from env.email_env import EmailTriageEnv, EmailAction

app = FastAPI(title="Email Triage OpenEnv")
envs: dict = {}

class ResetRequest(BaseModel):
    task_id: Optional[str] = "task1"

class StepRequest(BaseModel):
    task_id: str
    labels:  dict
    actions: dict = {}
    summary: str  = ""

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Email Triage OpenEnv</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
.hero{background:linear-gradient(135deg,#1e3a5f,#1e1b4b);padding:50px 40px;text-align:center;border-bottom:1px solid #334155}
.hero h1{font-size:2.8rem;font-weight:800;color:#fff;margin-bottom:10px}
.hero h1 span{color:#60a5fa}
.hero p{font-size:1.1rem;color:#94a3b8;max-width:600px;margin:0 auto 24px}
.badges{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:20px}
.badge{padding:5px 14px;border-radius:999px;font-size:0.82rem;font-weight:600}
.b-blue{background:#1d4ed8;color:#bfdbfe}
.b-green{background:#15803d;color:#bbf7d0}
.b-purple{background:#6d28d9;color:#ddd6fe}
.b-orange{background:#92400e;color:#fde68a}
.status{display:inline-flex;align-items:center;gap:8px;background:#14532d;color:#86efac;padding:7px 18px;border-radius:999px;font-weight:600;font-size:0.9rem}
.dot{width:8px;height:8px;background:#4ade80;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.container{max-width:1100px;margin:0 auto;padding:40px 20px}
.section{margin-bottom:44px}
.section h2{font-size:1.4rem;font-weight:700;margin-bottom:18px;border-left:4px solid #3b82f6;padding-left:12px;color:#f1f5f9}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:40px}
.card{background:#1e293b;border:1px solid #334155;border-radius:14px;padding:24px}
.card h3{font-size:1rem;font-weight:700;margin-bottom:6px}
.card p{color:#94a3b8;font-size:0.88rem;line-height:1.6}
.score{font-size:2.4rem;font-weight:800;margin:10px 0}
.sg{color:#4ade80}.sb{color:#60a5fa}
.diff{display:inline-block;padding:3px 10px;border-radius:999px;font-size:0.73rem;font-weight:600;margin-bottom:8px}
.easy{background:#166534;color:#86efac}
.medium{background:#92400e;color:#fde68a}
.hard{background:#991b1b;color:#fca5a5}

/* DEMO SECTION */
.demo-box{background:#1e293b;border:2px solid #3b82f6;border-radius:16px;padding:30px}
.task-tabs{display:flex;gap:10px;margin-bottom:24px;flex-wrap:wrap}
.tab{padding:8px 20px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#94a3b8;cursor:pointer;font-size:0.9rem;font-weight:600;transition:all .2s}
.tab.active{background:#1d4ed8;border-color:#3b82f6;color:#fff}
.tab:hover{border-color:#60a5fa;color:#fff}
.email-grid{display:flex;flex-direction:column;gap:10px;margin-bottom:20px;max-height:420px;overflow-y:auto;padding-right:4px}
.email-card{background:#0f172a;border:1px solid #334155;border-radius:10px;padding:14px;display:flex;align-items:flex-start;gap:12px}
.email-info{flex:1;min-width:0}
.email-subject{font-weight:600;font-size:0.92rem;color:#f1f5f9;margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.email-sender{font-size:0.78rem;color:#64748b}
.email-body{font-size:0.8rem;color:#94a3b8;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.controls{display:flex;flex-direction:column;gap:6px;min-width:200px}
.sel{background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:5px 8px;border-radius:6px;font-size:0.82rem;width:100%}
.sel:focus{outline:none;border-color:#3b82f6}
.summary-box{margin-bottom:18px}
.summary-box textarea{width:100%;background:#0f172a;border:1px solid #475569;color:#e2e8f0;padding:10px;border-radius:8px;font-size:0.88rem;resize:vertical;font-family:inherit}
.summary-box textarea:focus{outline:none;border-color:#3b82f6}
.summary-box label{display:block;margin-bottom:6px;color:#94a3b8;font-size:0.85rem}
.btn{padding:12px 28px;border-radius:8px;border:none;font-size:0.95rem;font-weight:700;cursor:pointer;transition:all .2s}
.btn-primary{background:#2563eb;color:#fff}
.btn-primary:hover{background:#1d4ed8}
.btn-primary:disabled{background:#334155;color:#64748b;cursor:not-allowed}
.btn-reset{background:#334155;color:#94a3b8;margin-left:10px}
.btn-reset:hover{background:#475569;color:#fff}
.result-box{margin-top:20px;background:#0f172a;border-radius:12px;padding:20px;display:none}
.result-box.show{display:block}
.result-title{font-size:1.1rem;font-weight:700;margin-bottom:14px;color:#f1f5f9}
.score-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #1e293b}
.score-row:last-child{border:none}
.score-label{color:#94a3b8;font-size:0.9rem}
.score-val{font-weight:700;font-size:1rem}
.score-bar-wrap{width:120px;height:6px;background:#1e293b;border-radius:999px;overflow:hidden}
.score-bar-fill{height:100%;border-radius:999px;background:#3b82f6;transition:width .6s}
.final-score{font-size:2rem;font-weight:800;text-align:center;margin:16px 0 4px}
.loading{text-align:center;padding:20px;color:#60a5fa;display:none}
.loading.show{display:block}
.spinner{display:inline-block;width:24px;height:24px;border:3px solid #334155;border-top-color:#3b82f6;border-radius:50%;animation:spin .8s linear infinite;margin-right:8px;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}

/* API TABLE */
.api-table{width:100%;border-collapse:collapse;background:#1e293b;border-radius:12px;overflow:hidden}
.api-table th{background:#0f172a;padding:11px 16px;text-align:left;font-size:0.82rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em}
.api-table td{padding:11px 16px;border-top:1px solid #334155;font-size:0.88rem}
.method{padding:3px 8px;border-radius:6px;font-size:0.78rem;font-weight:700;font-family:monospace}
.get{background:#166534;color:#86efac}.post{background:#1e40af;color:#93c5fd}
code{background:#0f172a;padding:2px 8px;border-radius:6px;font-family:monospace;font-size:0.83rem;color:#60a5fa}
.reward-box{background:#1e293b;border:1px solid #334155;border-radius:14px;padding:24px}
.rrow{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #334155}
.rrow:last-child{border:none}
.footer{text-align:center;padding:36px;color:#475569;font-size:0.88rem;border-top:1px solid #1e293b;margin-top:20px}

@media(max-width:700px){.grid3{grid-template-columns:1fr}.controls{min-width:140px}.hero h1{font-size:1.8rem}}
</style>
</head>
<body>

<div class="hero">
  <h1>📧 Email Triage <span>OpenEnv</span></h1>
  <p>A real-world reinforcement learning environment where AI agents learn to manage email inboxes.</p>
  <div class="badges">
    <span class="badge b-blue">OpenEnv Compliant</span>
    <span class="badge b-green">3 Tasks</span>
    <span class="badge b-purple">Avg Score: 0.93</span>
    <span class="badge b-orange">Meta PyTorch Hackathon</span>
  </div>
  <div class="status"><div class="dot"></div> Live &amp; Running</div>
</div>

<div class="container">

  <!-- TASKS -->
  <div class="section">
    <h2>Tasks</h2>
    <div class="grid3">
      <div class="card">
        <span class="diff easy">Easy</span>
        <h3>Task 1 — Email Labeling</h3>
        <div class="score sg">1.0</div>
        <p>Label 10 emails as <code>urgent</code>, <code>normal</code>, or <code>spam</code>.</p>
      </div>
      <div class="card">
        <span class="diff medium">Medium</span>
        <h3>Task 2 — Email Triage</h3>
        <div class="score sg">1.0</div>
        <p>Label 20 emails AND decide: <code>reply</code>, <code>archive</code>, or <code>delete</code>.</p>
      </div>
      <div class="card">
        <span class="diff hard">Hard</span>
        <h3>Task 3 — Full Inbox</h3>
        <div class="score sb">0.89</div>
        <p>Label 30 emails, decide actions, AND write an urgent summary.</p>
      </div>
    </div>
  </div>

  <!-- LIVE DEMO -->
  <div class="section">
    <h2>🎮 Live Interactive Demo — Try It Yourself!</h2>
    <div class="demo-box">
      <div class="task-tabs">
        <button class="tab active" onclick="selectTask('task1')">📧 Task 1 — Easy (10 emails)</button>
        <button class="tab" onclick="selectTask('task2')">📬 Task 2 — Medium (20 emails)</button>
        <button class="tab" onclick="selectTask('task3')">📮 Task 3 — Hard (30 emails)</button>
      </div>

      <div id="demo-loading" class="loading">
        <span class="spinner"></span> Loading emails...
      </div>

      <div id="email-list" class="email-grid"></div>

      <div id="summary-section" class="summary-box" style="display:none">
        <label>📝 Write a summary of urgent emails:</label>
        <textarea id="summary-input" rows="3" placeholder="Summarize the urgent emails here..."></textarea>
      </div>

      <div style="display:flex;align-items:center;flex-wrap:wrap;gap:10px">
        <button class="btn btn-primary" id="submit-btn" onclick="submitAnswers()" disabled>
          Submit Answers
        </button>
        <button class="btn btn-reset" onclick="selectTask(currentTask)">
          🔄 Reset
        </button>
        <span id="progress-text" style="color:#64748b;font-size:0.85rem"></span>
      </div>

      <div id="submit-loading" class="loading">
        <span class="spinner"></span> Scoring your answers...
      </div>

      <div id="result-box" class="result-box">
        <div class="result-title">📊 Your Results</div>
        <div class="score-row">
          <span class="score-label">Label accuracy</span>
          <div style="display:flex;align-items:center;gap:12px">
            <div class="score-bar-wrap"><div class="score-bar-fill" id="bar-label"></div></div>
            <span class="score-val" id="val-label">-</span>
          </div>
        </div>
        <div class="score-row" id="action-row">
          <span class="score-label">Action accuracy</span>
          <div style="display:flex;align-items:center;gap:12px">
            <div class="score-bar-wrap"><div class="score-bar-fill" id="bar-action"></div></div>
            <span class="score-val" id="val-action">-</span>
          </div>
        </div>
        <div class="score-row" id="summary-row">
          <span class="score-label">Summary quality</span>
          <div style="display:flex;align-items:center;gap:12px">
            <div class="score-bar-wrap"><div class="score-bar-fill" id="bar-summary"></div></div>
            <span class="score-val" id="val-summary">-</span>
          </div>
        </div>
        <div class="final-score" id="final-score">-</div>
        <div style="text-align:center;color:#94a3b8;font-size:0.88rem">Final Score (0.0 – 1.0)</div>
      </div>
    </div>
  </div>

  <!-- REWARD -->
  <div class="section">
    <h2>Reward Function</h2>
    <div class="reward-box">
      <div class="rrow"><span>Task 1 — Label accuracy only</span><span style="color:#60a5fa;font-weight:700">100% labels</span></div>
      <div class="rrow"><span>Task 2 — Labels + Actions</span><span style="color:#60a5fa;font-weight:700">50% labels + 50% actions</span></div>
      <div class="rrow"><span>Task 3 — Labels + Actions + Summary</span><span style="color:#60a5fa;font-weight:700">40% + 40% + 20%</span></div>
      <div class="rrow"><span style="color:#4ade80;font-weight:600">✓ Partial credit on every email</span><span style="color:#4ade80;font-weight:600">Never binary win/loss</span></div>
    </div>
  </div>

  <!-- API -->
  <div class="section">
    <h2>API Endpoints</h2>
    <table class="api-table">
      <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
      <tr><td><span class="method post">POST</span></td><td><code>/reset</code></td><td>Start new episode — returns inbox emails</td></tr>
      <tr><td><span class="method post">POST</span></td><td><code>/step</code></td><td>Submit answers — returns reward score</td></tr>
      <tr><td><span class="method get">GET</span></td><td><code>/state</code></td><td>Current environment state</td></tr>
      <tr><td><span class="method get">GET</span></td><td><code>/tasks</code></td><td>List all 3 tasks</td></tr>
      <tr><td><span class="method get">GET</span></td><td><code>/health</code></td><td>Health check</td></tr>
    </table>
  </div>

</div>

<div class="footer">Built for Meta PyTorch OpenEnv Hackathon · Email Triage Environment · Python · Docker · FastAPI</div>

<script>
let currentTask = 'task1';
let emails = [];
let userLabels = {};
let userActions = {};

const LABEL_OPTIONS = ['urgent','normal','spam'];
const ACTION_OPTIONS = ['reply','archive','delete'];

async function selectTask(taskId) {
  currentTask = taskId;
  userLabels = {};
  userActions = {};
  document.getElementById('summary-input').value = '';
  document.getElementById('result-box').classList.remove('show');
  document.getElementById('submit-btn').disabled = true;

  // Update tabs
  document.querySelectorAll('.tab').forEach((t,i) => {
    t.classList.toggle('active', ['task1','task2','task3'][i] === taskId);
  });

  // Show summary section only for task3
  document.getElementById('summary-section').style.display = taskId === 'task3' ? 'block' : 'none';
  document.getElementById('action-row').style.display = taskId === 'task1' ? 'none' : 'flex';
  document.getElementById('summary-row').style.display = taskId === 'task3' ? 'flex' : 'none';

  // Load emails
  document.getElementById('demo-loading').classList.add('show');
  document.getElementById('email-list').innerHTML = '';

  try {
    const res = await fetch('/reset', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({task_id: taskId})
    });
    const data = await res.json();
    emails = data.emails;
    renderEmails();
  } catch(e) {
    document.getElementById('email-list').innerHTML = '<p style="color:#f87171">Error loading emails. Please refresh.</p>';
  }

  document.getElementById('demo-loading').classList.remove('show');
}

function renderEmails() {
  const container = document.getElementById('email-list');
  container.innerHTML = '';

  emails.forEach(email => {
    const div = document.createElement('div');
    div.className = 'email-card';
    div.innerHTML = `
      <div class="email-info">
        <div class="email-subject">${email.subject}</div>
        <div class="email-sender">From: ${email.sender}</div>
        <div class="email-body">${email.body}</div>
      </div>
      <div class="controls">
        <select class="sel" id="label-${email.id}" onchange="updateLabel('${email.id}')">
          <option value="">Label...</option>
          ${LABEL_OPTIONS.map(l => `<option value="${l}">${l}</option>`).join('')}
        </select>
        ${currentTask !== 'task1' ? `
        <select class="sel" id="action-${email.id}" onchange="updateAction('${email.id}')">
          <option value="">Action...</option>
          ${ACTION_OPTIONS.map(a => `<option value="${a}">${a}</option>`).join('')}
        </select>` : ''}
      </div>
    `;
    container.appendChild(div);
  });

  updateProgress();
}

function updateLabel(emailId) {
  const val = document.getElementById('label-'+emailId).value;
  if (val) {
    userLabels[emailId] = val;
    // Auto-set matching action
    if (currentTask !== 'task1') {
      const actionMap = {urgent:'reply', normal:'archive', spam:'delete'};
      const actionSel = document.getElementById('action-'+emailId);
      if (actionSel && !userActions[emailId]) {
        actionSel.value = actionMap[val];
        userActions[emailId] = actionMap[val];
      }
    }
  } else {
    delete userLabels[emailId];
  }
  updateProgress();
}

function updateAction(emailId) {
  const val = document.getElementById('action-'+emailId).value;
  if (val) userActions[emailId] = val;
  else delete userActions[emailId];
  updateProgress();
}

function updateProgress() {
  const total = emails.length;
  const labeled = Object.keys(userLabels).length;
  const actioned = currentTask === 'task1' ? labeled : Object.keys(userActions).length;
  const needed = currentTask === 'task1' ? labeled : Math.min(labeled, actioned);
  const ready = currentTask === 'task1' ? labeled === total : labeled === total && actioned === total;

  document.getElementById('progress-text').textContent =
    currentTask === 'task1'
      ? `${labeled}/${total} labeled`
      : `${labeled}/${total} labeled · ${actioned}/${total} actioned`;

  document.getElementById('submit-btn').disabled = !ready;
}

async function submitAnswers() {
  document.getElementById('submit-loading').classList.add('show');
  document.getElementById('result-box').classList.remove('show');
  document.getElementById('submit-btn').disabled = true;

  try {
    const res = await fetch('/step', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        task_id: currentTask,
        labels:  userLabels,
        actions: userActions,
        summary: document.getElementById('summary-input').value
      })
    });
    const data = await res.json();
    const r = data.reward;

    // Show results
    const pct = v => Math.round(v * 100) + '%';
    const col = v => v >= 0.8 ? '#4ade80' : v >= 0.5 ? '#facc15' : '#f87171';

    document.getElementById('bar-label').style.width = pct(r.label_score);
    document.getElementById('val-label').textContent = pct(r.label_score);
    document.getElementById('val-label').style.color = col(r.label_score);

    document.getElementById('bar-action').style.width = pct(r.action_score);
    document.getElementById('val-action').textContent = pct(r.action_score);
    document.getElementById('val-action').style.color = col(r.action_score);

    document.getElementById('bar-summary').style.width = pct(r.summary_score);
    document.getElementById('val-summary').textContent = pct(r.summary_score);
    document.getElementById('val-summary').style.color = col(r.summary_score);

    const fs = document.getElementById('final-score');
    fs.textContent = r.value.toFixed(2);
    fs.style.color = col(r.value);

    document.getElementById('result-box').classList.add('show');
  } catch(e) {
    alert('Error submitting. Please try again.');
  }

  document.getElementById('submit-loading').classList.remove('show');
  document.getElementById('submit-btn').disabled = false;
}

// Load task1 on page load
selectTask('task1');
</script>
</body>
</html>
"""

@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    task_id = req.task_id or "task1"
    env = EmailTriageEnv(task_id=task_id)
    envs[task_id] = env
    obs = env.reset()
    return obs.model_dump()

@app.post("/step")
def step(req: StepRequest):
    env = envs.get(req.task_id)
    if env is None:
        env = EmailTriageEnv(task_id=req.task_id)
        env.reset()
        envs[req.task_id] = env
    action = EmailAction(
        task_id = req.task_id,
        labels  = req.labels,
        actions = req.actions,
        summary = req.summary,
    )
    obs, reward, done, info = env.step(action)
    return {"observation": obs.model_dump(), "reward": reward.model_dump(), "done": done, "info": info}

@app.get("/state")
def state(task_id: str = "task1"):
    env = envs.get(task_id)
    if env is None:
        return {"error": "No active episode. Call /reset first."}
    return env.state()

@app.get("/tasks")
def list_tasks():
    from env.tasks import TASKS
    return {"tasks": list(TASKS.values())}

@app.get("/health")
def health():
    return {"status": "ok"}
