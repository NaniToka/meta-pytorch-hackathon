---
title: Meta Pytorch Hackathon
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
port: 7860
---

# 📧 Email Triage OpenEnv

> A real-world reinforcement learning environment where AI agents learn to manage inboxes by labeling emails, deciding actions, and summarizing urgent messages.

## What this is

This project is an OpenEnv-compatible email triage environment built for the Meta PyTorch OpenEnv Hackathon.  
It simulates realistic inbox-management tasks where an AI agent must classify emails as `urgent`, `normal`, or `spam`, choose the correct action, and handle harder phishing-style cases in advanced tasks.

## Live demo

👉 **Hugging Face Space:** `https://tokanani786-meta-pytorch-hackathon.hf.space`

The live app includes:
- Interactive email labeling demo.
- Task-based evaluation across 3 difficulty levels.
- Leaderboard for submitted scores.
- API playground for testing `/reset`, `/step`, `/state`, and related endpoints.
- Per-email correctness feedback in the UI after submission.

## Tasks

The environment includes three tasks with increasing difficulty.

| Task | Difficulty | Emails | What the agent must do |
|---|---|---:|---|
| `task1` | Easy | 10 | Label each email as `urgent`, `normal`, or `spam`. |
| `task2` | Medium | 20 | Label each email and choose an action: `reply`, `archive`, or `delete`. |
| `task3` | Hard | 30 | Label emails, choose actions, and write a short summary of urgent emails; includes tricky phishing-like spam that looks urgent. |

## Reward design

The grader gives partial credit instead of binary pass/fail scoring.  
Your updated grading logic clamps results so task scores remain strictly between 0 and 1, which addresses the validator requirement that scores must not be exactly `0.0` or `1.0`.

| Task | Reward formula |
|---|---|
| `task1` | `label_score` |
| `task2` | `0.5 * label_score + 0.5 * action_score` |
| `task3` | `0.4 * label_score + 0.4 * action_score + 0.2 * summary_score` |

### Scoring behavior

- Label accuracy is computed from correct predicted labels over all emails.
- Action accuracy is computed from correct predicted actions over all emails.
- Summary quality is based on whether the urgent-email subjects are reflected in the generated summary.
- Empty-task edge cases return neutral or bounded scores instead of invalid extremes.
- Final outputs are clamped to stay strictly inside `(0, 1)`.

## Baseline behavior

The baseline performs strongly on easy and medium tasks and lower on the hardest phishing-aware task, which demonstrates meaningful difficulty progression rather than a trivial benchmark.

## Observation space

A reset returns a task-specific observation containing task metadata and the visible inbox emails.

```json
{
  "task_id": "task1",
  "task_name": "Email Labeling (Easy)",
  "description": "You have 10 emails. Label each one as urgent, normal, or spam.",
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

## Action space

The agent submits labels, optional actions, and an optional summary.

```json
{
  "task_id": "task3",
  "labels": {
    "email_0": "urgent",
    "email_1": "spam"
  },
  "actions": {
    "email_0": "reply",
    "email_1": "delete"
  },
  "summary": "Urgent items include a production issue and a security-related message."
}
```

## API reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/reset` | Start a new episode for a task. |
| `POST` | `/step` | Submit labels/actions/summary and receive reward output. |
| `GET` | `/state` | Get current environment state for a task. |
| `GET` | `/tasks` | List all available tasks. |
| `GET` | `/health` | Health check endpoint. |
| `GET` | `/leaderboard` | View top submitted scores. |
| `POST` | `/leaderboard` | Add a score entry to the leaderboard. |
| `GET` | `/stats` | Return environment statistics such as active tasks and total episodes. |

## Features

- OpenEnv-style environment with `reset`, `step`, and `state` flows.
- Three tasks with clear difficulty progression.
- Realistic email triage scenario instead of a toy environment.
- Tricky phishing-like spam examples in the hardest task.
- Partial-credit grading with per-component scores.
- Per-email feedback showing what was right or wrong after submission.
- Interactive web UI for judges and users.
- Leaderboard support.
- API playground in the demo app.
- Deterministic seeds for reproducible tasks.
- Structured inference logging using `[START]`, `[STEP]`, and `[END]` format.

## Project structure

```text
meta-pytorch-hackathon/
├── app/
│   └── main.py              # FastAPI app + web demo + leaderboard + API playground
├── env/
│   ├── data.py              # Email generation, including tricky phishing-like spam
│   ├── graders.py           # Reward logic, clamping, and per-email feedback
│   ├── tasks.py             # Task definitions and difficulty settings
│   └── email_env.py         # Core environment class and typed models
├── server/
│   └── app.py               # Multi-mode server entry point with callable main()
├── inference.py             # Baseline agent using OpenAI client style interface
├── openenv.yaml             # OpenEnv metadata/spec file
├── pyproject.toml           # Project metadata and server entry point
├── uv.lock                  # Lockfile for validator compatibility
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container build file
└── README.md                # Project documentation
```

## Quick start

```bash
git clone https://github.com/NaniToka/meta-pytorch-hackathon
cd meta-pytorch-hackathon
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

Open:

```bash
http://localhost:7860
```

## Run the baseline agent

```bash
export HF_TOKEN=your_token
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
export ENV_URL=http://localhost:7860
python inference.py
```

## Expected inference log format

```text
[START] model=meta-llama/Llama-3.1-8B-Instruct env=http://localhost:7860
[START] task_id=task1 model=meta-llama/Llama-3.1-8B-Instruct env=http://localhost:7860
[STEP] task_id=task1 status=reset emails=10
[STEP] task_id=task1 status=inference labels=10 actions=10
[STEP] task_id=task1 label_score=0.999 action_score=0.999 summary_score=0.001
[END] task_id=task1 score=0.999
```

## Why task 3 is harder

Task 3 includes deceptive phishing-like spam that uses urgent wording, fake security alerts, and misleading account/payment messages.  
This makes the environment more realistic and ensures that the hardest task is not solved perfectly by simple keyword matching.

## Demo feedback

After submission in the UI, the app can show per-email feedback such as:
- Whether the label was correct.
- Whether the action was correct.
- The true label and true action.
- The submitted label and action.

## Tech stack

- Python
- FastAPI
- Pydantic
- Uvicorn
- OpenAI-compatible client flow for inference
- Docker deployment on Hugging Face Spaces

## License

This project was created as a hackathon submission/demo environment. Add your preferred license here if you want public reuse terms.
