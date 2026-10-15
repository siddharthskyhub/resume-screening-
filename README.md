# 🎯 SkillMatch AI

A career copilot built with Python and Streamlit. Compare your resume with job
descriptions, see which skills your resume actually *proves*, find the gaps that
matter most across all your target roles, track applications, and get a
project-based learning roadmap.

## Features
- **Resume Analyzer**: required vs. nice-to-have skills, keyword match and an
  evidence-backed match score, resume health checks.
- **Evidence-based matching**: each skill is labelled *strong* (used in a project/job
  with a result), *demonstrated*, or *listed only*.
- **Skill Gaps**: compare one resume against up to 10 jobs; ranked gaps and a heatmap.
- **Job Tracker**: Kanban board backed by SQLite; saves match score and missing skills.
- **Learning Roadmap**: prerequisite-aware plan with projects and resume bullet templates.
- **AI Coach** (optional, local): fact-checked bullet rewriting, semantic matching, fit summary,
  and interview questions, all through [Ollama](https://ollama.com).

## Run it
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional: enable the AI Coach
The AI Coach runs on a local model, so your resume never leaves your machine. Everything else
works without it.
```bash
# install Ollama from https://ollama.com, then:
ollama pull llama3.2          # chat model
ollama pull nomic-embed-text  # embedding model
```
Open the **AI Coach** page. It detects Ollama automatically (default `http://localhost:11434`).

Design rules: scores never come from the AI, and every AI output is checked against the
deterministic analysis. A rewritten bullet that adds a number or skill not in the original is
flagged, and a summary that mentions a skill outside the facts is flagged.

## Test it
```bash
pytest
```

## Project layout
| File | Purpose |
|------|---------|
| `app.py` | Entry point, navigation, and sidebar |
| `.streamlit/config.toml` | Theme colors and toolbar settings |
| `analyzer.py` | Skill matching, evidence extraction, scoring, file reading |
| `gaps.py` | Multi-job gap analysis |
| `roadmap.py` | Learning roadmap builder |
| `tracker.py` | SQLite application tracker |
| `ai.py` | Ollama client, fact-checked rewriting, semantic matching, summaries |
| `ui.py` | Shared styling and resume loader |
| `views/` | One file per page (home, analyzer, gaps, tracker, roadmap, AI coach) |

## Notes
- Your resume is processed in memory and never written to disk. Only tracker entries
  (which you choose to save) are stored in `data/skillmatch.db`.
- On hosts with ephemeral storage (e.g. Streamlit Community Cloud) the tracker database
  resets when the app restarts. Set `SKILLMATCH_DB` to a persistent path, or use a hosted DB.
- Scores measure keyword evidence only. They do not predict hiring outcomes.
