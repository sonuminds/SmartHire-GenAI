import os
import sys
import tempfile
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------
# Project path setup
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Project module imports
# ---------------------------------------------------------

from src.generate.suggestions import generate_resume_suggestions
from src.mentor.rag_chain import (
    ask_mentor,
    build_notes_index,
    chunk_notes,
    embed_chunks,
    load_career_notes,
)
from src.parsing.loader import load_resume
from src.parsing.resume_parser import parse_resume
from src.safety.guardrails import check_input
from src.search.job_search import search_jobs


# ---------------------------------------------------------
# Streamlit page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="SmartHire GenAI",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Small UI styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0;
        }

        .subtitle {
            font-size: 1.05rem;
            color: #9ca3af;
            margin-top: 0.2rem;
            margin-bottom: 1.4rem;
        }

        .skill-tag {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            margin: 0.2rem;
            border-radius: 1rem;
            background-color: rgba(124, 58, 237, 0.18);
            border: 1px solid rgba(167, 139, 250, 0.45);
            font-size: 0.9rem;
        }

        .small-muted {
            color: #9ca3af;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def format_value(value, fallback="Not provided"):
    """Return a clean value for displaying extracted resume information."""

    if value is None:
        return fallback

    if isinstance(value, str) and not value.strip():
        return fallback

    return value


def render_skills(skills):
    """Display extracted skills as visual tags."""

    if not skills:
        st.info("No skills were extracted.")
        return

    skill_html = ""

    for skill in skills:
        skill_html += (
            f'<span class="skill-tag">{str(skill)}</span>'
        )

    st.markdown(skill_html, unsafe_allow_html=True)


def render_education(education_items):
    """Display education details as separate cards."""

    if not education_items:
        st.info("No education details were extracted.")
        return

    for item in education_items:
        with st.container(border=True):
            if isinstance(item, dict):
                qualification = format_value(
                    item.get("Qualification"),
                    "Education",
                )

                st.markdown(f"#### 🎓 {qualification}")

                institute = format_value(item.get("Institute"))
                year = format_value(item.get("Year"))
                score = format_value(item.get("Score"))

                st.write(f"**Institute:** {institute}")
                st.write(f"**Year:** {year}")
                st.write(f"**Score:** {score}")

            else:
                st.write(item)


def render_experience(experience_items):
    """Display experience entries."""

    if not experience_items:
        st.info(
            "No professional experience was extracted. "
            "Projects and internships can still strengthen the profile."
        )
        return

    for item in experience_items:
        with st.container(border=True):
            if isinstance(item, dict):
                title = (
                    item.get("Role")
                    or item.get("Title")
                    or item.get("Position")
                    or "Experience"
                )

                st.markdown(f"#### 💼 {title}")

                for key, value in item.items():
                    if key not in {"Role", "Title", "Position"}:
                        st.write(
                            f"**{key}:** {format_value(value)}"
                        )

            else:
                st.write(item)


def render_projects(project_items):
    """Display projects as cards."""

    if not project_items:
        st.info("No projects were extracted.")
        return

    for project in project_items:
        with st.container(border=True):
            if isinstance(project, dict):
                title = (
                    project.get("Title")
                    or project.get("Name")
                    or "Project"
                )

                description = (
                    project.get("Description")
                    or project.get("Details")
                    or ""
                )

                st.markdown(f"#### 🧩 {title}")

                if description:
                    st.write(description)

                for key, value in project.items():
                    if key not in {
                        "Title",
                        "Name",
                        "Description",
                        "Details",
                    }:
                        st.write(
                            f"**{key}:** {format_value(value)}"
                        )

            else:
                st.markdown(f"#### 🧩 {project}")


def render_certifications(certification_items):
    """Display certifications as cards."""

    if not certification_items:
        st.info("No certifications were extracted.")
        return

    for certification in certification_items:
        with st.container(border=True):
            if isinstance(certification, dict):
                title = (
                    certification.get("Title")
                    or certification.get("Name")
                    or "Certification"
                )

                st.markdown(f"#### 🏅 {title}")

                for key, value in certification.items():
                    if key not in {"Title", "Name"}:
                        st.write(
                            f"**{key}:** {format_value(value)}"
                        )

            else:
                st.write(f"🏅 {certification}")


def render_job_cards(matched_jobs):
    """Display matched jobs as individual cards."""

    if matched_jobs is None or matched_jobs.empty:
        st.warning("No matching jobs were found.")
        return

    for rank, (_, job) in enumerate(
        matched_jobs.iterrows(),
        start=1,
    ):
        with st.container(border=True):
            title = format_value(
                job.get("jobtitle"),
                "Job title not provided",
            )

            company = format_value(
                job.get("company"),
                "Company not provided",
            )

            location = format_value(
                job.get("joblocation_address"),
                "Location not provided",
            )

            experience = format_value(
                job.get("experience"),
                "Experience not provided",
            )

            skills = format_value(
                job.get("skills"),
                "Skills not provided",
            )

            st.markdown(f"### {rank}. {title}")

            first_column, second_column, third_column = st.columns(3)

            with first_column:
                st.write(f"🏢 **Company:** {company}")

            with second_column:
                st.write(f"📍 **Location:** {location}")

            with third_column:
                st.write(f"💼 **Experience:** {experience}")

            st.write(f"🛠️ **Skills:** {skills}")


# ---------------------------------------------------------
# Cache the mentor knowledge base
# ---------------------------------------------------------

@st.cache_resource(show_spinner=False)
def prepare_mentor():
    """
    Load, chunk, embed and index the career notes once.
    """

    notes = load_career_notes()
    chunks = chunk_notes(notes)
    chunk_embeddings = embed_chunks(chunks)
    notes_index = build_notes_index(chunk_embeddings)

    return chunks, notes_index


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:
    st.title("💼 SmartHire GenAI")

    st.markdown(
        """
        **Project modules**

        - Resume Parser
        - Semantic Job Search
        - CV Improvement Generator
        - AI Career Mentor
        - Guardrails
        """
    )

    st.divider()

    st.caption(
        "The job recommendations are generated from the locally "
        "stored Naukri job dataset using Gemini embeddings and FAISS."
    )


# ---------------------------------------------------------
# Main heading
# ---------------------------------------------------------

st.markdown(
    '<p class="main-title">💼 SmartHire GenAI</p>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p class="subtitle">
        Resume Matching, AI Resume Feedback and a RAG-based Career Mentor
    </p>
    """,
    unsafe_allow_html=True,
)

st.write(
    "Upload a PDF resume to extract your profile, discover semantically "
    "matching jobs, receive improvement suggestions and ask grounded "
    "career-related questions."
)

st.divider()


# ---------------------------------------------------------
# Resume upload and analysis
# ---------------------------------------------------------

st.header("📤 Upload Resume")

uploaded_file = st.file_uploader(
    "Select a PDF resume",
    type=["pdf"],
    help="Upload a text-based PDF resume.",
)

analyse_button = st.button(
    "Analyse Resume",
    type="primary",
    use_container_width=False,
)


if analyse_button:
    if uploaded_file is None:
        st.warning("Please upload a PDF resume first.")

    else:
        temporary_path = None

        try:
            with st.spinner(
                "Reading the resume and running the SmartHire pipeline..."
            ):
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf",
                ) as temporary_file:
                    temporary_file.write(
                        uploaded_file.getbuffer()
                    )

                    temporary_path = temporary_file.name

                resume_text = load_resume(temporary_path)

                if not resume_text.strip():
                    st.error(
                        "No readable text was found in this PDF. "
                        "Please upload a text-based resume."
                    )
                    st.stop()

                parsed_resume = parse_resume(resume_text)

                matched_jobs = search_jobs(
                    resume_text,
                    top_k=5,
                )

                suggestions = generate_resume_suggestions(
                    parsed_resume,
                    matched_jobs,
                )

                st.session_state["resume_text"] = resume_text
                st.session_state["parsed_resume"] = parsed_resume
                st.session_state["matched_jobs"] = matched_jobs
                st.session_state["suggestions"] = suggestions

            st.success(
                "Resume analysis completed successfully!"
            )

        except FileNotFoundError as error:
            st.error(
                f"A required project file could not be found: {error}"
            )

        except Exception as error:
            st.error(
                f"Resume analysis failed: {error}"
            )

        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.remove(temporary_path)


# ---------------------------------------------------------
# Parsed profile
# ---------------------------------------------------------

if "parsed_resume" in st.session_state:
    parsed_resume = st.session_state["parsed_resume"]

    st.divider()
    st.header("📄 Parsed Resume Profile")

    overview_tab, json_tab = st.tabs(
        ["Profile Overview", "Structured JSON"]
    )

    with overview_tab:
        personal_column, skills_column = st.columns(
            [1, 1.5]
        )

        with personal_column:
            st.subheader("Personal Details")

            with st.container(border=True):
                st.write(
                    f"**Name:** "
                    f"{format_value(parsed_resume.get('Name'))}"
                )

                st.write(
                    f"**Email:** "
                    f"{format_value(parsed_resume.get('Email'))}"
                )

                st.write(
                    f"**Phone:** "
                    f"{format_value(parsed_resume.get('Phone'))}"
                )

                st.write(
                    f"**Target Role:** "
                    f"{format_value(parsed_resume.get('Target Role'))}"
                )

        with skills_column:
            st.subheader("Skills")

            render_skills(
                parsed_resume.get("Skills", [])
            )

        st.subheader("Education")
        render_education(
            parsed_resume.get("Education", [])
        )

        st.subheader("Experience")
        render_experience(
            parsed_resume.get("Experience", [])
        )

        st.subheader("Projects")
        render_projects(
            parsed_resume.get("Projects", [])
        )

        st.subheader("Certifications")
        render_certifications(
            parsed_resume.get("Certifications", [])
        )

    with json_tab:
        st.json(parsed_resume)


# ---------------------------------------------------------
# Matching jobs
# ---------------------------------------------------------

if "matched_jobs" in st.session_state:
    st.divider()
    st.header("💼 Top Matching Jobs")

    st.caption(
        "Jobs are ranked using semantic similarity between "
        "the resume and embedded job descriptions."
    )

    render_job_cards(
        st.session_state["matched_jobs"]
    )


# ---------------------------------------------------------
# Resume suggestions
# ---------------------------------------------------------

if "suggestions" in st.session_state:
    st.divider()
    st.header("📝 Resume Improvement Suggestions")

    with st.container(border=True):
        st.markdown(
            st.session_state["suggestions"]
        )


# ---------------------------------------------------------
# AI Career Mentor
# ---------------------------------------------------------

st.divider()
st.header("🎓 AI Career Mentor")

st.caption(
    "The mentor retrieves information from the provided career notes. "
    "Unsafe and unrelated questions are blocked."
)


if "mentor_messages" not in st.session_state:
    st.session_state["mentor_messages"] = []


for message in st.session_state["mentor_messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


question = st.chat_input(
    "Ask a career, resume, skills, job or interview question"
)


if question:
    st.session_state["mentor_messages"].append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    allowed, guardrail_message = check_input(question)

    if not allowed:
        mentor_answer = guardrail_message

    else:
        try:
            with st.spinner(
                "Searching the career knowledge base..."
            ):
                chunks, notes_index = prepare_mentor()

                mentor_answer = ask_mentor(
                    question,
                    chunks,
                    notes_index,
                )

        except Exception as error:
            mentor_answer = (
                f"The mentor could not answer the question: {error}"
            )

    st.session_state["mentor_messages"].append(
        {
            "role": "assistant",
            "content": mentor_answer,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(mentor_answer)