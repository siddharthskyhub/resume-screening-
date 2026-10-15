import math

import streamlit as st

import ui
from gaps import analyze_jobs
from roadmap import build_roadmap, roadmap_markdown

KIND_LABEL = {
    "learn": "Learn",
    "prove": "Prove it",
    "prerequisite": "Prerequisite",
}

ui.hero(
    "Learning roadmap",
    "A step-by-step plan that turns your biggest skill gaps into projects you can put on your resume.",
)

resume_text = st.session_state.get("resume_text")
jobs = st.session_state.get("gap_jobs", {})

if not resume_text or not jobs:
    st.info("The roadmap is built from your resume and target jobs. Add them on the Skill Gaps page first.")
    st.page_link("views/skill_gaps_page.py", label="Go to Skill Gaps")
    st.stop()

analysis = analyze_jobs(resume_text, jobs)
if not analysis["gaps"]:
    st.success("No gaps to close: your resume already proves every skill these jobs ask for.")
    st.stop()

c1, c2, c3 = st.columns(3)
with c1:
    hours_per_week = ui.persistent(st.slider, "Hours you can study per week", "roadmap_hours", 8, 2, 40)
with c2:
    max_skills = ui.persistent(st.slider, "Gaps to tackle", "roadmap_max_skills", 6, 1, 15)
with c3:
    include_proofs = ui.persistent(
        st.checkbox, "Include skills I list but haven't proven", "roadmap_include_proofs", True
    )

items = build_roadmap(
    analysis["gaps"], have=set(analysis["resume_skills"]),
    hours_per_week=hours_per_week, max_skills=max_skills, include_proofs=include_proofs,
)
if not items:
    st.info("Nothing to plan with these settings. Try including listed-but-unproven skills.")
    st.stop()

total_hours = sum(i["hours"] for i in items)
st.markdown(
    ui.stat_row([
        ("Steps", len(items)),
        ("Estimated hours", total_hours),
        ("Estimated weeks", math.ceil(total_hours / hours_per_week)),
    ]),
    unsafe_allow_html=True,
)
st.caption("Hour estimates are rough guides for reaching a small, demonstrable project, not mastery.")

progress_bar = st.empty()  # filled after the checkboxes are drawn, so it is never one click behind
done = 0

for item in items:
    weeks = (
        f"Week {item['start_week']}"
        if item["start_week"] == item["end_week"]
        else f"Weeks {item['start_week']}–{item['end_week']}"
    )
    with st.container(border=True):
        is_done = ui.persistent(
            st.checkbox,
            f"**{item['order']}. {item['skill']}**  ·  {KIND_LABEL[item['kind']]}  ·  {weeks}  ·  ~{item['hours']} h",
            f"done_{item['skill']}", False,
        )
        done += bool(is_done)
        st.caption(item["reason"])
        st.markdown(f"**Project:** {item['project']}")
        st.markdown("**Resume bullet template** (fill in only what is true):")
        st.code(item["bullet"], language=None)

progress_bar.progress(done / len(items), text=f"{done} of {len(items)} steps complete")

st.download_button(
    "Download roadmap (Markdown)",
    data=roadmap_markdown(items, hours_per_week),
    file_name="skillmatch_roadmap.md",
    mime="text/markdown",
)
