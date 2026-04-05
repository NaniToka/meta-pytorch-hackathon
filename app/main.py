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
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .hero { background: linear-gradient(135deg, #1e3a5f 0%, #1e1b4b 100%); padding: 60px 40px; text-align: center; border-bottom: 1px solid #334155; }
        .hero h1 { font-size: 3rem; font-weight: 800; color: #fff; margin-bottom: 12px; }
        .hero h1 span { color: #60a5fa; }
        .hero p { font-size: 1.2rem; color: #94a3b8; max-width: 600px; margin: 0 auto 30px; }
        .badges { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
        .badge { padding: 6px 16px; border-radius: 999px; font-size: 0.85rem; font-weight: 600; }
        .badge-blue { background: #1d4ed8; color: #bfdbfe; }
        .badge-green { background: #15803d; color: #bbf7d0; }
        .badge-purple { background: #6d28d9; color: #ddd6fe; }
        .container { max-width: 1100px; margin: 0 auto; padding: 40px 20px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 28px; }
        .card h3 { font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; }
        .card p { color: #94a3b8; font-size: 0.9rem; line-height: 1.6; }
        .card .score { font-size: 2.5rem; font-weight: 800; margin: 12px 0; }
        .score-green { color: #4ade80; }
        .score-blue { color: #60a5fa; }
        .difficulty { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; margin-bottom: 10px; }
        .easy { background: #166534; color: #86efac; }
        .medium { background: #92400e; color: #fde68a; }
        .hard { background: #991b1b; color: #fca5a5; }
        .section { margin-bottom: 40px; }
        .section h2 { font-size: 1.5rem; font-weight: 700; margin-bottom: 20px; color: #f1f5f9; border-left: 4px solid #3b82f6; padding-left: 12px; }
        .api-table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; }
        .api-table th { background: #0f172a; padding: 12px 16px; text-align: left; font-size: 0.85rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
        .api-table td { padding: 12px 16px; border-top: 1px solid #334155; font-size: 0.9rem; }
        .method { padding: 3px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; font-family: monospace; }
        .get { background: #166534; color: #86efac; }
        .post { background: #1e40af; color: #93c5fd; }
        code { background: #0f172a; padding: 2px 8px; border-radius: 6px; font-family: monospace; font-size: 0.85rem; color: #60a5fa; }
        .reward-box { background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 28px; }
        .reward-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #334155; }
        .reward-row:last-child { border-bottom: none; }
        .bar { height: 8px; border-radius: 999px; background: #3b82f6; }
        .footer { text-align: center; padding: 40px; color: #475569; font-size: 0.9rem; border-top: 1px solid #1e293b; }
        .status { display: inline-flex; align-items: center; gap: 8px; background: #14532d; color: #86efac; padding: 8px 20px; border-radius: 999px; font-weight: 600; }
        .dot { width: 8px; height: 8px; background: #4ade80; border-radius: 50%; animation: pulse 2s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
    </style>
</head>
<body>
<div class="hero">
    <h1>📧 Email Triage <span>OpenEnv</span></h1>
    <p>A real-world reinforcement learning environment where AI agents learn to manage email inboxes — labeling, triaging, and summarizing with precision.</p>
    <div class="badges">
        <span class="badge badge-blue">OpenEnv Compliant</span>
        <span class="badge badge-green">3 Tasks</span>
        <span class="badge badge-purple">Avg Score: 0.94</span>
    </div>
    <br>
    <div class="status"><div class="dot"></div> Live & Running</div>
</div>

<div class="container">

    <div class="section">
        <h2>Tasks</h2>
        <div class="grid">
            <div class="card">
                <span class="difficulty easy">Easy</span>
                <h3>Task 1 — Email Labeling</h3>
                <div class="score score-green">1.0</div>
                <p>Label 10 emails as <code>urgent</code>, <code>normal</code>, or <code>spam</code>. Pure classification challenge.</p>
            </div>
            <div class="card">
                <span class="difficulty medium">Medium</span>
                <h3>Task 2 — Email Triage</h3>
                <div class="score score-green">1.0</div>
                <p>Label 20 emails AND decide the action: <code>reply</code>, <code>archive</code>, or <code>delete</code>.</p>
            </div>
            <div class="card">
                <span class="difficulty hard">Hard</span>
                <h3>Task 3 — Full Inbox</h3>
                <div class="score score-blue">0.82</div>
                <p>Label 30 emails, decide actions, AND write a summary of all urgent items.</p>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Reward Function</h2>
        <div class="reward-box">
            <div class="reward-row">
                <span>Task 1 — Label accuracy only</span>
                <span style="color:#60a5fa;font-weight:700">100% labels</span>
            </div>
            <div class="reward-row">
                <span>Task 2 — Labels + Actions</span>
                <span style="color:#60a5fa;font-weight:700">50% labels + 50% actions</span>
            </div>
            <div class="reward-row">
                <span>Task 3 — Labels + Actions + Summary</span>
                <span style="color:#60a5fa;font-weight:700">40% + 40% + 20%</span>
            </div>
            <div class="reward-row">
                <span style="color:#4ade80;font-weight:600">✓ Partial credit on every email</span>
                <span style="color:#4ade80;font-weight:600">Never binary win/loss</span>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>API Endpoints</h2>
        <table class="api-table">
            <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
            <tr><td><span class="method post">POST</span></td><td><code>/reset</code></td><td>Start new episode — returns inbox emails</td></tr>
            <tr><td><span class="method post">POST</span></td><td><code>/step</code></td><td>Submit labels, actions, summary — returns reward</td></tr>
            <tr><td><span class="method get">GET</span></td><td><code>/state</code></td><td>Get current environment state</td></tr>
            <tr><td><span class="method get">GET</span></td><td><code>/tasks</code></td><td>List all 3 tasks with metadata</td></tr>
            <tr><td><span class="method get">GET</span></td><td><code>/health</code></td><td>Health check — returns status ok</td></tr>
        </table>
    </div>

</div>
<div class="footer">Built for Meta PyTorch OpenEnv Hackathon · Email Triage Environment · Python 97% · Docker</div>
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
