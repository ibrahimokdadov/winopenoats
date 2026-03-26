TEMPLATES: list[tuple[str, str]] = [
    (
        "Generic",
        "Summarize this meeting as structured notes with key decisions, action items, and topics discussed.",
    ),
    (
        "1:1",
        (
            "Summarize this 1:1 meeting as structured notes. Include: discussion topics, "
            "feedback given and received, agreed action items with owners, and any follow-ups."
        ),
    ),
    (
        "Customer Discovery",
        (
            "Summarize this customer discovery call. Include: customer pain points, "
            "job-to-be-done, memorable quotes, product signals, and next steps."
        ),
    ),
    (
        "Hiring Interview",
        (
            "Summarize this hiring interview. Include: candidate strengths, concerns, "
            "notes by interview topic, and a hiring recommendation with rationale."
        ),
    ),
    (
        "Stand-Up",
        (
            "Summarize this stand-up meeting. For each person capture: what they did, "
            "what they plan to do, and any blockers. List any cross-team action items."
        ),
    ),
    (
        "Weekly Meeting",
        (
            "Summarize this weekly team meeting. Include: agenda items covered, "
            "key decisions, action items with owners and due dates, and open questions."
        ),
    ),
]

TEMPLATE_NAMES = [name for name, _ in TEMPLATES]


def get_prompt(template_name: str) -> str:
    for name, prompt in TEMPLATES:
        if name == template_name:
            return prompt
    return TEMPLATES[0][1]
