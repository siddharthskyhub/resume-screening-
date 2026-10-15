import streamlit as st

import tracker
import ui
from analyzer import analyze_resume, build_report

EVIDENCE_LABEL = {
    "strong": ("matched", "strong evidence: used in a project or job, with a result"),
    "demonstrated": ("matched", "demonstrated: used in a project or job"),
    "listed": ("unproven", "listed only: no project or job bullet shows it"),
}


def render_results(result: dict, job_text: str) -> None:
    st.divider()
    st.subheader("Your analysis")

    job = result["job"]
    if not job:
        st.warning("No supported technical skills were detected in the job description.")
    else:
        st.markdown(ui.proof_bar(result), unsafe_allow_html=True)
        st.markdown(ui.legend(), unsafe_allow_html=True)
        st.caption(
            "Keyword match counts every skill found. The evidence-backed match counts skills you only "
            "list at half value, and required skills count double. Neither score predicts hiring success."
        )

        left, right = st.columns(2)
        with left:
            badges = [
                (s, "unproven" if s in result["unproven"] else "matched")
                for s in result["matched"]
            ]
            st.markdown(
                ui.skill_card("Matching skills",
                              "Green means your resume proves it. Yellow means you only list it.", badges),
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                ui.skill_card(
                    "Skills to review",
                    "Asked for by the job, not found in your resume. Dotted means nice-to-have.",
                    [(s, "missing" if job[s]["level"] == "required" else "preferred")
                     for s in result["missing"]],
                ),
                unsafe_allow_html=True,
            )

        if result["matched"]:
            with st.expander("See the evidence behind each matching skill"):
                for skill in result["matched"]:
                    entry = result["evidence"].get(skill, {"level": "listed", "snippets": []})
                    css, label = EVIDENCE_LABEL[entry["level"]]
                    st.markdown(
                        f'{ui.chip(skill, css)} <span style="color:var(--muted)">{ui.esc(label)}</span>',
                        unsafe_allow_html=True,
                    )
                    for snippet in entry["snippets"]:
                        st.caption(f"“{snippet['text']}”")

        if result["extra"]:
            st.markdown(
                ui.skill_card("Extra strengths", "On your resume, not mentioned in the job post.",
                              [(s, "extra") for s in result["extra"]]),
                unsafe_allow_html=True,
            )

        if result["by_category"]:
            st.subheader("Match by category")
            for category, (hits, total) in result["by_category"].items():
                st.write(f"**{category}**: {hits} of {total}")
                st.progress(hits / total)

    st.subheader("Suggestions")
    suggestions = result["suggestions"] + result["proof_suggestions"]
    if suggestions:
        for skill, tip in suggestions:
            st.markdown(f"- **{ui.md_escape(skill)}**: {tip}")
    elif job:
        st.markdown("- Every detected skill is on your resume and backed by evidence. Nice work.")

    st.subheader("Resume health check")
    for check in result["checks"]:
        chip = ui.chip("OK", "matched") if check["ok"] else ui.chip("Review", "unproven")
        st.markdown(
            f'<div style="margin:6px 0">{chip} <b>{ui.esc(check["label"])}</b> '
            f'<span style="color:var(--muted)">{ui.esc(check["detail"])}</span></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    st.download_button(
        "Download analysis report",
        data=build_report(result),
        file_name="skillmatch_analysis.txt",
        mime="text/plain",
    )

    if job:
        with st.expander("Save this job to your tracker"):
            with st.form("save_to_tracker", clear_on_submit=True):
                c1, c2 = st.columns(2)
                company = c1.text_input("Company")
                role = c2.text_input("Role")
                url = st.text_input("Job link (optional)")
                if st.form_submit_button("Save to tracker"):
                    try:
                        tracker.add_application(
                            company, role, url=url, job_description=job_text,
                            score=result["score"], evidence_score=result["evidence_score"],
                            missing=result["missing"],
                        )
                        st.success("Saved. Open the Job Tracker page to manage it.")
                    except ValueError as error:
                        st.error(str(error))

    with st.expander("View extracted resume text"):
        st.text(result["resume_text"][:10000])


ui.hero(
    "Resume analyzer",
    "Compare your resume with one job and see which matched skills your projects actually prove.",
)

left_input, right_input = st.columns(2)
with left_input:
    st.subheader("Your resume")
    resume_text = ui.resume_loader()

with right_input:
    st.subheader("Target job")
    job_description = ui.persistent(
        st.text_area, "Job description", "job_text_input", "",
        placeholder=(
            "Paste the job requirements here...\n\n"
            "Tip: keep headings like 'Requirements' and 'Nice to have' "
            "so skills are weighted correctly."
        ),
        height=220,
        label_visibility="collapsed",
    )

if st.button("Analyze resume", type="primary", width="stretch"):
    if not resume_text:
        st.error("Upload your resume or paste its text first.")
    elif not job_description.strip():
        st.error("Paste a job description first.")
    else:
        st.session_state["result"] = analyze_resume(resume_text, job_description)
        st.session_state["analysis_job_text"] = job_description

# Render from session state so results survive reruns (e.g. download clicks).
if "result" in st.session_state:
    render_results(st.session_state["result"], st.session_state.get("analysis_job_text", ""))
