import importlib
import streamlit as st

import ui

importlib.reload(ui)

st.set_page_config(
    page_title="ResuMate AI · Precision Resume & Career Intelligence",
    page_icon=":material/track_changes:",
    layout="wide",
    initial_sidebar_state="expanded",
)
ui.inject_css()

pages = {
    "OVERVIEW": [
        st.Page("views/home_page.py", title="Home", icon=":material/home:", default=True),
    ],
    "CORE AUDIT": [
        st.Page("views/analyzer_page.py", title="Resume Analyzer", icon=":material/find_in_page:", url_path="analyzer"),
        st.Page("views/ats_checker_page.py", title="ATS Checker", icon=":material/verified_user:", url_path="ats-checker"),
        st.Page("views/skill_gaps_page.py", title="Skill Gaps", icon=":material/explore:", url_path="skill-gaps"),
    ],
    "CAREER STRATEGY": [
        st.Page("views/tracker_page.py", title="Job Tracker", icon=":material/assignment:", url_path="tracker"),
        st.Page("views/roadmap_page.py", title="Learning Roadmap", icon=":material/map:", url_path="roadmap"),
        st.Page("views/ai_coach_page.py", title="AI Coach", icon=":material/science:", url_path="ai-coach"),
    ],
}
navigation = st.navigation(pages)

with st.sidebar:
    st.markdown(
        '<div class="brand-container">'
        '<div class="brand-header">'
        f'<div class="brand-logo-wrap">{ui.brand_logo(42)}</div>'
        '<div>'
        '<div class="brand-title-row">'
        '<span class="brand-text">ResuMate</span>'
        '<span class="brand-pill-ai">AI PRO</span>'
        '</div>'
        '<div class="brand-sub">Career &amp; Resume Intelligence</div>'
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
            '<div class="sidebar-status-title">No Resume Loaded</div>'
            '<div class="sidebar-status-sub">Ready for 1-click sample</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Load 1-Click Sample", icon=":material/auto_awesome:", key="sb_btn_sample", use_container_width=True):
            ui.load_sample_data()
            st.rerun()

    st.markdown(
        '<div class="sidebar-tip-card">'
        '<div class="sidebar-tip-head">'
        f'<span class="inline-icon-wrap">{ui.icon("lightbulb", size=14, color="#4338ca")}</span><b>ATS INSIDER TIP</b>'
        '</div>'
        '<div class="sidebar-tip-body">'
        'Applicant Tracking Systems favor single-column layouts and quantifiable project achievements.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-health-bar">'
        f'<span class="inline-icon-wrap" style="margin-right:2px;">{ui.icon("shield-check", size=13, color="#10b981")}</span>'
        '<span>Privacy Engine: 100% Client-Side</span>'
        '</div>',
        unsafe_allow_html=True,
    )

navigation.run()

st.divider()
st.markdown(
    '<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; font-size:0.86rem; color:var(--muted);">'
    '<span>ResuMate AI · Evidence-Based Resume & Career Intelligence</span>'
    '<span>Portfolio Project by Siddharth Kumar</span>'
    '</div>',
    unsafe_allow_html=True,
)
