ALLOWED_KEYWORDS = [
    "resume",
    "cv",
    "job",
    "career",
    "skills",
    "interview",
    "internship",
    "education",
    "experience",
    "project",
    "salary",
    "role",
    "data analyst",
    "software developer",
    "machine learning"
]


BLOCKED_KEYWORDS = [
    "hack",
    "steal",
    "password",
    "malware",
    "virus",
    "bomb",
    "weapon",
    "kill"
]


import re

def check_input(user_input):
    text = user_input.lower().strip()

    if not text:
        return False, "Please enter a question."

    # Split into actual words
    words = re.findall(r"\b\w+\b", text)

    for word in BLOCKED_KEYWORDS:
        if word in words:
            return False, "This request is unsafe and cannot be answered."

    if not any(keyword in text for keyword in ALLOWED_KEYWORDS):
        return False, "Please ask a career, resume, job, or interview-related question."

    return True, ""