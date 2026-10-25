import streamlit as st

import tracker
import ui
from analyzer import analyze_resume, build_report

EVIDENCE_LABEL = {
    "strong": ("matched", "Strong evidence: proven in a project or job bullet with a quantifiable outcome"),
    "demonstrated": ("matched", "Demonstrated: used in a documented project or experience section"),
    "listed": ("unproven", "Listed only: keyword present with no project proof"),
}


def render_results(result: dict, job_text: str) -> None:
    st.divider()
    st.markdown("### Analysis Results & Evidence Breakdown")

    job = result["job"]
    if not job:
        st.warning("No supported technical skills were detected in the target job description.", icon=":material/warning:")
    else:
        st.markdown(ui.proof_bar(result), unsafe_allow_html=True)
        st.markdown(ui.legend(), unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.84rem; color:var(--muted); margin:8px 0 14px; display:flex; align-items:flex-start; gap:6px;">'
            f'<span class="inline-icon-wrap" style="flex-shrink:0; margin-top:2px;">{ui.icon("lightbulb", size=14, color="var(--primary)")}</span>'
            f'<span>Keyword match scores count every detected skill equally. Evidence-backed match evaluates '
            f'whether you have demonstrated projects/results (skills without proof count at half weight, and required skills carry double weight).</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        left, right = st.columns(2)
        with left:
            badges = [
                (s, "unproven" if s in result["unproven"] else "matched")
                for s in result["matched"]
            ]
            st.markdown(
                ui.skill_card(
                    "Matching Skills",
                    "Skills present in both your resume and the job posting. Green indicates project evidence.",
                    badges,
                ),
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                ui.skill_card(
                    "Skills to Review & Add",
                    "Skills requested by the employer that were not identified on your resume.",
                    [(s, "missing" if job[s]["level"] == "required" else "preferred")
                     for s in result["missing"]],
                ),
                unsafe_allow_html=True,
            )

        if result["matched"]:
            with st.expander("Inspect project evidence behind each matching skill", expanded=False):
                for skill in result["matched"]:
                    entry = result["evidence"].get(skill, {"level": "listed", "snippets": []})
                    css, label = EVIDENCE_LABEL.get(entry["level"], ("unproven", "Listed only"))
                    st.markdown(
                        f'<div style="margin:10px 0 6px;">'
                        f'{ui.chip(skill, css)} '
                        f'<span style="font-size:0.86rem; color:var(--muted); font-weight:500;">{ui.esc(label)}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if entry["snippets"]:
                        for snippet in entry["snippets"]:
                            st.markdown(
                                f'<div style="background:var(--canvas); border-left:3px solid var(--primary); padding:6px 12px; margin-bottom:6px; border-radius:4px; font-size:0.88rem; color:var(--ink-light);">'
                                f'"{ui.esc(snippet["text"])}"'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.caption("No specific project bullets found mentioning this skill directly.")

        if result["extra"]:
            st.markdown(
                ui.skill_card(
                    "Additional Resume Strengths",
                    "Strong skills identified on your resume that were not explicitly listed in this job post.",
                    [(s, "extra") for s in result["extra"]],
                ),
                unsafe_allow_html=True,
            )

        if result["by_category"]:
            st.markdown("### Match by Category")
            cols = st.columns(min(len(result["by_category"]), 3))
            col_idx = 0
            for category, (hits, total) in result["by_category"].items():
                pct = int(100 * hits / total) if total else 0
                with cols[col_idx % len(cols)]:
                    with st.container(border=True):
                        st.markdown(f"**{category}**")
                        st.markdown(
                            f"<span style='font-size:1.4rem; font-weight:800; color:var(--primary);'>{pct}%</span> "
                            f"<span style='font-size:0.85rem; color:var(--muted);'>({hits}/{total} skills)</span>",
                            unsafe_allow_html=True,
                        )
                        st.progress(hits / total)
                col_idx += 1

    st.markdown("### Tailoring Suggestions")
    suggestions = result["suggestions"] + result["proof_suggestions"]
    if suggestions:
        for skill, tip in suggestions:
            st.markdown(
                f'<div style="background:var(--card-bg); border:1px solid var(--line); border-radius:8px; padding:10px 14px; margin-bottom:8px; display:flex; gap:10px; align-items:flex-start;">'
                f'<span class="inline-icon-wrap" style="color:var(--primary); flex-shrink:0; margin-top:2px;">{ui.icon("lightbulb", size=16, color="var(--primary)")}</span>'
                f'<div><b>{ui.esc(skill)}</b>: <span style="color:var(--ink-light); font-size:0.92rem;">{ui.esc(tip)}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    elif job:
        st.success("Outstanding! Every detected skill is on your resume and backed by verifiable project evidence.", icon=":material/verified:")

    st.markdown("### Resume Format & Health Check")
    for check in result["checks"]:
        chip_html = ui.chip("Pass", "matched") if check["ok"] else ui.chip("Review", "unproven")
        st.markdown(
            f'<div style="background:var(--card-bg); border:1px solid var(--line); border-radius:8px; padding:10px 14px; margin-bottom:8px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;">'
            f'<div style="display:flex; align-items:center; gap:8px;">{chip_html} <b>{ui.esc(check["label"])}</b></div>'
            f'<span style="color:var(--muted); font-size:0.88rem;">{ui.esc(check["detail"])}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.page_link("views/ats_checker_page.py", label="Run full ATS Friendly Resume Audit →")

    st.write("")
    c_dl, _ = st.columns([1, 1])
    with c_dl:
        st.download_button(
            "Download full analysis report (TXT)",
            icon=":material/download:",
            data=build_report(result),
            file_name="skillmatch_analysis.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if job:
        with st.expander("Save this job application to your Job Tracker"):
            with st.form("save_to_tracker", clear_on_submit=True):
                c1, c2 = st.columns(2)
                company = c1.text_input("Company Name", placeholder="e.g. Google, Stripe")
                role = c2.text_input("Job Title / Role", placeholder="e.g. Senior Software Engineer")
                url = st.text_input("Job Posting Link (optional)", placeholder="https://...")
                if st.form_submit_button("Save Application", icon=":material/bookmark_add:", use_container_width=True):
                    try:
                        tracker.add_application(
                            company, role, url=url, job_description=job_text,
                            score=result["score"], evidence_score=result["evidence_score"],
                            missing=result["missing"],
                        )
                        st.success("Application saved successfully! View and track it on the Job Tracker page.")
                    except ValueError as error:
                        st.error(str(error))

    with st.expander("View parsed resume text in memory"):
        st.text(result["resume_text"][:10000])


ui.hero(
    "Resume Analyzer",
    "Compare your resume with a target job. Uncover which skills your projects prove, which are only listed, and which are missing.",
    badge="Step 1 · Single Job Comparison",
)

left_input, right_input = st.columns(2, gap="medium")
with left_input:
    st.markdown("#### 1. Your Resume")
    resume_text = ui.resume_loader()

with right_input:
    c_job_title, c_job_sample = st.columns([1, 1], vertical_alignment="center")
    with c_job_title:
        st.markdown("#### 2. Target Job Description")
    with c_job_sample:
        if st.button("Load sample job (1-click)", icon=":material/work:", key="btn_sample_job_analyzer"):
            ui.load_sample_job()

    job_description = ui.persistent(
        st.text_area, "Job description", "job_text_input", "",
        placeholder=(
            "Paste the job requirements here...\n\n"
            "Tip: keep headings like 'Requirements' and 'Nice to have' "
            "so skills are weighted correctly."
        ),
        height=240,
        label_visibility="collapsed",
    )

if st.button("Analyze Resume Match", icon=":material/bolt:", type="primary", use_container_width=True):
    if not resume_text:
        st.error("Upload your resume or paste its text first.")
    elif not job_description.strip():
        st.error("Paste a job description first.")
    else:
        with st.spinner("Analyzing skills, evidence, and requirements..."):
            st.session_state["result"] = analyze_resume(resume_text, job_description)
            st.session_state["analysis_job_text"] = job_description

# Render from session state so results survive reruns (e.g. download clicks).
if "result" in st.session_state:
    render_results(st.session_state["result"], st.session_state.get("analysis_job_text", ""))
