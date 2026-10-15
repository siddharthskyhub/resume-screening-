import streamlit as st

import tracker
import ui

STEPS = [
    ("1", "Resume analyzer",
     "Compare your resume with one job. See which matched skills your projects actually prove.",
     "views/analyzer_page.py"),
    ("2", "Skill gaps",
     "Compare against several jobs at once and find the gaps that come up most.",
     "views/skill_gaps_page.py"),
    ("3", "Job tracker",
     "Keep every application, match score, and note on one board.",
     "views/tracker_page.py"),
    ("4", "Learning roadmap",
     "Turn your biggest gaps into projects you can add to your resume.",
     "views/roadmap_page.py"),
    ("Optional", "AI coach",
     "Fact-checked bullet rewrites, interview questions, and a plain-language fit summary. "
     "Runs on your computer with Ollama.",
     "views/ai_coach_page.py"),
]

# A tiny resume that shows the three marks the whole app uses.
SHEET = (
    '<div class="sheet">'
    '<div class="sheet-h">Skills</div>'
    f'<div>Python, SQL, {ui.chip("Docker", "unproven")}</div>'
    '<div class="sheet-h">Projects</div>'
    f'<div>Built a {ui.chip("FastAPI", "matched")} service handling 2,000 requests a day '
    "and cut latency by 35%.</div>"
    '<div class="sheet-ask"><span class="sheet-ask-label">The job asks for</span>'
    f'{ui.chip("FastAPI", "matched")}{ui.chip("Docker", "unproven")}{ui.chip("Kubernetes", "missing")}'
    "</div>"
    f"{ui.legend()}"
    "</div>"
)

left, right = st.columns([6, 5], gap="large", vertical_alignment="center")
with left:
    st.markdown(
        '<div class="home-title">See which skills your resume actually proves.</div>'
        '<p class="home-sub">Add your resume and a job description. SkillMatch marks each skill '
        "as proven by a project, only listed, or missing, then helps you close the gaps.</p>",
        unsafe_allow_html=True,
    )
    if st.button("Analyze a resume", type="primary"):
        st.switch_page("views/analyzer_page.py")
with right:
    st.markdown(SHEET, unsafe_allow_html=True)

st.write("")
counts = tracker.status_counts()
st.markdown(
    ui.stat_row([
        ("Resume", "Loaded" if st.session_state.get("resume_text") else "Not loaded"),
        ("Jobs compared", len(st.session_state.get("gap_jobs", {}))),
        ("Applications tracked", sum(counts.values())),
    ]),
    unsafe_allow_html=True,
)

st.subheader("How to use it")
for number, title, description, path in STEPS:
    text_col, link_col = st.columns([9, 2], vertical_alignment="center")
    badge = (
        f'<div class="flow-num">{number}</div>' if number.isdigit()
        else f'<div class="flow-opt">{number}</div>'
    )
    text_col.markdown(
        f'<div class="flow">{badge}<div><div class="flow-title">{ui.esc(title)}</div>'
        f'<div class="flow-desc">{ui.esc(description)}</div></div></div>',
        unsafe_allow_html=True,
    )
    link_col.page_link(path, label=f"Open {title.lower()}")

st.caption(
    "Your resume is processed in memory and is never saved. Only the applications you choose "
    "to track are stored, on your computer."
)
