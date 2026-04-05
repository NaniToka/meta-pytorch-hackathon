"""
inference.py — Baseline agent for Email Triage OpenEnv
Mandatory hackathon submission file.
"""
import os
import json
import requests
from openai import OpenAI

# ── Config (read from environment variables) ──────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")
MODEL_NAME   = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3.1-8B-Instruct")
ENV_URL      = os.getenv("ENV_URL", "http://localhost:7860")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

# ── System prompt for the AI agent ───────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert email triage assistant.

Given a list of emails, you must:
1. Label each email as exactly one of: urgent, normal, spam
2. Decide an action for each email: reply (for urgent), archive (for normal), delete (for spam)
3. If asked, write a short 2-3 sentence summary of the urgent emails only.

Rules:
- urgent = needs immediate attention, from real colleagues or systems
- normal = regular work email, no rush
- spam   = promotional, scam, or irrelevant

ALWAYS respond with valid JSON only. No extra text, no markdown, no explanation.

Format:
{
  "labels":  {"email_0": "urgent", "email_1": "spam", "email_2": "normal"},
  "actions": {"email_0": "reply",  "email_1": "delete", "email_2": "archive"},
  "summary": "Write summary here if required, otherwise leave empty string"
}"""

# ── Helper: call the LLM ─────────────────────────────────────────────────────
def call_llm(emails: list, task_description: str, needs_summary: bool) -> dict:
    email_list = "\n".join(
        f"[{e['id']}] From: {e['sender']} | Subject: {e['subject']} | Body: {e['body'][:80]}"
        for e in emails
    )

    summary_note = ""
    if needs_summary:
        summary_note = "\nIMPORTANT: Also write a 2-3 sentence summary of urgent emails in the 'summary' field."

    user_prompt = f"""Task: {task_description}{summary_note}

Emails to process:
{email_list}

Respond with JSON only."""

    try:
        completion = client.chat.completions.create(
            model       = MODEL_NAME,
            messages    = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature = 0.1,
            max_tokens  = 1500,
        )
        raw = completion.choices[0].message.content or "{}"
        # Strip markdown fences if model adds them
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip().rstrip("```").strip()
        return json.loads(raw)

    except Exception as e:
        print(f"  LLM error: {e}")
        return {"labels": {}, "actions": {}, "summary": ""}

# ── Run one task ──────────────────────────────────────────────────────────────
def run_task(task_id: str) -> float:
    print(f"\n{'='*55}")
    print(f"  Running {task_id}...")
    print(f"{'='*55}")

    # 1. Reset environment
    try:
        reset_resp = requests.post(
            f"{ENV_URL}/reset",
            json={"task_id": task_id},
            timeout=30,
        )
        obs = reset_resp.json()
    except Exception as e:
        print(f"  ERROR calling /reset: {e}")
        return 0.0

    emails      = obs["emails"]
    description = obs["description"]
    task_name   = obs["task_name"]

    print(f"  Task: {task_name}")
    print(f"  Emails: {len(emails)}")

    # 2. Call LLM
    needs_summary = (task_id == "task3")
    agent_response = call_llm(emails, description, needs_summary)

    labels_given  = len(agent_response.get("labels",  {}))
    actions_given = len(agent_response.get("actions", {}))
    print(f"  Agent labeled:  {labels_given} emails")
    print(f"  Agent actioned: {actions_given} emails")

    # 3. Submit to environment
    try:
        step_resp = requests.post(
            f"{ENV_URL}/step",
            json={
                "task_id": task_id,
                "labels":  agent_response.get("labels",  {}),
                "actions": agent_response.get("actions", {}),
                "summary": agent_response.get("summary", ""),
            },
            timeout=30,
        )
        result = step_resp.json()
    except Exception as e:
        print(f"  ERROR calling /step: {e}")
        return 0.0

    reward = result["reward"]
    print(f"\n  Label score:   {reward['label_score']}")
    print(f"  Action score:  {reward['action_score']}")
    print(f"  Summary score: {reward['summary_score']}")
    print(f"  FINAL SCORE:   {reward['value']}")

    return reward["value"]

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*55)
    print("  Email Triage OpenEnv — Baseline Inference")
    print("="*55)
    print(f"  Model:   {MODEL_NAME}")
    print(f"  Env URL: {ENV_URL}")

    scores = {}
    for task_id in ["task1", "task2", "task3"]:
        scores[task_id] = run_task(task_id)

    print(f"\n{'='*55}")
    print("  FINAL RESULTS")
    print(f"{'='*55}")
    for task_id, score in scores.items():
        bar = "█" * int(score * 20)
        print(f"  {task_id}: {score:.4f}  |{bar:<20}|")
    avg = sum(scores.values()) / len(scores)
    print(f"\n  Average score: {avg:.4f}")
    print("="*55 + "\n")

if __name__ == "__main__":
    main()
