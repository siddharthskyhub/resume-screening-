import math

import streamlit as st

import ui
from gaps import analyze_jobs
from roadmap import build_roadmap, roadmap_markdown

KIND_BADGES = {
    "learn": ("var(--blue-bg)", "var(--blue-text)", "var(--blue-border)", "📚 Learn Skill"),
    "prove": ("var(--green-bg)", "var(--green-text)", "var(--green-border)", "🛠️ Prove with Project"),
    "prerequisite": ("var(--purple-bg)", "var(--purple-text)", "var(--purple-border)", "⚡ Prerequisite"),
}

ui.hero(
    "Learning Roadmap",
    "A step-by-step project plan that transforms your highest-impact skill gaps into demonstrable portfolio projects and resume bullets.",
    badge="Step 5 · Action Plan",
)

resume_text = st.session_state.get("resume_text")
jobs = st.session_state.get("gap_jobs", {})

if not resume_text or not jobs:
    st.info("The personalized roadmap requires both your resume and target jobs. Add them on the Skill Gaps page first.")
    st.page_link("views/skill_gaps_page.py", label="🧭 Navigate to Skill Gaps", use_container_width=True)
    st.stop()

analysis = analyze_jobs(resume_text, jobs)
if not analysis["gaps"]:
    st.success("🎉 You have no gaps to close: your resume already demonstrates every skill these target jobs require.")
    st.stop()

with st.container(border=True):
    st.markdown("##### ⚙️ Plan Customization")
    c1, c2, c3 = st.columns(3)
    with c1:
        hours_per_week = ui.persistent(st.slider, "Study hours available per week", "roadmap_hours", 8, 2, 40)
    with c2:
        max_skills = ui.persistent(st.slider, "Number of priority gaps to tackle", "roadmap_max_skills", 6, 1, 15)
    with c3:
        st.write("")
        include_proofs = ui.persistent(
            st.checkbox, "Include unproven listed skills", "roadmap_include_proofs", True,
            help="Also includes skills you currently list in skills section without project proof.",
        )

items = build_roadmap(
    analysis["gaps"], have=set(analysis["resume_skills"]),
    hours_per_week=hours_per_week, max_skills=max_skills, include_proofs=include_proofs,
)
if not items:
    st.info("No roadmap items generated with current settings. Try enabling 'Include unproven listed skills'.")
    st.stop()

total_hours = sum(i["hours"] for i in items)
est_weeks = math.ceil(total_hours / hours_per_week)

st.markdown(
    ui.stat_row([
        ("Roadmap Steps", len(items)),
        ("Total Estimated Effort", f"~{total_hours} hrs"),
        ("Estimated Timeline", f"{est_weeks} weeks @ {hours_per_week}h/wk"),
    ]),
    unsafe_allow_html=True,
)
st.caption("ℹ️ Estimates reflect the time needed to build a demonstrable, real-world portfolio project, not theoretical mastery.")

progress_bar = st.empty()
done_count = 0

for item in items:
    weeks_text = (
        f"Week {item['start_week']}"
        if item["start_week"] == item["end_week"]
        else f"Weeks {item['start_week']}–{item['end_week']}"
    )
    bg, fg, border, label = KIND_BADGES.get(
        item["kind"], ("var(--canvas)", "var(--muted)", "var(--line)", item["kind"].title())
    )

    with st.container(border=True):
        col_top1, col_top2 = st.columns([8, 4], vertical_alignment="center")
        with col_top1:
            is_done = ui.persistent(
                st.checkbox,
                f"**Step {item['order']}: {item['skill']}**",
                f"done_{item['skill']}", False,
            )
            done_count += bool(is_done)
        with col_top2:
            st.markdown(
                f'<div style="text-align:right;">'
                f'<span style="background:{bg}; color:{fg}; border:1px solid {border}; padding:3px 9px; border-radius:9999px; font-size:0.75rem; font-weight:700;">{label}</span> '
                f'<span style="background:var(--canvas); border:1px solid var(--line); padding:3px 9px; border-radius:9999px; font-size:0.75rem; font-weight:600; color:var(--muted);">{weeks_text} · ~{item["hours"]}h</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.caption(f"🎯 **Why this skill**: {item['reason']}")

        st.markdown(
            f'<div style="background:var(--primary-light); border-left:3px solid var(--primary); padding:10px 14px; border-radius:6px; margin:8px 0 12px; font-size:0.92rem;">'
            f'<b>Portfolio Project Challenge:</b><br>{ui.esc(item["project"])}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**Tailored Resume Bullet Template** (fill in bracketed placeholders with actual metrics):")
        st.code(item["bullet"], language=None)

pct_done = done_count / len(items)
progress_bar.progress(pct_done, text=f"Roadmap Progress: {done_count} of {len(items)} steps completed ({int(pct_done * 100)}%)")

if done_count == len(items):
    st.balloons()
    st.success("🎉 Amazing! You have completed every milestone in your learning roadmap!")

st.write("")
st.download_button(
    "📥 Download Roadmap as Markdown (MD)",
    data=roadmap_markdown(items, hours_per_week),
    file_name="skillmatch_learning_roadmap.md",
    mime="text/markdown",
    use_container_width=True,
)
