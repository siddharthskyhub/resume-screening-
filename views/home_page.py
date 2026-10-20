import streamlit as st

import tracker
import ui

STEPS = [
    ("1", "Resume analyzer",
     "Compare your resume with one job. See which matched skills your projects actually prove.",
     "views/analyzer_page.py",
     "linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%)"),
    ("2", "ATS checker",
     "Audit your resume for ATS friendliness: contact details, standard headings, formatting, and action verbs.",
     "views/ats_checker_page.py",
     "linear-gradient(135deg, #10b981 0%, #059669 100%)"),
    ("3", "Skill gaps",
     "Compare against several jobs at once and find the gaps that come up most across your target market.",
     "views/skill_gaps_page.py",
     "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"),
    ("4", "Job tracker",
     "Keep every application, match score, and note organized on a clean, responsive board.",
     "views/tracker_page.py",
     "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)"),
    ("5", "Learning roadmap",
     "Turn your biggest skill gaps into concrete portfolio projects you can add to your resume.",
     "views/roadmap_page.py",
     "linear-gradient(135deg, #06b6d4 0%, #0284c7 100%)"),
    ("AI", "AI coach",
     "Fact-checked bullet rewrites, interview questions, and a plain-language fit summary running privately on your computer with Ollama.",
     "views/ai_coach_page.py",
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
    c_action1, c_action2 = st.columns([1, 1])
    with c_action1:
        if st.button("🚀 Analyze a resume", type="primary", use_container_width=True):
            st.switch_page("views/analyzer_page.py")
    with c_action2:
        if st.button("✨ 1-Click Demo (Sample data)", key="btn_home_sample_demo", use_container_width=True):
            ui.load_sample_data()
            st.switch_page("views/analyzer_page.py")
with right:
    st.markdown(SHEET, unsafe_allow_html=True)

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

for number, title, description, path, gradient in STEPS:
    text_col, link_col = st.columns([9, 2], vertical_alignment="center")
    badge = (
        f'<div class="flow-num" style="--flow-c:{gradient};">{number}</div>' if number.isdigit()
        else f'<div class="flow-opt">{number}</div>'
    )
    text_col.markdown(
        f'<div class="flow">{badge}<div><div class="flow-title">{ui.esc(title.capitalize())}</div>'
        f'<div class="flow-desc">{ui.esc(description)}</div></div></div>',
        unsafe_allow_html=True,
    )
    link_col.page_link(path, label=f"Open {title.lower()}", use_container_width=True)

st.caption(
    "🔒 Privacy guarantee: Your resume is processed in local memory and is never saved to external databases. "
    "Only applications you choose to track are stored, locally on your computer."
)
