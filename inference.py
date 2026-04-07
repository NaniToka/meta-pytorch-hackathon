
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
MODEL_NAME   = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
ENV_URL      = os.getenv("ENV_URL", "http://localhost:7860")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


def _clamp(x: float) -> float:
    """Clamp any score strictly inside (0,1) and round to 4 decimals."""
    return round(min(max(x, 0.001), 0.999), 4)


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
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip().rstrip("```").strip()
        return json.loads(raw)

    except Exception as e:
        print(f"[STEP] task_id=error status=llm_error detail={e}")
        return {"labels": {}, "actions": {}, "summary": ""}


# ── Run one task ──────────────────────────────────────────────────────────────
def run_task(task_id: str) -> float:
    print(f"[START] task_id={task_id} model={MODEL_NAME} env={ENV_URL}")

    # 1. Reset environment
    try:
        reset_resp = requests.post(
            f"{ENV_URL}/reset",
            json={"task_id": task_id},
            timeout=30,
        )
        obs = reset_resp.json()
    except Exception as e:
        print(f"[STEP] task_id={task_id} status=reset_error detail={e}")
        print(f"[END] task_id={task_id} score=0.0010")
        return 0.001

    emails      = obs["emails"]
    description = obs["description"]

    print(f"[STEP] task_id={task_id} status=reset emails={len(emails)}")

    # 2. Call LLM
    needs_summary = (task_id == "task3")
    agent_response = call_llm(emails, description, needs_summary)

    labels_given  = len(agent_response.get("labels",  {}))
    actions_given = len(agent_response.get("actions", {}))
    print(f"[STEP] task_id={task_id} status=inference labels={labels_given} actions={actions_given}")

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
        print(f"[STEP] task_id={task_id} status=step_error detail={e}")
        print(f"[END] task_id={task_id} score=0.0010")
        return 0.001

    reward = result["reward"]

    # Clamp all scores for logging / validator
    label_score   = _clamp(reward.get("label_score", 0.0))
    action_score  = _clamp(reward.get("action_score", 0.0))
    summary_score = _clamp(reward.get("summary_score", 0.0))
    final_score   = _clamp(reward.get("value", 0.0))

    print(
        f"[STEP] task_id={task_id} "
        f"label_score={label_score} action_score={action_score} summary_score={summary_score}"
    )
    print(f"[END] task_id={task_id} score={final_score}")

    return final_score


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"[START] model={MODEL_NAME} env={ENV_URL}")

    scores = {}
    for task_id in ["task1", "task2", "task3"]:
        scores[task_id] = run_task(task_id)

    avg = sum(scores.values()) / len(scores)
    avg = _clamp(avg)

    print(
        f"[END] task1={scores['task1']:.4f} "
        f"task2={scores['task2']:.4f} task3={scores['task3']:.4f} average={avg:.4f}"
    )


if __name__ == "__main__":
    main()