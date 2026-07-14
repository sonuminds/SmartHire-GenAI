from src.config import client


def generate_resume_suggestions(parsed_resume, matched_jobs):
    prompt = f"""
You are an expert resume reviewer.

Candidate Resume:
{parsed_resume}

Top Matching Jobs:
{matched_jobs.to_string()}

Provide:

1. Resume strengths
2. Missing skills
3. Suggestions for improvement
4. Overall resume score out of 10

Keep the response concise and professional.
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    return response.text