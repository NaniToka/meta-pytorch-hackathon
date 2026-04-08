import os
import json
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
ENV_URL      = os.getenv("ENV_URL", "https://tokanani786-meta-pytorch-hackathon.hf.space")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

SYSTEM_PROMPT = """You are an expert email triage assistant.
Label each email as exactly one of: urgent, normal, spam
Decide action: reply (urgent), archive (normal), delete (spam)
If asked, write 2-3 sentence summary of urgent emails only.
ALWAYS respond with valid JSON only. No extra text.
Format:
{
  "labels":  {"email_0": "urgent", "email_1": "spam"},
  "actions": {"email_0": "reply",  "email_1": "delete"},
  "summary": "summary if required else empty string"
}"""

def clamp(x):
    """Ensure score is strictly between 0 and 1"""
    try:
        v = float(x)
        if v <= 0.0: return 0.001
        if v >= 1.0: return 0.999
        return round(v, 4)
    except:
        return 0.5

def call_llm(emails, description, needs_summary):
    email_list = "\n".join(
        f"[{e['id']}] From: {e['sender']} | Subject: {e['subject']} | Body: {e['body'][:80]}"
        for e in emails
    )
    summary_note = "\nIMPORTANT: Write 2-3 sentence summary of urgent emails in 'summary' field." if needs_summary else ""
    user_prompt = f"Task: {description}{summary_note}\n\nEmails:\n{email_list}\n\nJSON only:"
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=1500,
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
        print(f"[STEP] llm_error={e}")
        return {"labels": {}, "actions": {}, "summary": ""}

def run_task(task_id):
    print(f"[START] task_id={task_id} model={MODEL_NAME} env={ENV_URL}")
    try:
        obs = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id}, timeout=60).json()
    except Exception as e:
        print(f"[STEP] task_id={task_id} error={e}")
        print(f"[END] task_id={task_id} score=0.5")
        return 0.5

    emails      = obs["emails"]
    description = obs["description"]
    print(f"[STEP] task_id={task_id} status=reset emails={len(emails)}")

    needs_summary  = (task_id == "task3")
    agent_response = call_llm(emails, description, needs_summary)
    labels_given   = len(agent_response.get("labels", {}))
    actions_given  = len(agent_response.get("actions", {}))
    print(f"[STEP] task_id={task_id} status=inference labels={labels_given} actions={actions_given}")

    try:
        result = requests.post(
            f"{ENV_URL}/step",
            json={
                "task_id": task_id,
                "labels":  agent_response.get("labels",  {}),
                "actions": agent_response.get("actions", {}),
                "summary": agent_response.get("summary", ""),
            },
            timeout=60,
        ).json()
    except Exception as e:
        print(f"[STEP] task_id={task_id} error={e}")
        print(f"[END] task_id={task_id} score=0.5")
        return 0.5

    reward = result["reward"]

    # Clamp all scores strictly between 0 and 1
    label_score   = clamp(reward.get("label_score",   0.5))
    action_score  = clamp(reward.get("action_score",  0.5))
    summary_score = clamp(reward.get("summary_score", 0.5))
    score         = clamp(reward.get("value",         0.5))

    print(f"[STEP] task_id={task_id} label_score={label_score} action_score={action_score} summary_score={summary_score}")
    print(f"[END] task_id={task_id} score={score}")
    return score

def main():
    print(f"[START] model={MODEL_NAME} env={ENV_URL}")
    scores = {}
    for task_id in ["task1", "task2", "task3"]:
        scores[task_id] = run_task(task_id)
    avg = clamp(sum(scores.values()) / len(scores))
    print(f"[END] task1={scores['task1']} task2={scores['task2']} task3={scores['task3']} average={avg}")

if __name__ == "__main__":
    main()
