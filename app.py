import streamlit as st

import ui

st.set_page_config(page_title="SkillMatch AI", page_icon="🎯", layout="wide")
ui.inject_css()

pages = [
    st.Page("views/home_page.py", title="Home", icon="🏠", default=True),
    st.Page("views/analyzer_page.py", title="Resume Analyzer", icon="🎯", url_path="analyzer"),
    st.Page("views/skill_gaps_page.py", title="Skill Gaps", icon="🧭", url_path="skill-gaps"),
    st.Page("views/tracker_page.py", title="Job Tracker", icon="📋", url_path="tracker"),
    st.Page("views/roadmap_page.py", title="Learning Roadmap", icon="🗺️", url_path="roadmap"),
    st.Page("views/ai_coach_page.py", title="AI Coach", icon="🤖", url_path="ai-coach"),
]
navigation = st.navigation(pages)

with st.sidebar:
    st.divider()
    st.markdown(
        '<div class="brand">SkillMatch AI</div>'
        '<div class="brand-sub">Analyze, compare, track, and plan your job search.</div>',
        unsafe_allow_html=True,
    )
    resume_name = st.session_state.get("resume_name")
    st.caption(f"Resume loaded: {resume_name}" if resume_name else "No resume loaded yet.")
    st.caption("Your resume is processed in memory and is not stored.")
    st.caption("Version 2.2")

navigation.run()

st.divider()
st.caption("SkillMatch AI, a portfolio project by Siddharth Kumar")
