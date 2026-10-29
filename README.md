# 🚀 ResuMate AI

> **Privacy-First, Evidence-Based Career Intelligence, Hybrid RAG & ATS Resume Optimization**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50%2B-FF4B4B.svg)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Llama%203.2%20%7C%20nomic--embed-orange.svg)](https://ollama.com/)
[![RAG](https://img.shields.io/badge/RAG-Hybrid%20Dense%20%2B%20BM25-purple.svg)](#-hybrid-rag--guardrailed-llm-pipeline)
[![Tests](https://img.shields.io/badge/Tests-18%20Passing-brightgreen.svg)](https://pytest.org/)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20In--Memory-success.svg)](#-privacy--security)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**ResuMate AI** is an intelligent, privacy-first career copilot that bridges the gap between candidates and applicant tracking systems (ATS). Unlike conventional keyword matchers that give false confidence, ResuMate implements a **Hybrid Retrieval-Augmented Generation (Hybrid RAG) and deterministic auditing engine** to evaluate whether competencies are **quantifiably proven**, **demonstrated in context**, or merely **listed**.

---

## 🏛️ System Architecture

ResuMate AI is designed with a decoupled architecture separating the presentation layer, deterministic analytical engines, in-memory state, and an optional local generative AI subsystem.

```mermaid
flowchart TD
    subgraph Client["Client Interface"]
        Browser["User Browser (Desktop / Mobile)"]
        Theme["Theme Controller (Light & Dark Mode)"]
    end

    subgraph Presentation["Presentation Layer (Streamlit 1.50+)"]
        Router["app.py (Navigation Router & State Controller)"]
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

    subgraph AI["Local Hybrid RAG & LLM Subsystem"]
        AI_Client["ai.py (Ollama Client & Embeddings Engine)"]
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

---

## 🔬 Hybrid RAG & Guardrailed LLM Pipeline

The AI coaching and semantic matching subsystem uses a **Dual-Path Hybrid Search (Dense Vector + Sparse BM25) with Reciprocal Rank Fusion (RRF)** and an **Anti-Hallucination Fact-Checking Guardrail**:

```mermaid
flowchart TD
    Query["User Query / Resume & Job Description"]
    
    Query --> Dense["Dense Vector Search (nomic-embed-text)"]
    Query --> Sparse["Sparse BM25 Search (Okapi BM25 & Evidence Matcher)"]
    
    Dense --> RankedDense["Ranked Dense Chunks"]
    Sparse --> RankedSparse["Ranked Sparse Chunks"]
    
    RankedDense --> RRF["Reciprocal Rank Fusion (RRF)"]
    RankedSparse --> RRF
    
    RRF --> TopK["Top-K Scored Evidence Chunks"]
    
    TopK --> PromptBuilder["Strict Grounding Prompt Builder (Chunk IDs + Refusal Policy)"]
    
    PromptBuilder --> Ollama["Ollama LLM (Llama 3.2 Context-Grounded Answer)"]
    
    Ollama --> Guardrail["Anti-Hallucination Guardrail (Citation & Fact Verifier)"]
    
    Guardrail --> Dashboard["Interactive Web Dashboard (Streamlit 1.50+)"]
```

### 1. Dual-Path Retrieval
- **Dense Vector Search (`nomic-embed-text`)**: Embeds job requirements and candidate experience bullets into high-dimensional vector spaces, computing cosine similarity to surface matches by underlying meaning (e.g. *"orchestrated container clusters"* $\leftrightarrow$ *"Kubernetes administrator"*).
- **Sparse BM25 & Lexical Matcher**: Evaluates exact technical keywords, tool names, and evidence categories (*Strong*, *Demonstrated*, *Listed Only*) using frequency analysis and section heuristics.

### 2. Reciprocal Rank Fusion (RRF)
Combines dense semantic and sparse lexical rankings to ensure candidates receive credit for both verbatim skills and conceptual experience:

$$RRF(d) = \frac{\alpha}{k + r_{\text{dense}}(d)} + \frac{1 - \alpha}{k + r_{\text{sparse}}(d)}$$

*(where $k = 60$ is the standard smoothing constant and $\alpha$ balances dense semantic similarity vs. exact keyword presence).*

### 3. Strict Grounding Prompt Builder
Injects retrieved candidate chunks with strict reference boundaries:
- Enforces an explicit **refusal policy** (`REWRITE_SYSTEM`, `SUMMARY_SYSTEM`).
- Prohibits the LLM from creating unverified metrics, new tools, or unmentioned employers.
- Inserts candidate placeholders (e.g., `[X%]` or `[number of users]`) when measurable impact is missing rather than inventing fictional data.

### 4. Local LLM Generation (`Llama 3.2`)
Runs on-device via local Ollama inference (`http://localhost:11434`), generating context-grounded bullet rewrites, fit summaries, and role-specific interview prep.

### 5. Anti-Hallucination Guardrail
Before any LLM-generated output reaches the UI, it passes through an automated validation gate in [`ai.py`](ai.py):
- **Metric Verification**: Compares extracted numerical metrics against the original bullet. Any invented number causes an immediate rejection and regeneration.
- **Skill Verification**: Scans generated text for technical skills not present in the source facts.
- **Sentence Faithfulness Score**: Rejects responses exceeding acceptable token drift.

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
- **AI Coach with RAG & Guardrails**: On-device LLM assistance for bullet rewrites, fit summaries, and mock interview prep—all verified by deterministic anti-hallucination checks.

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

## 🤖 Enable Local AI & RAG Subsystem

The AI Coach and Semantic Matcher are powered by local open-weight models via [Ollama](https://ollama.com):

```bash
# 1. Install Ollama from https://ollama.com
# 2. Pull the recommended lightweight models:
ollama pull llama3.2          # Context-grounded generation
ollama pull nomic-embed-text  # Dense vector search & RAG embeddings
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
├── ai.py                   # Local Ollama RAG client & anti-hallucination validator
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
