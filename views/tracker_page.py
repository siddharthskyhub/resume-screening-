import streamlit as st

import tracker
import ui
from analyzer import analyze_resume
from tracker import STATUSES

ui.hero(
    "Job tracker",
    "Keep every application in one place, with the match score and skill gaps saved alongside it.",
)

flash = st.session_state.pop("_flash", None)
if flash:
    st.success(flash)

apps = tracker.list_applications()
resume_text = st.session_state.get("resume_text")


def move_app(app_id: int) -> None:
    tracker.update_application(app_id, status=st.session_state[f"status_{app_id}"])


def render_card(app: dict) -> None:
    app_id = app["id"]
    with st.container(border=True):
        st.markdown(f"**{ui.md_escape(app['company'])}**  \n{ui.md_escape(app['role'])}")
        if app["score"] is not None:
            evidence = f" · evidence {app['evidence_score']}%" if app["evidence_score"] is not None else ""
            st.caption(f"Match {app['score']}%{evidence}")
        if app["applied_date"]:
            st.caption(f"Applied {app['applied_date']}")

        st.selectbox(
            "Move to", STATUSES, index=STATUSES.index(app["status"]),
            key=f"status_{app_id}", on_change=move_app, args=(app_id,),
            label_visibility="collapsed",
        )

        with st.expander("Details"):
            if app["url"].startswith(("http://", "https://")):
                st.markdown(f"[Open job posting]({app['url']})")
            if app["missing"]:
                st.caption("Skills to review: " + ", ".join(app["missing"]))

            notes = st.text_area("Notes", value=app["notes"], key=f"notes_{app_id}", height=90)
            if st.button("Save notes", key=f"save_notes_{app_id}"):
                tracker.update_application(app_id, notes=notes)
                st.rerun()

            if st.session_state.get(f"confirm_{app_id}"):
                st.warning("Delete this application?")
                if st.button("Yes, delete", key=f"yes_{app_id}"):
                    tracker.delete_application(app_id)
                    st.session_state.pop(f"confirm_{app_id}", None)
                    st.rerun()
                if st.button("Cancel", key=f"no_{app_id}"):
                    st.session_state.pop(f"confirm_{app_id}", None)
                    st.rerun()
            elif st.button("Delete", key=f"del_{app_id}"):
                st.session_state[f"confirm_{app_id}"] = True
                st.rerun()


with st.expander("Add an application", expanded=not apps):
    with st.form("add_application", clear_on_submit=True):
        c1, c2 = st.columns(2)
        company = c1.text_input("Company")
        role = c2.text_input("Role")
        c3, c4 = st.columns(2)
        url = c3.text_input("Job link (optional)")
        status = c4.selectbox("Status", STATUSES)
        job_description = st.text_area(
            "Job description (optional)", height=140,
            help="Adds a match score if your resume is loaded, and lets you reuse the job on the Skill Gaps page.",
        )
        notes = st.text_area("Notes", height=70)
        submitted = st.form_submit_button("Save application")

    if submitted:
        score = evidence_score = None
        missing: list[str] = []
        if job_description.strip() and resume_text:
            result = analyze_resume(resume_text, job_description)
            score, evidence_score, missing = result["score"], result["evidence_score"], result["missing"]
        try:
            tracker.add_application(
                company, role, url=url, status=status, notes=notes,
                job_description=job_description, score=score,
                evidence_score=evidence_score, missing=missing,
            )
            st.session_state["_flash"] = f"Saved {company.strip()} – {role.strip()}."
            st.rerun()
        except ValueError as error:
            st.error(str(error))

if not apps:
    st.info("No applications yet. Add your first one above.")
    st.stop()

counts = tracker.status_counts()
st.markdown(ui.stat_row([(status, counts[status]) for status in STATUSES]), unsafe_allow_html=True)

insights = tracker.score_insights()
if insights:
    st.info(
        f"Jobs that reached interview or offer averaged a **{insights['advanced_avg']}%** match "
        f"({insights['advanced_n']} jobs), versus **{insights['rejected_avg']}%** for rejected ones "
        f"({insights['rejected_n']} jobs). Small samples, so treat this as a hint, not a rule."
    )

st.divider()
for column, status in zip(st.columns(len(STATUSES)), STATUSES):
    with column:
        in_status = [a for a in apps if a["status"] == status]
        st.markdown(ui.column_head(status, len(in_status)), unsafe_allow_html=True)
        for app in in_status:
            render_card(app)
