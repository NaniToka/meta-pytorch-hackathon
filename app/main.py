from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from env.email_env import EmailTriageEnv, EmailAction
import json, time

app = FastAPI(title="Email Triage OpenEnv")
envs: dict = {}
leaderboard: list = []

class ResetRequest(BaseModel):
    task_id: Optional[str] = "task1"

class StepRequest(BaseModel):
    task_id: str
    labels:  dict
    actions: dict = {}
    summary: str  = ""

class LeaderboardEntry(BaseModel):
    name: str
    score: float
    task_id: str

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
.nav{display:flex;justify-content:center;gap:8px;margin-top:24px;flex-wrap:wrap}
.nav-btn{padding:8px 20px;border-radius:8px;border:none;background:#1e293b;color:#94a3b8;cursor:pointer;font-size:0.9rem;font-weight:600;border:1px solid #334155;transition:all .2s}
.nav-btn.active{background:#2563eb;color:#fff;border-color:#3b82f6}
.nav-btn:hover{color:#fff;border-color:#60a5fa}
.container{max-width:1100px;margin:0 auto;padding:40px 20px}
.page{display:none}.page.active{display:block}
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
.demo-box{background:#1e293b;border:2px solid #3b82f6;border-radius:16px;padding:30px}
.task-tabs{display:flex;gap:10px;margin-bottom:24px;flex-wrap:wrap}
.tab{padding:8px 20px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#94a3b8;cursor:pointer;font-size:0.9rem;font-weight:600;transition:all .2s}
.tab.active{background:#1d4ed8;border-color:#3b82f6;color:#fff}
.email-grid{display:flex;flex-direction:column;gap:10px;margin-bottom:20px;max-height:420px;overflow-y:auto;padding-right:4px}
.email-card{background:#0f172a;border:1px solid #334155;border-radius:10px;padding:14px;display:flex;align-items:flex-start;gap:12px;transition:border-color .2s}
.email-card.correct{border-color:#22c55e}
.email-card.wrong{border-color:#ef4444}
.email-info{flex:1;min-width:0}
.email-subject{font-weight:600;font-size:0.92rem;color:#f1f5f9;margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.email-sender{font-size:0.78rem;color:#64748b}
.email-body{font-size:0.8rem;color:#94a3b8;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.controls{display:flex;flex-direction:column;gap:6px;min-width:200px}
.sel{background:#1e293b;border:1px solid #475569;color:#e2e8f0;padding:5px 8px;border-radius:6px;font-size:0.82rem;width:100%}
.summary-box{margin-bottom:18px}
.summary-box textarea{width:100%;background:#0f172a;border:1px solid #475569;color:#e2e8f0;padding:10px;border-radius:8px;font-size:0.88rem;resize:vertical;font-family:inherit}
.summary-box label{display:block;margin-bottom:6px;color:#94a3b8;font-size:0.85rem}
.btn{padding:10px 24px;border-radius:8px;border:none;font-size:0.9rem;font-weight:700;cursor:pointer;transition:all .2s}
.btn-primary{background:#2563eb;color:#fff}.btn-primary:hover{background:#1d4ed8}
.btn-primary:disabled{background:#334155;color:#64748b;cursor:not-allowed}
.btn-reset{background:#334155;color:#94a3b8;margin-left:10px}.btn-reset:hover{background:#475569;color:#fff}
.result-box{margin-top:20px;background:#0f172a;border-radius:12px;padding:20px;display:none}
.result-box.show{display:block}
.score-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #1e293b}
.score-row:last-child{border:none}
.score-label{color:#94a3b8;font-size:0.9rem}
.score-bar-wrap{width:120px;height:6px;background:#1e293b;border-radius:999px;overflow:hidden}
.score-bar-fill{height:100%;border-radius:999px;background:#3b82f6;transition:width .6s}
.final-score{font-size:2.5rem;font-weight:800;text-align:center;margin:16px 0 4px}
.loading{text-align:center;padding:20px;color:#60a5fa;display:none}
.loading.show{display:block}
.spinner{display:inline-block;width:20px;height:20px;border:3px solid #334155;border-top-color:#3b82f6;border-radius:50%;animation:spin .8s linear infinite;margin-right:8px;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}
.name-input{background:#0f172a;border:1px solid #475569;color:#e2e8f0;padding:8px 12px;border-radius:8px;font-size:0.9rem;width:200px;margin-right:10px}
.name-input:focus{outline:none;border-color:#3b82f6}

/* LEADERBOARD */
.lb-table{width:100%;border-collapse:collapse;background:#1e293b;border-radius:12px;overflow:hidden}
.lb-table th{background:#0f172a;padding:12px 16px;text-align:left;font-size:0.82rem;color:#64748b;text-transform:uppercase}
.lb-table td{padding:12px 16px;border-top:1px solid #334155;font-size:0.9rem}
.lb-table tr:hover td{background:#243447}
.rank{font-weight:800;font-size:1rem}
.r1{color:#fbbf24}.r2{color:#94a3b8}.r3{color:#b45309}
.lb-score{font-weight:700;color:#4ade80}
.lb-empty{text-align:center;padding:40px;color:#475569}

/* API PLAYGROUND */
.playground{background:#1e293b;border:1px solid #334155;border-radius:14px;padding:24px;margin-bottom:20px}
.playground h3{font-size:1rem;font-weight:700;margin-bottom:14px;color:#60a5fa}
.play-row{display:flex;gap:10px;margin-bottom:12px;align-items:center;flex-wrap:wrap}
.play-label{color:#94a3b8;font-size:0.85rem;min-width:80px}
.play-select{background:#0f172a;border:1px solid #475569;color:#e2e8f0;padding:7px 12px;border-radius:6px;font-size:0.88rem}
.play-btn{padding:8px 18px;border-radius:6px;border:none;background:#2563eb;color:#fff;font-weight:600;cursor:pointer;font-size:0.88rem}
.play-btn:hover{background:#1d4ed8}
.play-response{background:#0f172a;border-radius:8px;padding:14px;font-family:monospace;font-size:0.78rem;color:#86efac;white-space:pre-wrap;max-height:200px;overflow-y:auto;border:1px solid #1e293b;margin-top:10px}
.method-badge{padding:3px 8px;border-radius:6px;font-size:0.78rem;font-weight:700;font-family:monospace}
.get{background:#166534;color:#86efac}.post{background:#1e40af;color:#93c5fd}

/* API TABLE */
.api-table{width:100%;border-collapse:collapse;background:#1e293b;border-radius:12px;overflow:hidden}
.api-table th{background:#0f172a;padding:11px 16px;text-align:left;font-size:0.82rem;color:#64748b;text-transform:uppercase}
.api-table td{padding:11px 16px;border-top:1px solid #334155;font-size:0.88rem}
code{background:#0f172a;padding:2px 8px;border-radius:6px;font-family:monospace;font-size:0.83rem;color:#60a5fa}
.reward-box{background:#1e293b;border:1px solid #334155;border-radius:14px;padding:24px}
.rrow{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #334155}
.rrow:last-child{border:none}
.footer{text-align:center;padding:36px;color:#475569;font-size:0.88rem;border-top:1px solid #1e293b;margin-top:20px}
@media(max-width:700px){.grid3{grid-template-columns:1fr}.controls{min-width:120px}.hero h1{font-size:1.8rem}}
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
  <div class="nav">
    <button class="nav-btn active" onclick="showPage('demo')">🎮 Live Demo</button>
    <button class="nav-btn" onclick="showPage('leaderboard')">🏆 Leaderboard</button>
    <button class="nav-btn" onclick="showPage('playground')">⚡ API Playground</button>
    <button class="nav-btn" onclick="showPage('about')">📖 About</button>
  </div>
</div>

<div class="container">

<!-- DEMO PAGE -->
<div id="page-demo" class="page active">
  <div class="section">
    <h2>🎮 Try It Yourself — Label Emails Like an AI Agent!</h2>
    <div class="demo-box">
      <div class="task-tabs">
        <button class="tab active" onclick="selectTask('task1')">📧 Easy — 10 emails</button>
        <button class="tab" onclick="selectTask('task2')">📬 Medium — 20 emails</button>
        <button class="tab" onclick="selectTask('task3')">📮 Hard — 30 emails</button>
      </div>
      <div id="demo-loading" class="loading"><span class="spinner"></span> Loading emails...</div>
      <div id="email-list" class="email-grid"></div>
      <div id="summary-section" class="summary-box" style="display:none">
        <label>📝 Write a summary of urgent emails:</label>
        <textarea id="summary-input" rows="3" placeholder="Summarize the urgent emails here..."></textarea>
      </div>
      <div style="display:flex;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:10px">
        <input class="name-input" id="player-name" type="text" placeholder="Your name (for leaderboard)"/>
        <button class="btn btn-primary" id="submit-btn" onclick="submitAnswers()" disabled>Submit Answers</button>
        <button class="btn btn-reset" onclick="selectTask(currentTask)">🔄 Reset</button>
        <span id="progress-text" style="color:#64748b;font-size:0.85rem"></span>
      </div>
      <div id="submit-loading" class="loading"><span class="spinner"></span> Scoring...</div>
      <div id="result-box" class="result-box">
        <div style="font-size:1.1rem;font-weight:700;margin-bottom:14px">📊 Your Results</div>
        <div class="score-row">
          <span class="score-label">Label accuracy</span>
          <div style="display:flex;align-items:center;gap:12px">
            <div class="score-bar-wrap"><div class="score-bar-fill" id="bar-label"></div></div>
            <span id="val-label" style="font-weight:700">-</span>
          </div>
        </div>
        <div class="score-row" id="action-row">
          <span class="score-label">Action accuracy</span>
          <div style="display:flex;align-items:center;gap:12px">
            <div class="score-bar-wrap"><div class="score-bar-fill" id="bar-action"></div></div>
            <span id="val-action" style="font-weight:700">-</span>
          </div>
        </div>
        <div class="score-row" id="summary-row">
          <span class="score-label">Summary quality</span>
          <div style="display:flex;align-items:center;gap:12px">
            <div class="score-bar-wrap"><div class="score-bar-fill" id="bar-summary"></div></div>
            <span id="val-summary" style="font-weight:700">-</span>
          </div>
        </div>
        <div class="final-score" id="final-score">-</div>
        <div style="text-align:center;color:#94a3b8;font-size:0.88rem;margin-bottom:12px">Final Score (0.0 – 1.0)</div>
        <div style="text-align:center">
          <button class="btn btn-primary" onclick="showPage('leaderboard')">🏆 View Leaderboard</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- LEADERBOARD PAGE -->
<div id="page-leaderboard" class="page">
  <div class="section">
    <h2>🏆 Leaderboard — Top Scores</h2>
    <div style="display:flex;gap:10px;margin-bottom:18px;flex-wrap:wrap">
      <button class="tab active" id="lb-tab-all" onclick="filterLB('all')">All Tasks</button>
      <button class="tab" id="lb-tab-task1" onclick="filterLB('task1')">Task 1 — Easy</button>
      <button class="tab" id="lb-tab-task2" onclick="filterLB('task2')">Task 2 — Medium</button>
      <button class="tab" id="lb-tab-task3" onclick="filterLB('task3')">Task 3 — Hard</button>
    </div>
    <table class="lb-table">
      <thead><tr><th>Rank</th><th>Name</th><th>Task</th><th>Score</th><th>Time</th></tr></thead>
      <tbody id="lb-body"></tbody>
    </table>
  </div>
</div>

<!-- API PLAYGROUND PAGE -->
<div id="page-playground" class="page">
  <div class="section">
    <h2>⚡ API Playground — Test Endpoints Live</h2>

    <div class="playground">
      <h3><span class="method-badge get">GET</span> /health — Check if server is running</h3>
      <button class="play-btn" onclick="playHealth()">Send Request</button>
      <div id="res-health" class="play-response" style="display:none"></div>
    </div>

    <div class="playground">
      <h3><span class="method-badge get">GET</span> /tasks — List all tasks</h3>
      <button class="play-btn" onclick="playTasks()">Send Request</button>
      <div id="res-tasks" class="play-response" style="display:none"></div>
    </div>

    <div class="playground">
      <h3><span class="method-badge post">POST</span> /reset — Start new episode</h3>
      <div class="play-row">
        <span class="play-label">task_id</span>
        <select class="play-select" id="play-reset-task">
          <option value="task1">task1 (Easy)</option>
          <option value="task2">task2 (Medium)</option>
          <option value="task3">task3 (Hard)</option>
        </select>
      </div>
      <button class="play-btn" onclick="playReset()">Send Request</button>
      <div id="res-reset" class="play-response" style="display:none"></div>
    </div>

    <div class="playground">
      <h3><span class="method-badge get">GET</span> /state — Current environment state</h3>
      <div class="play-row">
        <span class="play-label">task_id</span>
        <select class="play-select" id="play-state-task">
          <option value="task1">task1</option>
          <option value="task2">task2</option>
          <option value="task3">task3</option>
        </select>
      </div>
      <button class="play-btn" onclick="playState()">Send Request</button>
      <div id="res-state" class="play-response" style="display:none"></div>
    </div>

  </div>
</div>

<!-- ABOUT PAGE -->
<div id="page-about" class="page">
  <div class="section">
    <h2>Tasks</h2>
    <div class="grid3">
      <div class="card"><span class="diff easy">Easy</span><h3>Task 1 — Email Labeling</h3><div class="score sg">1.0</div><p>Label 10 emails as <code>urgent</code>, <code>normal</code>, or <code>spam</code>.</p></div>
      <div class="card"><span class="diff medium">Medium</span><h3>Task 2 — Email Triage</h3><div class="score sg">1.0</div><p>Label 20 emails AND decide: <code>reply</code>, <code>archive</code>, or <code>delete</code>.</p></div>
      <div class="card"><span class="diff hard">Hard</span><h3>Task 3 — Full Inbox</h3><div class="score sb">0.89</div><p>Label 30 emails, decide actions, AND write an urgent summary.</p></div>
    </div>
  </div>
  <div class="section">
    <h2>Reward Function</h2>
    <div class="reward-box">
      <div class="rrow"><span>Task 1 — Label accuracy only</span><span style="color:#60a5fa;font-weight:700">100% labels</span></div>
      <div class="rrow"><span>Task 2 — Labels + Actions</span><span style="color:#60a5fa;font-weight:700">50% labels + 50% actions</span></div>
      <div class="rrow"><span>Task 3 — Labels + Actions + Summary</span><span style="color:#60a5fa;font-weight:700">40% + 40% + 20%</span></div>
      <div class="rrow"><span style="color:#4ade80;font-weight:600">✓ Partial credit on every email</span><span style="color:#4ade80;font-weight:600">Never binary win/loss</span></div>
    </div>
  </div>
  <div class="section">
    <h2>API Endpoints</h2>
    <table class="api-table">
      <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
      <tr><td><span class="method-badge post">POST</span></td><td><code>/reset</code></td><td>Start new episode</td></tr>
      <tr><td><span class="method-badge post">POST</span></td><td><code>/step</code></td><td>Submit answers — get reward</td></tr>
      <tr><td><span class="method-badge get">GET</span></td><td><code>/state</code></td><td>Current state</td></tr>
      <tr><td><span class="method-badge get">GET</span></td><td><code>/tasks</code></td><td>List all tasks</td></tr>
      <tr><td><span class="method-badge get">GET</span></td><td><code>/health</code></td><td>Health check</td></tr>
    </table>
  </div>
</div>

</div>
<div class="footer">Built for Meta PyTorch OpenEnv Hackathon · Email Triage Environment · FastAPI · Docker</div>

<script>
let currentTask='task1',emails=[],userLabels={},userActions={},lbData=[],lbFilter='all';
const LABEL_OPTIONS=['urgent','normal','spam'];
const ACTION_OPTIONS=['reply','archive','delete'];

function showPage(p){
  document.querySelectorAll('.page').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(x=>x.classList.remove('active'));
  document.getElementById('page-'+p).classList.add('active');
  event.target.classList.add('active');
  if(p==='leaderboard') renderLB();
}

async function selectTask(taskId){
  currentTask=taskId; userLabels={}; userActions={};
  document.getElementById('summary-input').value='';
  document.getElementById('result-box').classList.remove('show');
  document.getElementById('submit-btn').disabled=true;
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active',['task1','task2','task3'][i]===taskId));
  document.getElementById('summary-section').style.display=taskId==='task3'?'block':'none';
  document.getElementById('action-row').style.display=taskId==='task1'?'none':'flex';
  document.getElementById('summary-row').style.display=taskId==='task3'?'flex':'none';
  document.getElementById('demo-loading').classList.add('show');
  document.getElementById('email-list').innerHTML='';
  try{
    const res=await fetch('/reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task_id:taskId})});
    const data=await res.json(); emails=data.emails; renderEmails();
  }catch(e){document.getElementById('email-list').innerHTML='<p style="color:#f87171">Error loading. Refresh page.</p>';}
  document.getElementById('demo-loading').classList.remove('show');
}

function renderEmails(){
  const c=document.getElementById('email-list'); c.innerHTML='';
  emails.forEach(email=>{
    const d=document.createElement('div'); d.className='email-card'; d.id='card-'+email.id;
    d.innerHTML=`<div class="email-info">
      <div class="email-subject">${email.subject}</div>
      <div class="email-sender">From: ${email.sender}</div>
      <div class="email-body">${email.body}</div>
    </div>
    <div class="controls">
      <select class="sel" id="label-${email.id}" onchange="updateLabel('${email.id}')">
        <option value="">Label...</option>
        ${LABEL_OPTIONS.map(l=>`<option value="${l}">${l}</option>`).join('')}
      </select>
      ${currentTask!=='task1'?`<select class="sel" id="action-${email.id}" onchange="updateAction('${email.id}')">
        <option value="">Action...</option>
        ${ACTION_OPTIONS.map(a=>`<option value="${a}">${a}</option>`).join('')}
      </select>`:''}
    </div>`;
    c.appendChild(d);
  });
  updateProgress();
}

function updateLabel(id){
  const val=document.getElementById('label-'+id).value;
  if(val){userLabels[id]=val;
    if(currentTask!=='task1'){
      const m={urgent:'reply',normal:'archive',spam:'delete'};
      const s=document.getElementById('action-'+id);
      if(s&&!userActions[id]){s.value=m[val];userActions[id]=m[val];}
    }
  }else delete userLabels[id];
  updateProgress();
}

function updateAction(id){
  const val=document.getElementById('action-'+id).value;
  if(val)userActions[id]=val; else delete userActions[id];
  updateProgress();
}

function updateProgress(){
  const total=emails.length,labeled=Object.keys(userLabels).length;
  const actioned=Object.keys(userActions).length;
  const ready=currentTask==='task1'?labeled===total:labeled===total&&actioned===total;
  document.getElementById('progress-text').textContent=currentTask==='task1'?`${labeled}/${total} labeled`:`${labeled}/${total} labeled · ${actioned}/${total} actioned`;
  document.getElementById('submit-btn').disabled=!ready;
}

async function submitAnswers(){
  document.getElementById('submit-loading').classList.add('show');
  document.getElementById('result-box').classList.remove('show');
  document.getElementById('submit-btn').disabled=true;
  try{
    const res=await fetch('/step',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({task_id:currentTask,labels:userLabels,actions:userActions,summary:document.getElementById('summary-input').value})});
    const data=await res.json(); const r=data.reward;
    const pct=v=>Math.round(v*100)+'%';
    const col=v=>v>=0.8?'#4ade80':v>=0.5?'#facc15':'#f87171';
    document.getElementById('bar-label').style.width=pct(r.label_score);
    document.getElementById('val-label').textContent=pct(r.label_score);
    document.getElementById('val-label').style.color=col(r.label_score);
    document.getElementById('bar-action').style.width=pct(r.action_score);
    document.getElementById('val-action').textContent=pct(r.action_score);
    document.getElementById('val-action').style.color=col(r.action_score);
    document.getElementById('bar-summary').style.width=pct(r.summary_score);
    document.getElementById('val-summary').textContent=pct(r.summary_score);
    document.getElementById('val-summary').style.color=col(r.summary_score);
    const fs=document.getElementById('final-score');
    fs.textContent=r.value.toFixed(2); fs.style.color=col(r.value);
    document.getElementById('result-box').classList.add('show');

    // Save to leaderboard
    const name=document.getElementById('player-name').value||'Anonymous';
    const entry={name,score:r.value,task_id:currentTask,time:new Date().toLocaleTimeString()};
    await fetch('/leaderboard',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(entry)});
    lbData.push(entry); lbData.sort((a,b)=>b.score-a.score);
  }catch(e){alert('Error. Try again.');}
  document.getElementById('submit-loading').classList.remove('show');
  document.getElementById('submit-btn').disabled=false;
}

function filterLB(f){
  lbFilter=f;
  document.querySelectorAll('[id^="lb-tab-"]').forEach(t=>t.classList.remove('active'));
  document.getElementById('lb-tab-'+f).classList.add('active');
  renderLB();
}

async function renderLB(){
  try{
    const res=await fetch('/leaderboard'); const data=await res.json();
    lbData=data.entries||[];
  }catch(e){}
  const filtered=lbFilter==='all'?lbData:lbData.filter(e=>e.task_id===lbFilter);
  const tbody=document.getElementById('lb-body');
  if(!filtered.length){tbody.innerHTML='<tr><td colspan="5" class="lb-empty">No scores yet. Be the first! 🎯</td></tr>';return;}
  const rankClass=['r1','r2','r3'];
  tbody.innerHTML=filtered.map((e,i)=>`<tr>
    <td class="rank ${rankClass[i]||''}">${i===0?'🥇':i===1?'🥈':i===2?'🥉':i+1}</td>
    <td>${e.name}</td>
    <td><span class="diff ${e.task_id==='task1'?'easy':e.task_id==='task2'?'medium':'hard'}">${e.task_id}</span></td>
    <td class="lb-score">${(e.score*100).toFixed(0)}%</td>
    <td style="color:#64748b;font-size:0.82rem">${e.time||'-'}</td>
  </tr>`).join('');
}

async function playHealth(){
  const res=await fetch('/health'); const d=await res.json();
  show('res-health',JSON.stringify(d,null,2));
}
async function playTasks(){
  const res=await fetch('/tasks'); const d=await res.json();
  show('res-tasks',JSON.stringify(d,null,2));
}
async function playReset(){
  const t=document.getElementById('play-reset-task').value;
  const res=await fetch('/reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task_id:t})});
  const d=await res.json();
  const preview={...d,emails:d.emails.slice(0,2).concat([{note:`...and ${d.emails.length-2} more emails`}])};
  show('res-reset',JSON.stringify(preview,null,2));
}
async function playState(){
  const t=document.getElementById('play-state-task').value;
  const res=await fetch('/state?task_id='+t); const d=await res.json();
  show('res-state',JSON.stringify(d,null,2));
}
function show(id,text){const el=document.getElementById(id);el.style.display='block';el.textContent=text;}

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

@app.post("/leaderboard")
def add_leaderboard(entry: LeaderboardEntry):
    leaderboard.append({"name": entry.name, "score": entry.score, "task_id": entry.task_id, "time": time.strftime("%H:%M:%S")})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return {"status": "ok"}

@app.get("/leaderboard")
def get_leaderboard():
    return {"entries": leaderboard[:20]}

@app.get("/stats")
def stats():
    """Returns environment statistics for monitoring"""
    return {
        "total_episodes": len(envs),
        "active_tasks": list(envs.keys()),
        "tasks_available": 3,
        "score_range": "0.0 - 1.0",
        "environment": "email-triage-openenv",
        "version": "1.0.0",
    }
