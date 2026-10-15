"""Turn ranked skill gaps into an ordered, project-based learning roadmap."""

from __future__ import annotations

import math

# skill -> skills worth knowing first
PREREQS = {
    "FastAPI": ["Python", "REST APIs"],
    "Django": ["Python"],
    "Flask": ["Python"],
    "Streamlit": ["Python"],
    "Pandas": ["Python"],
    "NumPy": ["Python"],
    "scikit-learn": ["Python", "Pandas", "NumPy"],
    "PyTorch": ["Python", "NumPy"],
    "TensorFlow": ["Python", "NumPy"],
    "Machine Learning": ["Python", "Pandas"],
    "Deep Learning": ["Machine Learning"],
    "NLP": ["Machine Learning"],
    "LLMs": ["Python"],
    "Prompt Engineering": ["LLMs"],
    "RAG": ["LLMs"],
    "LangChain": ["LLMs", "Python"],
    "LangGraph": ["LangChain"],
    "Ollama": ["LLMs"],
    "Hugging Face": ["Python", "Machine Learning"],
    "PostgreSQL": ["SQL"],
    "MySQL": ["SQL"],
    "React": ["JavaScript", "HTML", "CSS"],
    "Node.js": ["JavaScript"],
    "TypeScript": ["JavaScript"],
    "Tailwind CSS": ["CSS"],
    "Kubernetes": ["Docker"],
    "CI/CD": ["Git"],
    "GitHub": ["Git"],
}

# Rough hours to become job-ready enough to build a small project.
HOURS = {
    "Python": 40, "SQL": 20, "Git": 6, "GitHub": 4, "Docker": 12,
    "Kubernetes": 30, "AWS": 30, "Azure": 30, "GCP": 30, "Linux": 15,
    "React": 40, "JavaScript": 40, "TypeScript": 15, "HTML": 10, "CSS": 12,
    "Node.js": 20, "FastAPI": 15, "Django": 25, "Flask": 15, "REST APIs": 10,
    "Pandas": 15, "NumPy": 10, "scikit-learn": 20, "PyTorch": 30,
    "TensorFlow": 30, "Machine Learning": 40, "Deep Learning": 40, "NLP": 25,
    "LLMs": 12, "RAG": 15, "LangChain": 12, "LangGraph": 10, "Ollama": 5,
    "Hugging Face": 15, "Prompt Engineering": 6, "PostgreSQL": 15,
    "MySQL": 12, "MongoDB": 12, "SQLite": 5, "Redis": 8, "CI/CD": 10,
    "Data Structures": 40, "OOP": 15, "Streamlit": 8, "Excel": 10,
    "Java": 50, "C++": 50, "Tailwind CSS": 8,
}
DEFAULT_HOURS = 15
PROVE_HOURS = 8  # skills you already list only need a proof project

PROJECTS = {
    "Python": "Build a CLI expense tracker with file storage and unit tests.",
    "SQL": "Design a small database (3-4 tables) and write reports with joins and aggregates.",
    "Git": "Contribute to one repo using branches and pull requests, with a clean history.",
    "GitHub": "Publish 2 projects with README files, screenshots, and setup instructions.",
    "Docker": "Containerize one of your existing apps and document the run command.",
    "Kubernetes": "Deploy a containerized app to a local cluster (minikube) with a Service.",
    "AWS": "Host a small app using EC2 or Lambda plus S3, and note the services used.",
    "React": "Build a small dashboard that fetches and displays data from an API.",
    "JavaScript": "Build an interactive to-do or quiz app without a framework.",
    "TypeScript": "Convert a small JavaScript project to TypeScript with strict types.",
    "FastAPI": "Build a CRUD API with validation, tests, and auto-generated docs.",
    "Django": "Build a blog or notes app with authentication.",
    "Flask": "Build a URL shortener with a small database.",
    "REST APIs": "Design and document a 4-endpoint API; consume a public API in a script.",
    "Pandas": "Clean and analyze a public dataset and publish the findings as a notebook.",
    "NumPy": "Implement linear regression from scratch with NumPy and compare to scikit-learn.",
    "scikit-learn": "Train and compare 3 models on a Kaggle dataset with proper evaluation.",
    "PyTorch": "Train an image classifier and report accuracy and training curves.",
    "Machine Learning": "Complete an end-to-end prediction project: data, model, metrics, write-up.",
    "LLMs": "Build a small app that calls an LLM and handles errors, prompts, and costs.",
    "RAG": "Build a document Q&A app over your own PDFs and measure answer quality.",
    "LangChain": "Rebuild a simple Q&A or summarizer workflow using LangChain components.",
    "LangGraph": "Build a multi-step agent with a graph and at least one tool call.",
    "Ollama": "Run a local model and wire it into a small chat or summarization app.",
    "Streamlit": "Ship a data app with inputs, charts, and a deployed demo link.",
    "PostgreSQL": "Move a project's data into PostgreSQL and add indexes for slow queries.",
    "MongoDB": "Store and query JSON documents for a small app.",
    "CI/CD": "Add a pipeline that runs tests and lints on every push.",
    "Data Structures": "Solve 30 curated problems and write up the patterns you learned.",
}


def _project(skill: str) -> str:
    return PROJECTS.get(
        skill,
        f"Build a small project using {skill} and document it with a README and results.",
    )


def _bullet(skill: str) -> str:
    return f"Built [what you built] using {skill} to [purpose], achieving [measurable result]."


def build_roadmap(
    gaps: list[dict],
    have: set[str],
    hours_per_week: int = 8,
    max_skills: int = 6,
    include_proofs: bool = True,
) -> list[dict]:
    """Order the top gaps (plus any missing prerequisites) into a plan.

    gaps: rows from gaps.analyze_jobs()["gaps"], already ranked by priority.
    have: skills already on the resume (used to skip prerequisites).
    """
    hours_per_week = max(1, hours_per_week)
    by_skill = {g["skill"]: g for g in gaps}
    targets = [g for g in gaps if include_proofs or g["status"] == "missing"][:max_skills]

    items: list[dict] = []
    placed: set[str] = set()

    def visit(skill: str, needed_for: str | None = None, stack: tuple = ()):
        if skill in placed or skill in stack:
            return
        for prereq in PREREQS.get(skill, []):
            if prereq not in have:
                visit(prereq, needed_for=skill, stack=stack + (skill,))
        placed.add(skill)

        gap = by_skill.get(skill)
        if gap is not None:
            kind = "prove" if gap["status"] == "listed" else "learn"
            reason = (
                f"Appears in {gap['demand']} of {gap['n_jobs']} jobs "
                f"({gap['required']} as required)."
            )
            demand = gap["demand"]
        else:
            kind = "prerequisite"
            reason = f"Foundation for {needed_for}."
            demand = 0

        hours = HOURS.get(skill, DEFAULT_HOURS)
        if kind == "prove":
            hours = min(hours, PROVE_HOURS)

        items.append({
            "skill": skill,
            "kind": kind,
            "reason": reason,
            "hours": hours,
            "demand": demand,
            "project": _project(skill),
            "bullet": _bullet(skill),
        })

    for gap in targets:
        visit(gap["skill"])

    elapsed = 0
    for order, item in enumerate(items, start=1):
        item["order"] = order
        item["start_week"] = elapsed // hours_per_week + 1
        elapsed += item["hours"]
        item["end_week"] = max(item["start_week"], math.ceil(elapsed / hours_per_week))
    return items


def roadmap_markdown(items: list[dict], hours_per_week: int) -> str:
    total = sum(i["hours"] for i in items)
    lines = [
        "# My Learning Roadmap",
        "",
        f"Plan: {len(items)} steps, about {total} hours at {hours_per_week} h/week "
        f"(roughly {math.ceil(total / max(1, hours_per_week))} weeks).",
        "",
    ]
    labels = {"learn": "Learn", "prove": "Prove it", "prerequisite": "Prerequisite"}
    for i in items:
        weeks = (
            f"Week {i['start_week']}"
            if i["start_week"] == i["end_week"]
            else f"Weeks {i['start_week']}-{i['end_week']}"
        )
        lines += [
            f"## {i['order']}. {i['skill']} ({labels[i['kind']]})",
            f"- When: {weeks} (~{i['hours']} h)",
            f"- Why: {i['reason']}",
            f"- Project: {i['project']}",
            f"- Resume bullet template: {i['bullet']}",
            "",
        ]
    lines.append("Only add a skill to your resume once you have actually built something with it.")
    return "\n".join(lines)
