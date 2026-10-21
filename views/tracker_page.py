import streamlit as st

import tracker
import ui
from analyzer import analyze_resume
from tracker import STATUSES

ui.hero(
    "Job Application Tracker",
    "Keep every application in one place, with match scores and skill gaps tracked directly alongside.",
    badge="Step 4 · Pipeline Management",
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
        st.markdown(
            f'<div style="font-weight:800; font-size:1.05rem; color:var(--ink);">{ui.esc(app["company"])}</div>'
            f'<div style="color:var(--muted); font-size:0.9rem; font-weight:600; margin-bottom:6px;">{ui.esc(app["role"])}</div>',
            unsafe_allow_html=True,
        )

        if app["score"] is not None:
            score = app["score"]
            ev_score = app.get("evidence_score")
            score_color = "var(--green-text)" if score >= 70 else ("var(--blue-text)" if score >= 50 else "var(--yellow-text)")
            score_bg = "var(--green-bg)" if score >= 70 else ("var(--blue-bg)" if score >= 50 else "var(--yellow-bg)")
            score_border = "var(--green-border)" if score >= 70 else ("var(--blue-border)" if score >= 50 else "var(--yellow-border)")

            ev_html = f" · Ev: <b>{ev_score}%</b>" if ev_score is not None else ""
            st.markdown(
                f'<div style="display:inline-flex; align-items:center; background:{score_bg}; color:{score_color}; border:1px solid {score_border}; padding:2px 9px; border-radius:9999px; font-size:0.78rem; font-weight:700; margin-bottom:8px;">'
                f'Match: {score}%{ev_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

        if app["applied_date"]:
            st.markdown(
                f'<div style="font-size:0.78rem; color:var(--muted); display:flex; align-items:center; gap:4px; margin-bottom:6px;">'
                f'<span class="inline-icon-wrap">{ui.icon("calendar", size=12, color="var(--muted)")}</span> Applied {app["applied_date"]}'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.selectbox(
            "Move to", STATUSES, index=STATUSES.index(app["status"]),
            key=f"status_{app_id}", on_change=move_app, args=(app_id,),
            label_visibility="collapsed",
        )

        with st.expander("Details & Notes"):
            if app["url"] and app["url"].startswith(("http://", "https://")):
                st.markdown(
                    f'<div style="margin-bottom:6px;">'
                    f'<a href="{app["url"]}" target="_blank" style="display:inline-flex; align-items:center; gap:4px; font-size:0.86rem; color:var(--primary); font-weight:600; text-decoration:none;">'
                    f'{ui.icon("external-link", size=13, color="var(--primary)")} Open Original Job Posting'
                    f'</a></div>',
                    unsafe_allow_html=True,
                )
            if app["missing"]:
                missing_chips = " ".join([ui.chip(m, "missing") for m in app["missing"][:6]])
                st.markdown(
                    f'<div style="margin:4px 0 8px;"><b style="font-size:0.8rem; color:var(--muted);">GAPS:</b><br>{missing_chips}</div>',
                    unsafe_allow_html=True,
                )

            notes = st.text_area("Notes", value=app["notes"], key=f"notes_{app_id}", height=80, placeholder="Interview notes, contacts, deadlines...")
            if st.button("Save Notes", key=f"save_notes_{app_id}", use_container_width=True):
                tracker.update_application(app_id, notes=notes)
                st.rerun()

            st.write("")
            if st.session_state.get(f"confirm_{app_id}"):
                st.warning("Confirm application deletion?")
                c_del_yes, c_del_no = st.columns(2)
                if c_del_yes.button("Yes, delete", key=f"yes_{app_id}", type="primary", use_container_width=True):
                    tracker.delete_application(app_id)
                    st.session_state.pop(f"confirm_{app_id}", None)
                    st.rerun()
                if c_del_no.button("Cancel", key=f"no_{app_id}", use_container_width=True):
                    st.session_state.pop(f"confirm_{app_id}", None)
                    st.rerun()
            elif st.button("Delete", icon=":material/delete:", key=f"del_{app_id}", use_container_width=True):
                st.session_state[f"confirm_{app_id}"] = True
                st.rerun()


with st.expander("Track a New Application", expanded=not apps):
    with st.form("add_application", clear_on_submit=True):
        c1, c2 = st.columns(2)
        company = c1.text_input("Company Name *", placeholder="e.g. Acme Corp")
        role = c2.text_input("Role / Job Title *", placeholder="e.g. Backend Engineer")
        c3, c4 = st.columns(2)
        url = c3.text_input("Job Link (optional)", placeholder="https://...")
        status = c4.selectbox("Status", STATUSES)
        job_description = st.text_area(
            "Job description (optional)", height=130,
            help="Adds a match score if your resume is loaded, and lets you reuse the job on the Skill Gaps page.",
            placeholder="Paste job description requirements here...",
        )
        notes = st.text_area("Initial Notes (optional)", height=70, placeholder="Interview notes, contacts...")
        submitted = st.form_submit_button("Save Application to Tracker", icon=":material/bookmark_add:", use_container_width=True)

    if submitted:
        if not company.strip() or not role.strip():
            st.error("Please provide at least a Company name and Role.")
        else:
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
                st.session_state["_flash"] = f"Successfully added {company.strip()} – {role.strip()} to your tracker."
                st.rerun()
            except ValueError as error:
                st.error(str(error))

if not apps:
    st.info("No applications yet. Add your first one above or save one directly from the Analyzer page.", icon=":material/info:")
    st.stop()

# Status overview stats
counts = tracker.status_counts()
st.markdown(ui.stat_row([(status, counts[status]) for status in STATUSES]), unsafe_allow_html=True)

insights = tracker.score_insights()
if insights:
    st.markdown(
        f'<div style="background:var(--primary-light); border:1px solid var(--primary-border); border-radius:10px; padding:12px 18px; margin-bottom:16px; color:var(--ink); font-size:0.92rem; display:flex; align-items:flex-start; gap:10px;">'
        f'<span class="inline-icon-wrap" style="color:var(--primary); margin-top:2px;">{ui.icon("trending-up", size=18, color="var(--primary)")}</span>'
        f'<div><b>Match Score Insight:</b> Applications reaching interview/offer stages averaged a <b>{insights["advanced_avg"]}%</b> match '
        f'({insights["advanced_n"]} applications), compared to <b>{insights["rejected_avg"]}%</b> for rejected applications '
        f'({insights["rejected_n"]} applications).</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.divider()

# Responsive View Selector (Board vs Stage Tabs)
view_mode = st.radio(
    "Tracker View Layout",
    ["Kanban Board (Desktop)", "Stage Tabs (Mobile & Tablet Friendly)"],
    horizontal=True,
    label_visibility="collapsed",
)

if view_mode.startswith("Kanban"):
    # Multi-column Kanban Board layout
    cols = st.columns(len(STATUSES))
    for column, status in zip(cols, STATUSES):
        with column:
            in_status = [a for a in apps if a["status"] == status]
            st.markdown(ui.column_head(status, len(in_status)), unsafe_allow_html=True)
            if not in_status:
                st.markdown(
                    '<div style="color:var(--muted); font-size:0.82rem; text-align:center; padding:18px 0; border:1px dashed var(--line); border-radius:8px;">No applications</div>',
                    unsafe_allow_html=True,
                )
            for app in in_status:
                render_card(app)
else:
    # Responsive Tabbed View (Clean & spacious on mobile/tablets)
    tab_labels = [f"{status} ({counts[status]})" for status in STATUSES]
    tabs = st.tabs(tab_labels)
    for tab, status in zip(tabs, STATUSES):
        with tab:
            in_status = [a for a in apps if a["status"] == status]
            st.markdown(f"#### {status} Applications ({len(in_status)})")
            if not in_status:
                st.info(f"No applications currently in '{status}' stage.")
            else:
                card_cols = st.columns(min(len(in_status), 2)) if len(in_status) > 1 else [st.container()]
                for idx, app in enumerate(in_status):
                    col = card_cols[idx % len(card_cols)]
                    with col:
                        render_card(app)
