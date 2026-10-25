import streamlit as st

import ui
from ats_checker import build_ats_report, check_ats

ui.hero(
    "ATS Resume Checker",
    "Audit your resume against Applicant Tracking System (ATS) parsers. Verify contact details, standard section headings, action verbs, and formatting hygiene.",
    badge="ATS Audit · Parser Optimization",
)

# ------------------------------- inputs ------------------------------------ #
left_input, right_input = st.columns(2, gap="medium")
with left_input:
    st.markdown("#### 1. Your Resume")
    resume_text = ui.resume_loader()

with right_input:
    c_ats_job_title, c_ats_job_sample = st.columns([1, 1], vertical_alignment="center")
    with c_ats_job_title:
        st.markdown("#### 2. Target Job (Optional)")
    with c_ats_job_sample:
        if st.button("Load sample job (1-click)", icon=":material/work:", key="btn_sample_job_ats"):
            ui.load_sample_job()

    job_text = ui.persistent(
        st.text_area,
        "Job description for keyword alignment",
        "job_text_input",
        "",
        height=180,
        placeholder="Paste an optional job description to check ATS keyword alignment...",
        label_visibility="collapsed",
    )
    st.caption("Optional: Adding a job description enables ATS keyword match analysis.")

if not resume_text:
    st.info("Please upload or paste your resume above to run the ATS compliance audit.", icon=":material/info:")
    st.stop()

# Auto-run or button
st.write("")
col_btn, _ = st.columns([1, 2])
with col_btn:
    run_audit = st.button("Run ATS Compliance Audit", icon=":material/verified_user:", type="primary", use_container_width=True)

if run_audit or "ats_audit_result" not in st.session_state:
    st.session_state["ats_audit_result"] = check_ats(resume_text, job_text)

audit = st.session_state["ats_audit_result"]

st.divider()
st.markdown("### ATS Compatibility Score")

score = audit["score"]
grade = audit["grade"]
rating = audit["rating"]

if score >= 85:
    badge_color = "var(--green-text)"
    badge_bg = "var(--green-bg)"
    badge_border = "var(--green-border)"
elif score >= 70:
    badge_color = "var(--blue-text)"
    badge_bg = "var(--blue-bg)"
    badge_border = "var(--blue-border)"
elif score >= 50:
    badge_color = "var(--yellow-text)"
    badge_bg = "var(--yellow-bg)"
    badge_border = "var(--yellow-border)"
else:
    badge_color = "var(--red-text)"
    badge_bg = "var(--red-bg)"
    badge_border = "var(--red-border)"

# Score banner
c_score, c_summary = st.columns([1, 2], vertical_alignment="center", gap="medium")
with c_score:
    st.markdown(
        f'<div class="ats-score-box" style="background:var(--card-bg); border:1px solid var(--line); border-radius:14px; padding:22px; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.04);">'
        f'<div style="font-size:3.3rem; font-weight:800; font-family:var(--display); line-height:1; color:var(--ink);">{score}<span style="font-size:1.4rem; color:var(--muted); font-weight:500;">/100</span></div>'
        f'<div class="ats-score-pill" style="display:inline-block; margin-top:10px; padding:4px 14px; border-radius:9999px; font-weight:700; font-size:0.88rem; background:{badge_bg}; color:{badge_color}; border:1px solid {badge_border};">'
        f'Grade {grade} · {rating}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with c_summary:
    st.markdown(
        f"**ATS Compatibility Rating: {rating}**  \n"
        f"This score evaluates how accurately automated applicant screening systems (Workday, Greenhouse, Taleo, iCIMS, Ashby) "
        f"can parse your sections, extract contact info, index technical skills, and validate quantifiable achievements."
    )
    st.progress(score / 100)

st.write("")
st.markdown(
    ui.stat_row([
        ("Length", f"{audit['format']['word_count']} words"),
        ("Bullet Points", f"{audit['format']['bullet_count']} items"),
        ("Quantified Impact", f"{audit['format']['quantified_bullets']} bullets"),
        ("Action Verbs", f"{len(audit['verbs']['strong_verbs_unique'])} detected"),
    ]),
    unsafe_allow_html=True,
)

# ----------------------------- Breakdown Tabs ------------------------------ #
tab_checklist, tab_contacts, tab_verbs, tab_alignment = st.tabs(
    ["Compliance Checklist", "Contact & Structure", "Action Verbs & Tone", "Job Keyword Match"]
)

with tab_checklist:
    st.caption("Every check impacts how your resume is categorized and ranked by automated parsers.")
    categories = sorted(list(set(c["category"] for c in audit["checks"])))

    for cat in categories:
        st.markdown(f"**{cat}**")
        cat_checks = [c for c in audit["checks"] if c["category"] == cat]
        for c in cat_checks:
            if c["status"] == "pass":
                icon = f'<span class="inline-icon-wrap" style="color:#10b981; margin-right:8px; display:inline-flex; align-items:center;">{ui.icon("check-circle-2", size=16, color="#10b981")}</span>'
                badge = f'<span style="background:var(--green-bg); color:var(--green-text); border:1px solid var(--green-border); padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:700;">{c["points"]}/{c["max_points"]} pts</span>'
            elif c["status"] == "warning":
                icon = f'<span class="inline-icon-wrap" style="color:#f59e0b; margin-right:8px; display:inline-flex; align-items:center;">{ui.icon("alert-circle", size=16, color="#f59e0b")}</span>'
                badge = f'<span style="background:var(--yellow-bg); color:var(--yellow-text); border:1px solid var(--yellow-border); padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:700;">{c["points"]}/{c["max_points"]} pts</span>'
            else:
                icon = f'<span class="inline-icon-wrap" style="color:#f43f5e; margin-right:8px; display:inline-flex; align-items:center;">{ui.icon("x-circle", size=16, color="#f43f5e")}</span>'
                badge = f'<span style="background:var(--red-bg); color:var(--red-text); border:1px solid var(--red-border); padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:700;">{c["points"]}/{c["max_points"]} pts</span>'

            st.markdown(
                f'<div style="background:var(--card-bg); border:1px solid var(--line); border-radius:8px; padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:8px;">'
                f'<div style="display:flex; align-items:flex-start;">{icon}<div><b>{c["name"]}</b><div style="color:var(--muted); font-size:0.88rem; margin-top:2px;">{c["detail"]}</div></div></div>'
                f'<div>{badge}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.write("")

with tab_contacts:
    col_c1, col_c2 = st.columns(2, gap="medium")
    with col_c1:
        st.markdown("##### Detected Contact Details")
        c = audit["contacts"]
        items = [
            ("Email", c["email"] or "Not found"),
            ("Phone", c["phone"] or "Not found"),
            ("LinkedIn", c["linkedin"] or "Not found"),
            ("GitHub / Portfolio", c["github"] or "Not found"),
            ("Location Indicator", c["location"] or "Not detected"),
        ]
        for label, val in items:
            found = val != "Not found" and val != "Not detected"
            chip_badge = ui.chip("Found", "matched") if found else ui.chip("Missing", "missing")
            st.markdown(
                f'<div style="padding:8px 0; border-bottom:1px solid var(--line); font-size:0.92rem; display:flex; justify-content:space-between; align-items:center;">'
                f'<div><b>{label}:</b> <span style="color:var(--muted);">{val}</span></div>'
                f'{chip_badge}'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_c2:
        st.markdown("##### Standard Section Headers")
        st.caption("ATS parsers search for standard headings to categorize work history, degrees, and skills.")
        sections = audit["detected_sections"]
        standard_keys = ["experience", "skills", "education", "projects", "certifications", "summary"]
        for s in standard_keys:
            is_present = s in sections
            st.markdown(
                f'<div style="padding:8px 0; border-bottom:1px solid var(--line); font-size:0.92rem; display:flex; justify-content:space-between; align-items:center;">'
                f'<span><b>{s.capitalize()} Section:</b></span>'
                f'{ui.chip("Detected", "matched") if is_present else ui.chip("Not Found", "missing")}'
                f'</div>',
                unsafe_allow_html=True,
            )

with tab_verbs:
    v = audit["verbs"]
    st.markdown("##### Strong Action Verbs Detected")
    if v["strong_verbs_unique"]:
        verb_chips = "".join([ui.chip(verb.capitalize(), "matched") for verb in v["strong_verbs_unique"]])
        st.markdown(f'<div style="margin-bottom:14px; display:flex; flex-wrap:wrap; gap:4px;">{verb_chips}</div>', unsafe_allow_html=True)
    else:
        st.caption("No standard strong action verbs detected at the beginning of bullets.")

    if v["weak_phrases_found"]:
        st.markdown(
            f'<div style="display:flex; align-items:center; gap:6px; margin:14px 0 6px;">'
            f'<span class="inline-icon-wrap">{ui.icon("alert-triangle", size=16, color="#f59e0b")}</span>'
            f'<h5 style="margin:0;">Passive Phrases to Rephrase</h5>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption("Replace passive language with decisive accomplishment verbs.")
        for p in v["weak_phrases_found"]:
            st.markdown(
                f'<div style="background:var(--yellow-bg); border:1px solid var(--yellow-border); border-radius:6px; padding:6px 12px; margin-bottom:6px; font-size:0.88rem; color:var(--yellow-text);">'
                f'Avoid <b>"{p}"</b> — replace with action-oriented phrasing like <i>"Architected and deployed..."</i>.'
                f'</div>',
                unsafe_allow_html=True,
            )

    if v["buzzwords_found"]:
        st.markdown(
            f'<div style="display:flex; align-items:center; gap:6px; margin:14px 0 6px;">'
            f'<span class="inline-icon-wrap">{ui.icon("alert-triangle", size=16, color="#f43f5e")}</span>'
            f'<h5 style="margin:0;">Overused Clichés &amp; Buzzwords</h5>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption("Hiring managers and modern algorithms prefer concrete achievements over subjective claims.")
        for b in v["buzzwords_found"]:
            st.markdown(
                f'<div style="background:var(--red-bg); border:1px solid var(--red-border); border-radius:6px; padding:6px 12px; margin-bottom:6px; font-size:0.88rem; color:var(--red-text);">'
                f'Replace <b>"{b}"</b> with verifiable project results and metrics.'
                f'</div>',
                unsafe_allow_html=True,
            )

with tab_alignment:
    ja = audit.get("job_alignment")
    if not ja:
        st.info("Paste a job description above to check how well your resume matches the specific keywords of your target role.")
    else:
        st.markdown(
            f'<div style="background:var(--card-bg); border:1px solid var(--line); border-radius:10px; padding:16px; margin-bottom:14px;">'
            f'<div style="font-size:2rem; font-weight:800; color:var(--primary);">{ja["match_rate"]}%</div>'
            f'<div style="color:var(--muted); font-size:0.9rem;">ATS Keyword Match against target job requirements</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        col_m, col_u = st.columns(2, gap="medium")
        with col_m:
            st.markdown(f"**Matched Keywords ({len(ja['matched_keywords'])})**")
            if ja["matched_keywords"]:
                st.markdown(
                    f'<div style="display:flex; flex-wrap:wrap; gap:4px;">'
                    + "".join([ui.chip(k, "matched") for k in ja["matched_keywords"]])
                    + '</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No matching catalog keywords found.")
        with col_u:
            st.markdown(f"**Missing Critical Keywords ({len(ja['missing_keywords'])})**")
            if ja["missing_keywords"]:
                st.markdown(
                    f'<div style="display:flex; flex-wrap:wrap; gap:4px;">'
                    + "".join([ui.chip(k, "missing") for k in ja["missing_keywords"]])
                    + '</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.success("All detected job skills are already present on your resume!")

# -------------------------- Download Report -------------------------------- #
st.write("")
st.download_button(
    "Download Full ATS Audit Report (TXT)",
    icon=":material/download:",
    data=build_ats_report(audit),
    file_name="skillmatch_ats_audit_report.txt",
    mime="text/plain",
    use_container_width=True,
)
