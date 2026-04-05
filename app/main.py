# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from env.email_env import EmailTriageEnv, EmailAction

app = FastAPI(title="Email Triage OpenEnv")

# Store one env per task
envs: dict = {}

class ResetRequest(BaseModel):
    task_id: Optional[str] = "task1"

class StepRequest(BaseModel):
    task_id: str
    labels:  dict
    actions: dict = {}
    summary: str  = ""

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
    return {
        "observation": obs.model_dump(),
        "reward":      reward.model_dump(),
        "done":        done,
        "info":        info,
    }

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
