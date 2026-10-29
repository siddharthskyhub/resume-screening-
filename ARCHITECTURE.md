# ResuMate AI — System Architecture & Technical Specification

> **Platform**: ResuMate AI (formerly SkillMatch AI)  
> **Type**: Privacy-First, Evidence-Based Career Intelligence, Hybrid RAG & ATS Optimization Platform  
> **Version**: 2.0.0  
> **Runtime**: Python 3.10+ / Streamlit 1.50+ / SQLite3 / Optional Local Ollama (Llama 3.2 + nomic-embed-text)

---

## 1. Executive Summary & Design Philosophy

ResuMate AI is an evidence-backed career companion engineered to bridge the gap between job seekers and applicant tracking systems (ATS). Unlike conventional keyword counters that induce false confidence, ResuMate evaluates whether competencies are **quantifiably proven**, **demonstrated**, or merely **listed**.

### Core Architecture Pillars

1. **Privacy-First & Zero-Cloud Ingestion**: Resumes are parsed directly in volatile memory and never persisted to disk or transmitted to third-party cloud servers.
2. **Deterministic Ground Truth**: All matching scores, ATS compliance metrics, and gap analyses are calculated through deterministic algorithms with unit-test guarantees.
3. **Hybrid RAG & Semantic Retrieval**: Combines dense vector embeddings (`nomic-embed-text`) with sparse lexical matching (Okapi BM25 heuristics) fused via Reciprocal Rank Fusion (RRF).
4. **Guardrailed Local AI**: Generative AI features (bullet rewrites, semantic synthesis) run strictly through local LLMs ([Ollama](https://ollama.com)) and pass through automated fact-checking engines that prevent hallucinations.
5. **Decoupled Architecture**: Pure computational engines (`analyzer.py`, `ats_checker.py`, `gaps.py`, `roadmap.py`) have zero Streamlit dependencies, ensuring complete testability and CLI/API portability.

---

## 2. High-Level Architecture Blueprint

```mermaid
flowchart TD
    subgraph Client["Client Browser Interface"]
        UI["Web Browser (Desktop / Mobile)"]
        ThemeSwitch["Theme Controller (Light / Dark Mode)"]
    end

    subgraph Presentation["Presentation & Application Layer"]
        App["app.py (Streamlit Entrypoint & Navigation Router)"]
        Sidebar["Sidebar Controller (Status & Brand Card)"]
        DesignSys["ui.py (Custom Design System, CSS & SVG Vectors)"]
        
        subgraph Views["Views & Route Controllers"]
            V_Home["views/home_page.py (Landing & Interactive Scanner)"]
            V_Analyzer["views/analyzer_page.py (Evidence Matcher)"]
            V_ATS["views/ats_checker_page.py (ATS Audit & Report)"]
            V_Gaps["views/skill_gaps_page.py (Multi-Job Heatmap)"]
            V_Tracker["views/tracker_page.py (Kanban Application Board)"]
            V_Roadmap["views/roadmap_page.py (Prerequisite Learning Path)"]
            V_AICoach["views/ai_coach_page.py (Guardrailed AI Coach)"]
        end
    end

    subgraph Domain["Core Computational Engines (Deterministic)"]
        AnalyzerEng["analyzer.py (Keyword & Evidence Matcher)"]
        ATSEng["ats_checker.py (Format, Verbs, Contact & ATS Scanner)"]
        GapsEng["gaps.py (Cross-Job Skill Aggregator)"]
        RoadmapEng["roadmap.py (DAG Prerequisite & Project Generator)"]
    end

    subgraph AISubsystem["Local Hybrid RAG & Guardrail Subsystem"]
        AIEng["ai.py (Ollama Client & Vector Embedding Engine)"]
        FactChecker["Fact-Checking & Anti-Hallucination Guard"]
        OllamaServer["Local Ollama Daemon (llama3.2 / nomic-embed)"]
    end

    subgraph Storage["Data & Session Layer"]
        SessionState["Streamlit Session State (Volatile Memory)"]
        SQLiteDB[("data/skillmatch.db (SQLite3 Storage)")]
        TrackerEng["tracker.py (Application DB DAO)"]
    end

    %% Client Interactions
    UI <--> App
    UI <--> ThemeSwitch

    %% Navigation & Routing
    App --> Sidebar
    App --> DesignSys
    App --> Views

    %% Views to Engines
    V_Analyzer --> AnalyzerEng
    V_ATS --> ATSEng
    V_Gaps --> GapsEng
    V_Roadmap --> RoadmapEng
    V_Tracker --> TrackerEng
    V_AICoach --> AIEng

    %% AI Pipeline
    AIEng --> FactChecker
    AIEng <--> OllamaServer
    FactChecker --> AnalyzerEng

    %% State & Storage
    Views <--> SessionState
    TrackerEng <--> SQLiteDB
```

---

## 3. Hybrid RAG & Guardrailed LLM Pipeline

ResuMate AI incorporates a complete **Hybrid Retrieval-Augmented Generation (Hybrid RAG)** architecture ensuring that candidates receive credit for both verbatim technical terms and conceptually related experience:

```mermaid
flowchart TD
    Query["User Query / Candidate Resume & Target Job Description"]
    
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
- **Dense Vector Retrieval (`nomic-embed-text`)**: Generates 768-dimensional embeddings for both parsed resume bullet chunks and target job requirement sentences. Cosine similarity surfaces semantic alignments that lack exact keyword matches (e.g. *"developed scalable event-driven workers"* $\leftrightarrow$ *"RabbitMQ message queuing"*).
- **Sparse BM25 & Lexical Matcher**: Evaluates exact technical keywords, tool names, and evidence categories (*Strong*, *Demonstrated*, *Listed Only*) using frequency analysis and section heuristics.

### 2. Reciprocal Rank Fusion (RRF)
To unify dense semantic and sparse lexical signals, candidate evidence chunks are merged via Reciprocal Rank Fusion:

$$RRF(d) = \frac{\alpha}{k + r_{\text{dense}}(d)} + \frac{1 - \alpha}{k + r_{\text{sparse}}(d)}$$

Where:
- $r_{\text{dense}}(d)$ is the rank position in the semantic vector search.
- $r_{\text{sparse}}(d)$ is the rank position in the lexical/evidence matcher.
- $k = 60$ is the standard smoothing constant preventing high-rank domination.
- $\alpha \in [0, 1]$ balances semantic similarity against exact lexical presence.

### 3. Strict Grounding Prompt Builder
The Top-K fused evidence chunks are formatted with explicit reference boundaries:
- Enforces an explicit **refusal policy** (`REWRITE_SYSTEM`, `SUMMARY_SYSTEM`).
- Prohibits the LLM from fabricating unverified metrics, new tools, or unmentioned employers.
- Inserts candidate placeholders (e.g., `[X%]` or `[number of users]`) when measurable impact is missing rather than inventing fictional data.

### 4. Local LLM Generation (`Llama 3.2`)
Inference executes strictly on-device through Ollama (`http://localhost:11434`), generating context-grounded bullet rewrites, fit summaries, and role-specific interview prep.

### 5. Anti-Hallucination Guardrail & Citation Verifier
Before any LLM-generated text reaches the user interface, it passes through an automated validation gate in [`ai.py`](ai.py):
- **Metric Verification**: Compares extracted numerical metrics against the original bullet. Any invented number causes an immediate rejection and regeneration.
- **Skill Verification**: Scans generated text for technical skills not present in the source facts.
- **Sentence Faithfulness Score**: Rejects responses exceeding acceptable token drift.

---

## 4. End-to-End Data Flow Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor User as Candidate
    participant UI as Browser / Streamlit UI
    participant Parser as In-Memory Ingestion (pypdf/docx)
    participant Core as Deterministic Matching Engine
    participant Guard as Fact-Checking Filter
    participant Ollama as Local Ollama LLM
    participant DB as SQLite Application DB

    User->>UI: Upload Resume (PDF / DOCX / TXT)
    UI->>Parser: Stream file bytes into memory
    Parser-->>Core: Normalized Plaintext & Structure
    
    User->>UI: Input Job Description (JD)
    UI->>Core: Analyze(resume_text, jd_text)
    Core->>Core: Tokenize, Extract Sections, Identify Evidence Levels
    Core->>Core: Compute Keyword %, Evidence %, ATS Score
    Core-->>UI: Interactive Cards, Score Gauges & Skill Chips

    opt AI Enhancement Requested (e.g. Bullet Rewriting via RAG)
        User->>UI: Request AI Bullet Optimization
        UI->>Ollama: Generate Rewritten Bullet with Top-K Grounding
        Ollama-->>Guard: Raw Generated Bullet
        Guard->>Core: Verify against extracted facts (metrics, skills, action verbs)
        alt Passed Verification
            Guard-->>UI: Verified High-Impact Bullet
        else Hallucination Detected (Unproven metric or skill added)
            Guard-->>UI: Warning Flag + Remediation Suggestion
        end
    end

    opt Track Job Application
        User->>UI: Save Role to Tracker
        UI->>DB: INSERT / UPDATE application record
        DB-->>UI: Updated Kanban Board
    end
```

---

## 5. Module Decomposition & Responsibilities

| Layer / Module | Primary File | Core Responsibilities & Algorithms | External Dependencies |
| :--- | :--- | :--- | :--- |
| **Routing & App Shell** | [`app.py`](file:///c:/Users/Siddharth%20kumar/Documents/resume-job-matching-04/app.py) | Streamlit multi-page router (`st.navigation`), session initialization, global sidebar brand card, memory status indicator. | `streamlit` |
| **Design System** | [`ui.py`](file:///c:/Users/Siddharth%20kumar/Documents/resume-job-matching-04/ui.py) | Responsive CSS injection, light/dark theme switcher, SVG vector generation (`brand_logo`, `ai_coach_logo`), custom HTML widgets. | Pure Python + CSS |
| **Resume & Skill Analyzer** | [`analyzer.py`](file:///c:/Users/Siddharth%20kumar/Documents/resume-job-matching-04/analyzer.py) | Evidence-based classification: `strong` (metric/result backed), `demonstrated` (contextual use), and `unproven` (listed only). Text extraction from PDF/DOCX. | `pypdf`, `python-docx` |
| **ATS Compliance Engine** | [`ats_checker.py`](file:///c:/Users/Siddharth%20kumar/Documents/resume-job-matching-04/ats_checker.py) | Full ATS heuristic suite: parse rate, contact detection, action verb density, measurable results percentage, hazard checks, text audit report generator. | Pure Python / Regex |
| **Skill Gap Analyzer** | [`gaps.py`](file:///c:/Users/Siddharth%20kumar/Documents/resume-job-matching-04/gaps.py) | Aggregates skill deficits across up to 10 job descriptions, computes frequency weights, outputs heatmap matrices. | Pure Python |
| **Roadmap Planner** | [`roadmap.py`](file:///c:/Users/Siddharth%20kumar/Documents/resume-job-matching-04/roadmap.py) | Directed acyclic graph (DAG) of technical competencies, prerequisite scheduling, hands-on portfolio project templates. | Pure Python |
| **Application Tracker** | [`tracker.py`](file:///c:/Users/Siddharth%20kumar/Documents/resume-job-matching-04/tracker.py) | SQLite-backed job application pipeline (Saved $\rightarrow$ Applied $\rightarrow$ Interviewing $\rightarrow$ Offer $\rightarrow$ Rejected $\rightarrow$ Archived). | `sqlite3` |
| **Local AI & RAG Engine** | [`ai.py`](file:///c:/Users/Siddharth%20kumar/Documents/resume-job-matching-04/ai.py) | Ollama HTTP client (`llama3.2`, `nomic-embed-text`), dense embeddings, cosine similarity, deterministic hallucination verification. | `urllib` / Ollama API |

---

## 6. Evidence-Based Scoring Algorithm

Rather than counting simple string occurrences, ResuMate implements a tripartite evidence classification model:

```mermaid
flowchart TD
    Token["Extracted Skill Token (e.g. 'FastAPI')"] --> InResume{"Present in Resume?"}
    
    InResume -- "No" --> Missing["Missing (0 pts)"]
    InResume -- "Yes" --> CheckEvidence{"Surrounding Sentence Analysis"}

    CheckEvidence -- "Quantifiable Metric or Result Found" --> Strong["Strong Evidence (1.0 pts)"]
    CheckEvidence -- "Action Verb & Context Found" --> Demonstrated["Demonstrated (0.65 pts)"]
    CheckEvidence -- "Only in Skills / Tools List" --> Listed["Listed Only (0.25 pts)"]

    Strong --> ScoreCalc["Composite Match Score Calculation"]
    Demonstrated --> ScoreCalc
    Listed --> ScoreCalc
    Missing --> ScoreCalc
```

### Mathematical Formulation

Given required skills set $R$ and nice-to-have skills set $N$, where each skill $s$ has evidence weight $w(s) \in \{0.0, 0.25, 0.65, 1.0\}$:

$$\text{Evidence Score} = \frac{0.75 \sum_{s \in R} w(s) + 0.25 \sum_{s \in N} w(s)}{0.75 |R| + 0.25 |N|} \times 100$$

---

## 7. Data Storage & Schema Design

Application tracking is persisted in local SQLite storage at `data/skillmatch.db` (customizable via `SKILLMATCH_DB` environment variable):

```mermaid
erDiagram
    APPLICATIONS {
        INTEGER id PK
        TEXT company "Company Name"
        TEXT role "Target Role Title"
        TEXT job_url "Job Description Link"
        TEXT location "Location / Remote Status"
        REAL salary "Target Compensation"
        TEXT status "Saved | Applied | Interviewing | Offer | Rejected | Archived"
        INTEGER match_score "Calculated Evidence Score"
        TEXT missing_skills "Comma-separated Missing Skills"
        TEXT notes "Candidate Notes & Next Steps"
        TEXT created_at "ISO-8601 Timestamp"
        TEXT updated_at "ISO-8601 Timestamp"
    }
```

---

## 8. Security, Privacy & Runtime Topology

- **Network Isolation**: The application operates completely air-gapped from cloud data processors. Resume bytes reside solely in volatile Python heap space during the Streamlit session and are discarded upon page reload or session close.
- **Client-Side Rendering**: Custom theme preferences are stored in the user's browser `localStorage` without tracking cookies.
- **Portability**: Packaged to run seamlessly via Docker Dev Containers (`.devcontainer/devcontainer.json`), standard Python virtual environments (`venv`), or self-hosted intranet instances.
