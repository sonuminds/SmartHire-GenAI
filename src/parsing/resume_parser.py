import json

from src.config import client


def test_gemini():
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents="Reply with exactly these words: Gemini connection successful."
    )

    print(response.text)


def parse_resume(resume_text):
    """
    Convert extracted resume text into structured resume information.
    """

    prompt = f"""
You are an expert resume parser.

Read the following resume and extract its information.

Return ONLY valid JSON. Do not add markdown or explanations.

Use exactly these fields:

{{
    "Name": "",
    "Email": "",
    "Phone": "",
    "Skills": [],
    "Education": [],
    "Experience": [],
    "Projects": [],
    "Certifications": [],
    "Target Role": ""
}}

If a field is unavailable, use an empty string or empty list.

Resume:
{resume_text}
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    cleaned_response = (
        response.text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(cleaned_response)