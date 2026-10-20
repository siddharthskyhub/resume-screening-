import streamlit as st

import ui

st.set_page_config(
    page_title="SkillMatch AI · Evidence-Based Resume Matching",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)
ui.inject_css()

pages = [
    st.Page("views/home_page.py", title="Home", icon="🏠", default=True),
    st.Page("views/analyzer_page.py", title="Resume Analyzer", icon="🎯", url_path="analyzer"),
    st.Page("views/ats_checker_page.py", title="ATS Checker", icon="✅", url_path="ats-checker"),
    st.Page("views/skill_gaps_page.py", title="Skill Gaps", icon="🧭", url_path="skill-gaps"),
    st.Page("views/tracker_page.py", title="Job Tracker", icon="📋", url_path="tracker"),
    st.Page("views/roadmap_page.py", title="Learning Roadmap", icon="🗺️", url_path="roadmap"),
    st.Page("views/ai_coach_page.py", title="AI Coach", icon="🤖", url_path="ai-coach"),
]
navigation = st.navigation(pages)

with st.sidebar:
    st.markdown(
        '<div class="brand-container">'
        '<div class="brand-header">'
        '<div class="brand-logo">🎯</div>'
        '<div>'
        '<div class="brand-text">SkillMatch AI</div>'
        '<div class="brand-sub">Career & Skill Analytics Platform</div>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    resume_name = st.session_state.get("resume_name")
    resume_text = st.session_state.get("resume_text")
    if resume_text:
        words = len(resume_text.split())
        st.markdown(
            f'<div class="sidebar-status-card">'
            f'<div class="status-indicator active"></div>'
            f'<div class="sidebar-status-info">'
            f'<div class="sidebar-status-title">{ui.esc(resume_name)}</div>'
            f'<div class="sidebar-status-sub">{words:,} words active in memory</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="sidebar-status-card">'
            '<div class="status-indicator idle"></div>'
            '<div class="sidebar-status-info">'
            '<div class="sidebar-status-title">No resume loaded</div>'
            '<div class="sidebar-status-sub">Upload or use 1-click sample</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.caption("🔒 Resumes are parsed in private session memory and never saved to databases.")
    st.caption("✨ Portfolio Project by Siddharth Kumar")

navigation.run()

st.divider()
st.markdown(
    '<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; font-size:0.86rem; color:var(--muted);">'
    '<span>SkillMatch AI · Evidence-Based Resume & Skill Gap Optimization</span>'
    '<span>Portfolio Project by Siddharth Kumar</span>'
    '</div>',
    unsafe_allow_html=True,
)
