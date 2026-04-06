---
title: Meta Pytorch Hackathon
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
port: 7860
---

# 📧 Email Triage OpenEnv

> A real-world reinforcement learning environment where AI agents learn to manage email inboxes — built for the Meta PyTorch OpenEnv Hackathon.

## 🎯 What Is This?

Every company on Earth has the same problem — too many emails, too little time. This OpenEnv environment trains AI agents to:

1. **Label** emails as `urgent`, `normal`, or `spam`
2. **Decide actions** — `reply`, `archive`, or `delete`
3. **Summarize** urgent emails for human review

## 🎮 Live Demo

👉 **[Try it yourself here](https://tokanani786-meta-pytorch-hackathon.hf.space)**

Label real emails, see your score instantly, and compete on the leaderboard!

## 📊 Baseline Scores

| Task | Difficulty | Emails | Score |
|------|-----------|--------|-------|
| task1 | 🟢 Easy | 10 | **1.0** |
| task2 | 🟡 Medium | 20 | **1.0** |
| task3 | 🔴 Hard | 30 | **0.89** |
| **Average** | | | **0.93** |

Model: `meta-llama/Llama-3.1-8B-Instruct`

## 🏗️ Environment Design

### Observation Space
```json
{
  "task_id": "task1",
  "task_name": "Email Labeling (Easy)",
  "emails": [
    {
      "id": "email_0",
      "subject": "URGENT: Server is down",
      "sender": "cto@company.com",
      "body": "This is a critical issue..."
    }
  ],
  "step": 0,
  "done": false
}
```

### Action Space
```json
{
  "task_id": "task1",
  "labels":  {"email_0": "urgent", "email_1": "spam"},
  "actions": {"email_0": "reply",  "email_1": "delete"},
  "summary": "Urgent: server down, database corrupted."
}
```

### Reward Function

| Task | Formula |
|------|---------|
| task1 | `label_accuracy` |
| task2 | `0.5 × label_accuracy + 0.5 × action_accuracy` |
| task3 | `0.4 × labels + 0.4 × actions + 0.2 × summary_quality` |

✅ **Partial credit on every email — never binary win/loss**

## 🚀 Quick Start
```bash
git clone https://github.com/NaniToka/meta-pytorch-hackathon
cd meta-pytorch-hackathon
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

## 🤖 Run Baseline Agent
```bash
export HF_TOKEN=your_token
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
export ENV_URL=https://tokanani786-meta-pytorch-hackathon.hf.space
python inference.py
```

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/reset` | Start episode |
| POST | `/step` | Submit answers and get reward |
| GET | `/state` | Current environment state |
| GET | `/tasks` | List all tasks |
| GET | `/health` | Health check |
| GET | `/leaderboard` | Top scores |

## 🗂️ Project Structure

meta-pytorch-hackathon/ 
├── env/ 
│ ├── data.py # Email dataset generator 
│ ├── graders.py # Scoring logic with partial credit
│ ├── tasks.py # 3 task definitions 
│ └── email_env.py # Main environment
├── app/ 
│ └── main.py # FastAPI server + web UI 
├── inference.py # Baseline AI agent 
├── openenv.yaml # OpenEnv spec file 
├── Dockerfile # Container config 
├── requirements.txt # Python dependencies 
└── README.md # READ This File




