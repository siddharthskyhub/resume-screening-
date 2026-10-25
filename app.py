import importlib
import streamlit as st

import ui

importlib.reload(ui)

st.set_page_config(
    page_title="SkillMatch AI · Evidence-Based Resume Matching",
    page_icon=":material/track_changes:",
    layout="wide",
    initial_sidebar_state="expanded",
)
ui.inject_css()

pages = {
    "Overview": [
        st.Page("views/home_page.py", title="Home", icon=":material/home:", default=True),
    ],
    "Core Audit": [
        st.Page("views/analyzer_page.py", title="Resume Analyzer", icon=":material/find_in_page:", url_path="analyzer"),
        st.Page("views/ats_checker_page.py", title="ATS Checker", icon=":material/verified_user:", url_path="ats-checker"),
        st.Page("views/skill_gaps_page.py", title="Skill Gaps", icon=":material/explore:", url_path="skill-gaps"),
    ],
    "Career Strategy": [
        st.Page("views/tracker_page.py", title="Job Tracker", icon=":material/assignment:", url_path="tracker"),
        st.Page("views/roadmap_page.py", title="Learning Roadmap", icon=":material/map:", url_path="roadmap"),
        st.Page("views/ai_coach_page.py", title="AI Coach", icon=":material/science:", url_path="ai-coach"),
    ],
}
navigation = st.navigation(pages, position="top")

with st.sidebar:
    st.markdown(
        '<div class="brand-container">'
        '<div class="brand-header">'
        f'<div class="brand-logo-wrap">{ui.brand_logo(42)}</div>'
        '<div>'
        '<div class="brand-title-row">'
        '<span class="brand-text">SkillMatch</span>'
        '<span class="brand-pill-ai">AI PRO</span>'
        '</div>'
        '<div class="brand-sub">Career &amp; Skill Intelligence</div>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown(
        '<div style="font-size:0.72rem; font-weight:800; letter-spacing:0.08em; text-transform:uppercase; color:var(--muted); margin:4px 0 6px;">'
        f'<span class="inline-icon-wrap" style="margin-right:5px;">{ui.icon("compass", size=13, color="var(--primary)")}</span>FEATURE NAVIGATOR'
        '</div>',
        unsafe_allow_html=True,
    )
    feature_options = [
        "Overview: Home",
        "Core Audit: Resume Analyzer",
        "Core Audit: ATS Checker",
        "Core Audit: Skill Gaps",
        "Career Strategy: Job Tracker",
        "Career Strategy: Learning Roadmap",
        "Career Strategy: AI Coach",
    ]
    current_title = getattr(navigation, "title", "Home")
    default_idx = 0
    for idx, opt in enumerate(feature_options):
        if current_title in opt:
            default_idx = idx
            break

    selected_feature = st.selectbox(
        "Navigate Feature",
        options=feature_options,
        index=default_idx,
        key="sb_nav_jump",
        label_visibility="collapsed",
    )
    if selected_feature != feature_options[default_idx]:
        route_map = {
            "Overview: Home": "views/home_page.py",
            "Core Audit: Resume Analyzer": "views/analyzer_page.py",
            "Core Audit: ATS Checker": "views/ats_checker_page.py",
            "Core Audit: Skill Gaps": "views/skill_gaps_page.py",
            "Career Strategy: Job Tracker": "views/tracker_page.py",
            "Career Strategy: Learning Roadmap": "views/roadmap_page.py",
            "Career Strategy: AI Coach": "views/ai_coach_page.py",
        }
        st.switch_page(route_map[selected_feature])

    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

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
    '<span>SkillMatch AI · Evidence-Based Resume & Skill Gap Optimization</span>'
    '<span>Portfolio Project by Siddharth Kumar</span>'
    '</div>',
    unsafe_allow_html=True,
)
