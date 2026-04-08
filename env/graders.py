def _clamp(x):
    if x <= 0.0:
        return 0.001
    if x >= 1.0:
        return 0.999
    return round(x, 4)

def grade_labels(emails, agent_labels):
    if not emails:
        return 0.5
    correct = sum(1 for e in emails if agent_labels.get(e["id"],"").strip().lower()==e["true_label"])
    return _clamp(correct/len(emails))

def grade_actions(emails, agent_actions):
    if not emails:
        return 0.5
    correct = sum(1 for e in emails if agent_actions.get(e["id"],"").strip().lower()==e["true_action"])
    return _clamp(correct/len(emails))

def grade_summary(emails, agent_summary):
    urgent = [e for e in emails if e["true_label"]=="urgent"]
    if not urgent:
        return 0.999
    if not agent_summary or not agent_summary.strip():
        return 0.001
    s = agent_summary.lower()
    hits = sum(1 for e in urgent if any(w in s for w in e["subject"].lower().split() if len(w)>3))
    return _clamp(hits/len(urgent))

def get_per_email_feedback(emails, agent_labels, agent_actions):
    feedback = []
    for e in emails:
        al = agent_labels.get(e["id"],"").strip().lower()
        aa = agent_actions.get(e["id"],"").strip().lower()
        feedback.append({"id":e["id"],"label_correct":al==e["true_label"],"action_correct":aa==e["true_action"],"true_label":e["true_label"],"true_action":e["true_action"],"your_label":al,"your_action":aa})
    return feedback

def compute_reward(task_id, emails, agent_response):
    labels  = agent_response.get("labels",{})
    actions = agent_response.get("actions",{})
    summary = agent_response.get("summary","")
    ls = grade_labels(emails, labels)
    as_ = grade_actions(emails, actions)
    ss = grade_summary(emails, summary)
    fb = get_per_email_feedback(emails, labels, actions)
    if task_id=="task1":
        final = ls
    elif task_id=="task2":
        final = 0.5*ls + 0.5*as_
    elif task_id=="task3":
        final = 0.4*ls + 0.4*as_ + 0.2*ss
    else:
        final = 0.5
    return {"value":_clamp(final),"label_score":ls,"action_score":as_,"summary_score":ss,"feedback":fb}
