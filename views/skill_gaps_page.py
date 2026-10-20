import html

import streamlit as st

import tracker
import ui
from gaps import analyze_jobs

MAX_JOBS = 10
STATUS_LABEL = {
    "missing": "missing",
    "listed": "listed only, no proof",
    "demonstrated": "demonstrated",
    "strong": "strong evidence",
}


def unique_name(name: str, existing: dict) -> str:
    name, candidate, n = name.strip(), name.strip(), 2
    while candidate in existing:
        candidate = f"{name} ({n})"
        n += 1
    return candidate


def shorten(text: str, limit: int = 20) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def heatmap_html(analysis: dict, max_rows: int = 25) -> str:
    names = list(analysis["jobs"])
    head = "<th>Skill</th>" + "".join(
        f'<th title="{html.escape(n)}">{html.escape(shorten(n))}</th>' for n in names
    )
    rows = []
    for row in analysis["skills"][:max_rows]:
        css, symbol = {
            "missing": ("hm-missing", "✕"),
            "listed": ("hm-listed", "●"),
        }.get(row["status"], ("hm-ok", "✓"))

        cells = [f"<td><b>{html.escape(row['skill'])}</b></td>"]
        for name in names:
            level = row["per_job"][name]
            if level is None:
                cells.append("<td><span style='color:var(--line);'>—</span></td>")
            else:
                extra = "" if level == "required" else " pref"
                title = f"{name}: {'Required' if level == 'required' else 'Nice-to-have'}"
                cells.append(
                    f'<td><span class="hm-cell-badge {css}{extra}" title="{html.escape(title)}">{symbol}</span></td>'
                )
        rows.append("<tr>" + "".join(cells) + "</tr>")

    scroll_hint = '<div style="font-size:0.78rem; color:var(--muted); margin-bottom:6px;">💡 Swipe or scroll horizontally on smaller screens to view all jobs. First column stays pinned.</div>'
    return (
        f'{scroll_hint}'
        f'<div class="hm-wrap"><table class="hm"><thead><tr>{head}</tr></thead><tbody>'
        f'{"".join(rows)}</tbody></table></div>'
    )


ui.hero(
    "Skill Gaps Analysis",
    "Target multiple roles simultaneously to uncover the high-frequency skill gaps across your industry. Prioritize what employers demand most.",
    badge="Step 3 · Multi-Job Matrix",
)

jobs: dict = st.session_state.setdefault("gap_jobs", {})

st.markdown("#### 1. Your Resume")
resume_text = ui.resume_loader()

st.markdown("#### 2. Target Job Descriptions")
col_gap_head, col_gap_sample = st.columns([3, 2], vertical_alignment="center")
with col_gap_head:
    st.caption("Compare up to 10 job descriptions to reveal recurring industry requirements.")
with col_gap_sample:
    if st.button("💼 Add sample demo job (1-click)", key="btn_sample_gap_job"):
        jobs["CloudScale AI – Senior Backend"] = ui.SAMPLE_JOB_DESCRIPTION
        st.rerun()

col_form, col_import = st.columns([3, 2], gap="medium")

with col_form:
    with st.container(border=True):
        st.markdown("**Add a New Target Job**")
        with st.form("add_job", clear_on_submit=True):
            name = st.text_input("Job / Company Identifier", placeholder="e.g. Acme – Backend Engineer")
            text = st.text_area("Job Description Requirements", height=140, placeholder="Paste job description requirements...")
            if st.form_submit_button("➕ Add Job to Matrix", use_container_width=True):
                if not name.strip() or not text.strip():
                    st.error("Please enter both a name and a job description.")
                elif len(jobs) >= MAX_JOBS:
                    st.error(f"You can compare up to {MAX_JOBS} jobs at once.")
                else:
                    jobs[unique_name(name, jobs)] = text
                    st.rerun()

with col_import:
    with st.container(border=True):
        st.markdown("**Import from Job Tracker**")
        saved = [a for a in tracker.list_applications() if a["job_description"].strip()]
        options = {}
        for app in saved:
            label = f'{app["company"]} – {app["role"]}'
            if label not in jobs and label not in options:
                options[label] = app["job_description"]
        chosen = st.multiselect("Select tracked jobs with descriptions", list(options),
                                help="Only tracked applications with a saved description appear here.")
        if st.button("📥 Import Selected Jobs", disabled=not chosen, use_container_width=True):
            for label in chosen:
                if len(jobs) < MAX_JOBS:
                    jobs[label] = options[label]
            st.rerun()

if jobs:
    st.markdown(f"##### Currently Comparing ({len(jobs)} / {MAX_JOBS} jobs)")
    for job_name in list(jobs):
        c1, c2 = st.columns([5, 1], vertical_alignment="center")
        with c1:
            st.markdown(
                f'<div style="background:#ffffff; border:1px solid var(--line); border-radius:8px; padding:8px 14px; display:flex; justify-content:space-between; align-items:center;">'
                f'<span>💼 <b>{ui.md_escape(job_name)}</b></span>'
                f'<span style="font-size:0.8rem; color:var(--muted);">{len(jobs[job_name].split())} words</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("Remove", key=f"rm_{job_name}", use_container_width=True):
                del jobs[job_name]
                st.rerun()
    if st.button("Clear all jobs", type="secondary"):
        jobs.clear()
        st.rerun()

if not resume_text:
    st.info("👆 Load your resume above to see your personalized skill gap matrix.")
    st.stop()
if not jobs:
    st.info("👆 Add at least one target job above to get started. Comparing 3 to 5 jobs provides the clearest market insight.")
    st.stop()

analysis = analyze_jobs(resume_text, jobs)

st.divider()
st.markdown("### Multi-Job Market Overview")
avg = analysis["avg_evidence_score"]
top = analysis["gaps"][0]["skill"] if analysis["gaps"] else "None"
st.markdown(
    ui.stat_row([
        ("Jobs Compared", len(jobs)),
        ("Avg Evidence Match", "n/a" if avg is None else f"{avg}%"),
        ("Highest Priority Gap", top),
    ]),
    unsafe_allow_html=True,
)

st.write("")
st.dataframe(
    [
        {
            "Target Job": name,
            "Keyword Match": "n/a" if info["score"] is None else f'{info["score"]}%',
            "Evidence Match": "n/a" if info["evidence_score"] is None else f'{info["evidence_score"]}%',
            "Skills Found": info["n_skills"],
            "Key Missing Skills": ", ".join(info["missing"][:5]) or "None",
        }
        for name, info in analysis["jobs"].items()
    ],
    hide_index=True,
    use_container_width=True,
)

st.markdown("### Gaps to Close First")
st.caption("Ranked by frequency across your target jobs, employer requirement level, and your current resume evidence.")
if not analysis["gaps"]:
    st.success("🎉 Spectacular! Every skill requested across these target jobs is backed by verifiable evidence on your resume.")
else:
    st.markdown(ui.legend(), unsafe_allow_html=True)
    st.markdown(ui.demand_rows(analysis["gaps"][:8]), unsafe_allow_html=True)
    st.page_link("views/roadmap_page.py", label="🗺️ Turn these gaps into a Learning Roadmap", use_container_width=True)

st.markdown("### Comprehensive Skill Heatmap")
st.markdown(heatmap_html(analysis), unsafe_allow_html=True)
st.caption("Key: ✓ Proven on resume · ● Listed without proof · ✕ Missing · Faded icons represent optional/nice-to-have requirements · Dashes represent skills not mentioned in that job.")
