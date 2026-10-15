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


def shorten(text: str, limit: int = 22) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def heatmap_html(analysis: dict, max_rows: int = 25) -> str:
    names = list(analysis["jobs"])
    head = "<th>Skill</th>" + "".join(
        f'<th title="{html.escape(n)}">{html.escape(shorten(n))}</th>' for n in names
    )
    rows = []
    for row in analysis["skills"][:max_rows]:
        css, symbol = {
            "missing": ("hm-missing", "✗"),
            "listed": ("hm-listed", "~"),
        }.get(row["status"], ("hm-ok", "✓"))

        cells = [f"<td>{html.escape(row['skill'])}</td>"]
        for name in names:
            level = row["per_job"][name]
            if level is None:
                cells.append("<td></td>")
            else:
                extra = "" if level == "required" else " pref"
                title = "required" if level == "required" else "nice-to-have"
                cells.append(f'<td class="{css}{extra}" title="{title}">{symbol}</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        '<div class="hm-wrap"><table class="hm"><thead><tr>' + head + "</tr></thead><tbody>"
        + "".join(rows) + "</tbody></table></div>"
    )


ui.hero(
    "Skill gaps",
    "Add the roles you are targeting and see which gaps matter most across all of them.",
)

jobs: dict = st.session_state.setdefault("gap_jobs", {})

st.subheader("Your resume")
resume_text = ui.resume_loader()

st.subheader("Target jobs")
col_form, col_import = st.columns([3, 2])

with col_form:
    with st.form("add_job", clear_on_submit=True):
        name = st.text_input("Job name", placeholder="e.g. Acme – Backend Intern")
        text = st.text_area("Job description", height=160)
        if st.form_submit_button("Add job"):
            if not name.strip() or not text.strip():
                st.error("Please enter both a name and a job description.")
            elif len(jobs) >= MAX_JOBS:
                st.error(f"You can compare up to {MAX_JOBS} jobs at once.")
            else:
                jobs[unique_name(name, jobs)] = text

with col_import:
    saved = [a for a in tracker.list_applications() if a["job_description"].strip()]
    options = {}
    for app in saved:
        label = f'{app["company"]} – {app["role"]}'
        if label not in jobs and label not in options:
            options[label] = app["job_description"]
    chosen = st.multiselect("Import from your tracker", list(options),
                            help="Only tracked jobs with a saved description appear here.")
    if st.button("Import selected", disabled=not chosen):
        for label in chosen:
            if len(jobs) < MAX_JOBS:
                jobs[label] = options[label]
        st.rerun()

if jobs:
    for job_name in list(jobs):
        c1, c2 = st.columns([6, 1])
        c1.markdown(f"**{ui.md_escape(job_name)}**  ·  {len(jobs[job_name].split())} words")
        if c2.button("Remove", key=f"rm_{job_name}"):
            del jobs[job_name]
            st.rerun()
    if st.button("Clear all jobs"):
        jobs.clear()
        st.rerun()

if not resume_text:
    st.info("Load your resume above to see your skill gaps.")
    st.stop()
if not jobs:
    st.info("Add at least one job to get started. Three or more shows the clearest patterns.")
    st.stop()

analysis = analyze_jobs(resume_text, jobs)

st.divider()
st.subheader("Overview")
avg = analysis["avg_evidence_score"]
top = analysis["gaps"][0]["skill"] if analysis["gaps"] else "None"
st.markdown(
    ui.stat_row([
        ("Jobs compared", len(jobs)),
        ("Average evidence-backed match", "n/a" if avg is None else f"{avg}%"),
        ("Biggest gap", top),
    ]),
    unsafe_allow_html=True,
)

st.write("")
st.dataframe(
    [
        {
            "Job": name,
            "Keyword match": "n/a" if info["score"] is None else f'{info["score"]}%',
            "Evidence-backed": "n/a" if info["evidence_score"] is None else f'{info["evidence_score"]}%',
            "Skills asked": info["n_skills"],
            "Missing": ", ".join(info["missing"][:6]) or "None",
        }
        for name, info in analysis["jobs"].items()
    ],
    hide_index=True,
    width="stretch",
)

st.subheader("Gaps to close first")
st.caption("Ranked by how many jobs ask for the skill, whether it is required, and how well your resume proves it.")
if not analysis["gaps"]:
    st.success("No gaps found: every skill these jobs ask for is backed by evidence on your resume.")
else:
    st.markdown(ui.legend(), unsafe_allow_html=True)
    st.markdown(ui.demand_rows(analysis["gaps"][:8]), unsafe_allow_html=True)
    st.page_link("views/roadmap_page.py", label="Build my learning roadmap")

st.subheader("Skill heatmap")
st.markdown(heatmap_html(analysis), unsafe_allow_html=True)
st.caption("✓ proven on your resume, ~ listed only, ✗ missing. Faded cells are nice-to-have; blank cells mean the job does not ask for that skill.")
