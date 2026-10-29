# 🚀 ResuMate AI

> **Privacy-First, Evidence-Based Career Intelligence & ATS Resume Matching**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50%2B-FF4B4B.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-18%20Passing-brightgreen.svg)](https://pytest.org/)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20In--Memory-success.svg)](#privacy--security)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**ResuMate AI** is an intelligent career copilot that bridges the gap between candidates and applicant tracking systems (ATS). Unlike conventional keyword matchers that give false confidence, ResuMate analyzes whether your competencies are **quantifiably proven**, **demonstrated in context**, or merely **listed**.

---

## 🏛️ System Architecture

ResuMate AI is designed with a decoupled architecture that cleanly separates presentation, deterministic analytical engines, and an optional local generative AI subsystem.

```mermaid
flowchart TD
    subgraph Client["Client Interface"]
        Browser["User Browser (Desktop / Mobile)"]
        Theme["Theme Controller (Light & Dark Mode)"]
    end

    subgraph Presentation["Presentation Layer (Streamlit 1.50+)"]
        Router["app.py (Navigation & Session State)"]
        UI_Sys["ui.py (Custom Design System & 3D Vector Logos)"]
        
        subgraph Views["Application Views"]
            V_Home["views/home_page.py (Landing & Scanner)"]
            V_Analyzer["views/analyzer_page.py (Evidence Matcher)"]
            V_ATS["views/ats_checker_page.py (ATS Audit & Report)"]
            V_Gaps["views/skill_gaps_page.py (Heatmap & Multi-Job Gaps)"]
            V_Tracker["views/tracker_page.py (Kanban Application Board)"]
            V_Roadmap["views/roadmap_page.py (Prerequisite Learning Path)"]
            V_Coach["views/ai_coach_page.py (Guardrailed AI Coach)"]
        end
    end

    subgraph Domain["Deterministic Domain Engines"]
        Analyzer["analyzer.py (Evidence & Keyword Matcher)"]
        ATSChecker["ats_checker.py (Format, Verbs, Contact & ATS Heuristics)"]
        Gaps["gaps.py (Cross-Job Skill Aggregator)"]
        Roadmap["roadmap.py (DAG Prerequisite & Portfolio Projects)"]
    end

    subgraph AI["Optional Local AI Subsystem"]
        AI_Client["ai.py (Ollama HTTP Client)"]
        FactCheck["Fact-Checking & Anti-Hallucination Guard"]
        Ollama["Local Ollama Daemon (llama3.2 / nomic-embed)"]
    end

    subgraph Storage["Storage & Persistence"]
        Heap["In-Memory Session State (Zero Cloud Ingestion)"]
        SQLite[("data/skillmatch.db (SQLite3 Tracker)")]
        DAO["tracker.py (Application DB DAO)"]
    end

    %% Wiring
    Browser <--> Router
    Browser <--> Theme
    Router --> UI_Sys
    Router --> Views

    V_Analyzer --> Analyzer
    V_ATS --> ATSChecker
    V_Gaps --> Gaps
    V_Roadmap --> Roadmap
    V_Coach --> AI_Client
    V_Tracker --> DAO

    AI_Client --> FactCheck
    AI_Client <--> Ollama
    FactCheck --> Analyzer

    Views <--> Heap
    DAO <--> SQLite
```

> 📖 **Deep Dive**: For full sequence diagrams, scoring formulas, data models, and component specifications, read the complete [**ARCHITECTURE.md**](ARCHITECTURE.md).

---

## ✨ Core Features

- **Resume Analyzer**: Dual-input comparison against target job descriptions with keyword match % and evidence-backed scoring.
- **Evidence-Based Classification**: Skills are categorized into:
  - 🟢 **Strong**: Proven with quantifiable metrics or project outcomes.
  - 🟡 **Demonstrated**: Contextually used in work experience.
  - ⚪ **Listed Only**: Mentioned only in a skills list without supporting context.
- **Dedicated ATS Checker**: Evaluates parse rate, header formatting, contact info completeness, action verb density, measurable achievement percentages, and generates downloadable audit reports.
- **Cross-Job Skill Gaps**: Compare one resume against up to 10 job descriptions simultaneously with ranked frequency charts and heatmaps.
- **Kanban Application Tracker**: SQLite-backed pipeline tracking applications from *Saved* $\rightarrow$ *Applied* $\rightarrow$ *Interviewing* $\rightarrow$ *Offer* $\rightarrow$ *Rejected*.
- **Learning Roadmap**: DAG-based prerequisite roadmap with hands-on portfolio projects and copyable resume bullet templates.
- **Guardrailed AI Coach (Local Ollama)**: Optional local LLM for bullet rewrites, fit summaries, and mock interview prep—all verified by deterministic anti-hallucination checks.

---

## 🔒 Privacy & Security

- **100% In-Memory Processing**: Uploaded resumes (`.pdf`, `.docx`, `.txt`) are parsed strictly in volatile memory. No resume bytes are ever saved to disk or transmitted to external servers.
- **Air-Gapped AI**: The AI Coach connects only to your local Ollama instance (`http://localhost:11434`), ensuring complete confidentiality.

---

## 🚀 Quickstart

### 1. Clone & Setup Environment

```bash
git clone https://github.com/siddharthskyhub/resume-screening-.git
cd resume-screening-

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Live Demo

```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 🤖 Optional: Enable Local AI Coach

The AI Coach is powered by local open-weight models via [Ollama](https://ollama.com):

```bash
# 1. Install Ollama from https://ollama.com
# 2. Pull the recommended lightweight models:
ollama pull llama3.2          # Fast, high-quality reasoning
ollama pull nomic-embed-text  # Dense vector embeddings
```

Once running, navigate to the **AI Coach** tab—it auto-detects Ollama at `http://localhost:11434`.

---

## 🧪 Testing

The platform includes a comprehensive unit test suite:

```bash
pytest
```

---

## 📁 Repository Structure

```text
├── app.py                  # Main application router & sidebar brand card
├── ARCHITECTURE.md         # Detailed architectural specification & design blueprint
├── analyzer.py             # Deterministic resume parsing & evidence matching engine
├── ats_checker.py          # Dedicated ATS compliance, heuristics & report generator
├── gaps.py                 # Multi-role skill gap aggregator & heatmap logic
├── roadmap.py              # Directed acyclic graph (DAG) learning roadmap planner
├── tracker.py              # SQLite DAO & job application pipeline logic
├── ai.py                   # Local Ollama client & anti-hallucination validator
├── ui.py                   # Custom design system, CSS injection & 3D vector logos
├── views/                  # Streamlit view controllers
│   ├── home_page.py        # Landing page with interactive scanner widget
│   ├── analyzer_page.py    # Resume & JD evidence analyzer
│   ├── ats_checker_page.py # ATS test bench & audit report generator
│   ├── skill_gaps_page.py  # Multi-job gap analysis & heatmaps
│   ├── tracker_page.py     # SQLite Kanban application tracker
│   ├── roadmap_page.py     # Skill development roadmap & project templates
│   └── ai_coach_page.py    # Fact-checked local AI career assistant
├── tests/
│   ├── test_ai.py          # Anti-hallucination & Ollama client unit tests
│   └── test_ats_checker.py # ATS heuristics & scoring unit tests
└── data/                   # Local SQLite storage (skillmatch.db)
```

---

## 📄 License

Distributed under the MIT License. Built as an open portfolio project by **Siddharth Kumar**.
