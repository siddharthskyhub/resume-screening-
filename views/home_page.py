import streamlit as st

import tracker
import ui

STEPS = [
    ("1", "Resume Analyzer",
     "Compare your resume with one job. See which matched skills your projects actually prove.",
     "/analyzer",
     "linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%)"),
    ("2", "ATS Checker",
     "Audit your resume for ATS friendliness: contact details, standard headings, formatting, and action verbs.",
     "/ats-checker",
     "linear-gradient(135deg, #10b981 0%, #059669 100%)"),
    ("3", "Skill Gaps",
     "Compare against several jobs at once and find the gaps that come up most across your target market.",
     "/skill-gaps",
     "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"),
    ("4", "Job Tracker",
     "Keep every application, match score, and note organized on a clean, responsive board.",
     "/tracker",
     "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)"),
    ("5", "Learning Roadmap",
     "Turn your biggest skill gaps into concrete portfolio projects you can add to your resume.",
     "/roadmap",
     "linear-gradient(135deg, #06b6d4 0%, #0284c7 100%)"),
    ("AI", "AI Coach",
     "Fact-checked bullet rewrites, interview questions, and a plain-language fit summary running privately on your computer with Ollama.",
     "/ai-coach",
     "linear-gradient(135deg, #ec4899 0%, #be185d 100%)"),
]

# A polished interactive resume card showcasing the markup vocabulary
SHEET = (
    '<div class="sheet">'
    '<div class="sheet-doc-header">'
    '<div class="sheet-doc-title">📄 Sample Candidate Resume</div>'
    '<span class="sheet-doc-status">Interactive Preview</span>'
    '</div>'
    '<div class="sheet-h">Technical Skills</div>'
    f'<div>Python, SQL, {ui.chip("Docker", "unproven")}, PostgreSQL</div>'
    '<div class="sheet-h">Experience & Projects</div>'
    f'<div>Built a {ui.chip("FastAPI", "matched")} service handling 2,000 requests/day '
    "and cut latency by 35%.</div>"
    '<div class="sheet-ask"><span class="sheet-ask-label">THE JOB ASKS FOR:</span>'
    f'{ui.chip("FastAPI", "matched")}{ui.chip("Docker", "unproven")}{ui.chip("Kubernetes", "missing")}'
    "</div>"
    f"{ui.legend()}"
    "</div>"
)

left, right = st.columns([6, 5], gap="large", vertical_alignment="center")
with left:
    st.markdown(
        '<div class="home-hero-badge">🎯 Evidence-Based Career Intelligence</div>'
        '<div class="home-title">See which skills your resume actually proves.</div>'
        '<p class="home-sub">Traditional keyword matchers give false confidence. SkillMatch identifies whether '
        'required skills are proven by quantifiable projects, merely listed, or missing entirely — then helps you close the gaps.</p>',
        unsafe_allow_html=True,
    )
    c_action1, c_action2, c_action3 = st.columns([1.2, 1.1, 1.3], gap="small")
    with c_action1:
        if st.button("🚀 Analyze resume", type="primary", use_container_width=True):
            st.switch_page("views/analyzer_page.py")
    with c_action2:
        if st.button("⚡ ATS Checker", use_container_width=True):
            st.switch_page("views/ats_checker_page.py")
    with c_action3:
        if st.button("✨ 1-Click Demo", key="btn_home_sample_demo", use_container_width=True):
            ui.load_sample_data()
            st.switch_page("views/analyzer_page.py")
with right:
    st.markdown(ui.interactive_scanner_preview(), unsafe_allow_html=True)

st.write("")
counts = tracker.status_counts()
st.markdown(
    ui.stat_row([
        ("Resume Status", "Loaded in Memory" if st.session_state.get("resume_text") else "Ready for Upload"),
        ("Jobs in Comparison", len(st.session_state.get("gap_jobs", {}))),
        ("Applications Tracked", sum(counts.values())),
    ]),
    unsafe_allow_html=True,
)

st.markdown("### How to Use SkillMatch AI")
st.markdown(
    '<p style="color:var(--muted); margin-top:-6px; margin-bottom:18px;">A comprehensive, evidence-based system to optimize and organize your job search.</p>',
    unsafe_allow_html=True,
)

cards_html = ['<div class="feature-cards-container">']
for number, title, description, route, gradient in STEPS:
    if number.isdigit():
        badge = f'<div class="feature-card-badge flow-num" style="--flow-c:{gradient};">{number}</div>'
    else:
        badge = f'<div class="feature-card-badge flow-opt">{number}</div>'

    cards_html.append(
        f'<a href="{route}" class="feature-card" aria-label="Open {ui.esc(title)}: {ui.esc(description)}">'
        f'{badge}'
        f'<div class="feature-card-content">'
        f'<div class="feature-card-title">{ui.esc(title)}</div>'
        f'<div class="feature-card-desc">{ui.esc(description)}</div>'
        f'</div>'
        f'</a>'
    )
cards_html.append("</div>")

st.markdown("".join(cards_html), unsafe_allow_html=True)

st.caption(
    "🔒 Privacy guarantee: Your resume is processed in local memory and is never saved to external databases. "
    "Only applications you choose to track are stored, locally on your computer."
)
