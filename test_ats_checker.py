"""Unit tests for the ATS Resume Checker module."""

import pytest
from ats_checker import (
    audit_action_verbs,
    audit_formatting,
    build_ats_report,
    check_ats,
    extract_contact_info,
)

SAMPLE_RESUME = """
John Doe
john.doe@example.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe
San Francisco, CA

Professional Summary
Senior Software Engineer with 5+ years of experience building high-scale Python web applications.

Experience
Acme Corporation - Senior Software Engineer
• Architected and deployed a FastAPI microservice handling 50,000 daily requests, reducing latency by 35%.
• Engineered automated CI/CD deployment pipelines using Docker and GitHub Actions, cutting release time by 50%.
• Led a cross-functional team of 4 engineers to rebuild the analytics dashboard in React.

Projects
SkillMatch AI - Founder & Lead Developer
• Developed an NLP-driven resume analyzer in Python and Streamlit with 2,000+ active GitHub stars.
• Optimized database queries in PostgreSQL, improving throughput by 40%.

Skills
Languages: Python, SQL, JavaScript, HTML, CSS
Frameworks: FastAPI, Django, React
DevOps: Docker, AWS, Git

Education
University of California, Berkeley
Bachelor of Science in Computer Science, 2020
"""

POOR_RESUME = """
Hi, this is Alex.
I am a hard worker and quick learner looking for a job.
Responsible for assisting in various tasks and helped with some coding.
"""


def test_extract_contact_info():
    contacts = extract_contact_info(SAMPLE_RESUME)
    assert contacts["email"] == "john.doe@example.com"
    assert contacts["phone"] is not None
    assert "linkedin.com/in/johndoe" in contacts["linkedin"]
    assert "github.com/johndoe" in contacts["github"]


def test_audit_action_verbs():
    verbs = audit_action_verbs(SAMPLE_RESUME)
    assert len(verbs["strong_verbs_unique"]) >= 4
    assert "architected" in verbs["strong_verbs_unique"]
    assert "engineered" in verbs["strong_verbs_unique"]
    assert "developed" in verbs["strong_verbs_unique"]
    assert len(verbs["weak_phrases_found"]) == 0


def test_audit_formatting():
    fmt = audit_formatting(SAMPLE_RESUME)
    assert fmt["word_count"] > 100
    assert fmt["bullet_count"] >= 4
    assert fmt["quantified_bullets"] >= 3
    assert len(fmt["problematic_chars"]) == 0


def test_check_ats_high_score():
    audit = check_ats(SAMPLE_RESUME)
    assert audit["score"] >= 80
    assert audit["grade"] in ("A", "B")
    assert any(c["status"] == "pass" for c in audit["checks"])


def test_check_ats_poor_resume():
    audit = check_ats(POOR_RESUME)
    assert audit["score"] < 60
    assert audit["grade"] in ("C", "D")
    # Should flag missing email, missing sections, buzzwords, passive verbs
    weak_found = audit["verbs"]["weak_phrases_found"]
    buzz_found = audit["verbs"]["buzzwords_found"]
    assert len(weak_found) > 0 or len(buzz_found) > 0


def test_build_ats_report():
    audit = check_ats(SAMPLE_RESUME, job_text="Looking for a Python and FastAPI engineer with Docker experience.")
    report = build_ats_report(audit)
    assert "SKILLMATCH AI - ATS RESUME AUDIT REPORT" in report
    assert "Overall ATS Score:" in report
    assert "TARGET JOB KEYWORD ALIGNMENT" in report
