"""Shared Streamlit helpers: the visual system, small components, and the resume loader.

Visual idea: the app marks up a resume the way an editor would.
  green highlighter  = skill proven by a project or job bullet
  yellow highlighter = skill only listed, with no proof
  red squiggle       = skill the job asks for that is missing
"""

import html
import re

import streamlit as st

from analyzer import ResumeError, extract_text

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Figtree:wght@400;500;600;700&display=swap');

:root {
    --ink: #172033;
    --muted: #5b667a;
    --line: rgba(23, 32, 51, .14);
    --green: #bdebd0;
    --green-strong: #86d4a8;
    --yellow: #ffe27a;
    --red: #d9372b;
    --blue-hl: #cfe0ff;
    --display: 'Bricolage Grotesque', 'Segoe UI', system-ui, sans-serif;
}

/* ---------- base ---------- */
html, body, .stApp, .stMarkdown, label, input, textarea, button,
[data-baseweb="select"], [data-testid="stCaptionContainer"] {
    font-family: 'Figtree', 'Segoe UI', system-ui, -apple-system, sans-serif;
}
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1100px; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

h1, h2, h3 {
    font-family: var(--display) !important;
    color: var(--ink);
    letter-spacing: -0.015em;
}
h3 { font-size: 1.3rem !important; }

[data-testid="stSidebar"] { border-right: 1px solid var(--line); }
.brand { font-family: var(--display); font-weight: 800; font-size: 1.4rem;
         color: var(--ink); letter-spacing: -0.02em; line-height: 1.1; }
.brand-sub { color: var(--muted); font-size: .88rem; margin: 4px 0 10px; }

/* ---------- Streamlit widgets ---------- */
div.stButton > button, div.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button, a[data-testid="stPageLink-NavLink"] {
    border-radius: 8px; font-weight: 600;
}
[data-testid="stExpander"] details {
    border: 1px solid var(--line); border-radius: 10px; background: #fff;
}
[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed rgba(23, 32, 51, .3); border-radius: 10px; background: #fff;
}
.stTabs [data-baseweb="tab"] { font-weight: 600; }

/* ---------- page header ---------- */
.page-head { padding: 2px 0 20px; border-bottom: 1px solid var(--line); margin-bottom: 28px; }
.page-head h1 {
    font-size: 2.1rem !important; line-height: 1.15 !important; font-weight: 700 !important;
    margin: 0 0 8px !important; padding: 0 !important; color: var(--ink) !important;
}
.page-head p { color: var(--muted); font-size: 1.03rem; margin: 0; max-width: 64ch; }

/* ---------- stats (one panel, not a row of cards) ---------- */
.stats { display: flex; flex-wrap: wrap; background: #fff; border: 1px solid var(--line);
         border-radius: 10px; margin-bottom: 6px; }
.stat { flex: 1 1 150px; padding: 16px 22px; border-right: 1px solid var(--line); }
.stat:last-child { border-right: 0; }
.stat-label { color: var(--muted); font-size: .86rem; }
.stat-value { font-family: var(--display); font-size: 1.9rem; font-weight: 700;
              color: var(--ink); line-height: 1.15; margin-top: 2px; }

/* ---------- panels ---------- */
.panel { background: #fff; border: 1px solid var(--line); border-radius: 10px;
         padding: 18px 20px; margin-bottom: 12px; min-height: 110px; }
.panel h3 { font-size: 1.08rem !important; margin: 0 0 2px !important; padding: 0 !important; }
.panel-sub { color: var(--muted); font-size: .88rem; margin: 0 0 12px; }
.empty { color: var(--muted); font-style: italic; }

/* ---------- the markup vocabulary ---------- */
.mk { display: inline-block; margin: 3px 8px 5px 0; padding: 1px 7px; font-weight: 600;
      font-size: .93rem; color: var(--ink); line-height: 1.5; border-radius: 3px; }
.mk.matched  { background: linear-gradient(180deg, transparent 38%, var(--green) 38%); }
.mk.unproven { background: linear-gradient(180deg, transparent 38%, var(--yellow) 38%); }
.mk.extra    { background: linear-gradient(180deg, transparent 38%, var(--blue-hl) 38%); }
.mk.missing  { text-decoration: underline wavy var(--red); text-decoration-thickness: 1.5px;
               text-underline-offset: 5px; }
.mk.preferred { color: var(--muted); font-weight: 500; text-decoration: underline dotted var(--muted);
                text-underline-offset: 5px; }
.legend { display: flex; flex-wrap: wrap; align-items: center; gap: 2px 14px; margin: 4px 0 14px; }
.legend .mk { font-size: .85rem; margin: 0; }

/* ---------- proof bar ---------- */
.proof { background: #fff; border: 1px solid var(--line); border-radius: 10px;
         padding: 20px 24px; margin-bottom: 10px; }
.proof-top { display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap; }
.proof-num { font-family: var(--display); font-size: 3.3rem; font-weight: 800;
             color: var(--ink); line-height: 1; letter-spacing: -0.03em; }
.proof-label { color: var(--muted); font-size: 1rem; }
.proof-track { display: flex; height: 14px; border-radius: 3px; overflow: hidden; margin: 16px 0 10px;
               background: rgba(23, 32, 51, .06); }
.proof-track i { display: block; height: 100%; }
.p-ok { background: var(--green-strong); }
.p-listed { background: var(--yellow); }
.p-missing { background: repeating-linear-gradient(135deg, #f3c5c1 0 5px, #fbe4e2 5px 10px); }
.proof-meta { display: flex; flex-wrap: wrap; gap: 4px 22px; font-size: .88rem; color: var(--muted); }
.proof-meta b { color: var(--ink); }

/* ---------- demand rows (skill gaps) ---------- */
.demand { display: grid; grid-template-columns: minmax(130px, 210px) 1fr minmax(150px, auto);
          align-items: center; gap: 16px; padding: 9px 0; border-bottom: 1px solid var(--line); }
.demand:last-child { border-bottom: 0; }
.demand .mk { justify-self: start; margin: 0; }
.demand-bar { height: 8px; background: rgba(23, 32, 51, .07); border-radius: 2px; overflow: hidden; }
.demand-bar i { display: block; height: 100%; background: var(--ink); }
.demand-meta { color: var(--muted); font-size: .86rem; text-align: right; white-space: nowrap; }
@media (max-width: 640px) {
    .home-title { font-size: 2.2rem; }
    .proof-num { font-size: 2.6rem; }
    .demand { grid-template-columns: 1fr; gap: 4px; }
    .demand-meta { text-align: left; }
}

/* ---------- heatmap ---------- */
.hm-wrap { overflow-x: auto; margin-bottom: 6px; background: #fff; border: 1px solid var(--line);
           border-radius: 10px; }
.hm { border-collapse: collapse; width: 100%; font-size: .9rem; }
.hm th, .hm td { border-bottom: 1px solid var(--line); padding: 8px 12px; text-align: center; }
.hm tr:last-child td { border-bottom: 0; }
.hm td:first-child, .hm th:first-child { text-align: left; font-weight: 600; width: 150px; }
.hm th { color: var(--muted); font-weight: 600; }
.hm-ok      { background: var(--green); color: #0e5a37; font-weight: 700; }
.hm-listed  { background: var(--yellow); color: #5c4800; font-weight: 700; }
.hm-missing { background: #fbe0dd; color: #a42a21; font-weight: 700; }
.pref { opacity: .55; }

/* ---------- tracker columns ---------- */
.col-head { display: flex; justify-content: space-between; align-items: baseline;
            padding: 4px 2px 6px; margin-bottom: 10px; font-weight: 700; color: var(--ink);
            border-bottom: 2px solid var(--c, var(--ink)); }
.col-head span { color: var(--muted); font-weight: 600; }

/* ---------- home page ---------- */
.home-title { font-family: var(--display); font-weight: 800; font-size: 3.1rem; line-height: 1.05;
              letter-spacing: -0.03em; color: var(--ink); margin: 6px 0 16px; }
.home-sub { color: var(--muted); font-size: 1.1rem; line-height: 1.55; max-width: 46ch; margin: 0 0 22px; }
.sheet { background: #fff; border: 1px solid var(--line); border-radius: 6px; padding: 22px 26px;
         box-shadow: 0 14px 30px -22px rgba(23, 32, 51, .45); line-height: 1.8; font-size: .97rem; }
.sheet-h { font-weight: 700; color: var(--muted); font-size: .85rem; margin-top: 8px; }
.sheet-ask { margin-top: 14px; padding-top: 12px; border-top: 1px dashed var(--line); }
.sheet-ask-label { display: block; color: var(--muted); font-size: .85rem; margin-bottom: 2px; }
.sheet .legend { margin-top: 16px; margin-bottom: 0; }
.flow { display: flex; gap: 16px; align-items: flex-start; padding: 14px 0; }
.flow-num { flex: 0 0 30px; height: 30px; border-radius: 50%; background: var(--ink); color: #fff;
            font-weight: 700; display: flex; align-items: center; justify-content: center; font-size: .9rem; }
.flow-opt { flex: 0 0 auto; padding: 4px 8px; border: 1px solid var(--line); border-radius: 6px;
            color: var(--muted); font-size: .78rem; font-weight: 600; }
.flow-title { font-weight: 700; color: var(--ink); font-size: 1.05rem; }
.flow-desc { color: var(--muted); margin-top: 2px; }
</style>
"""

STATUS_COLORS = {
    "Saved": "#8a94a6", "Applied": "#1f4fd8", "Interview": "#c9921a",
    "Offer": "#1f9d63", "Rejected": "#c7352f",
}
GAP_CHIP = {"missing": "missing", "listed": "unproven", "demonstrated": "matched", "strong": "matched"}


def esc(value) -> str:
    return html.escape(str(value))


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    """Slim page header (kept under the old name so every page keeps working)."""
    st.markdown(
        f'<div class="page-head"><h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def md_escape(text: str) -> str:
    """Escape characters Streamlit's markdown would otherwise interpret."""
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|<>$~])", r"\\\1", text)


# ----------------------------- components ---------------------------------- #

def stat_row(items: list[tuple[str, object]]) -> str:
    """One panel holding several stats, separated by hairlines."""
    cells = "".join(
        f'<div class="stat"><div class="stat-label">{esc(label)}</div>'
        f'<div class="stat-value">{esc(value)}</div></div>'
        for label, value in items
    )
    return f'<div class="stats">{cells}</div>'


def metric_card(label: str, value: str) -> str:  # backwards compatible
    return stat_row([(label, value)])


def chip(name: str, css: str) -> str:
    return f'<span class="mk {css}">{esc(name)}</span>'


def legend() -> str:
    return (
        '<div class="legend">'
        + chip("proven", "matched")
        + chip("listed only", "unproven")
        + chip("missing", "missing")
        + chip("nice-to-have", "preferred")
        + "</div>"
    )


def skill_card(title: str, subtitle: str, badges: list[tuple[str, str]]) -> str:
    """Heading and skill marks inside ONE panel. badges = [(name, css_class)]."""
    body = "".join(chip(name, css) for name, css in badges) or '<span class="empty">None detected.</span>'
    return (
        f'<div class="panel"><h3>{esc(title)}</h3>'
        f'<p class="panel-sub">{esc(subtitle)}</p>{body}</div>'
    )


def proof_bar(result: dict) -> str:
    """Headline score plus a bar showing how the job's skills split into proven / listed / missing."""
    job = result["job"]
    total = sum(info["weight"] for info in job.values())
    if not total:
        return ""

    unproven = set(result["unproven"])
    proven_skills = [s for s in result["matched"] if s not in unproven]
    weight = lambda skills: sum(job[s]["weight"] for s in skills)
    ok, listed = weight(proven_skills), weight(result["unproven"])
    missing = max(total - ok - listed, 0)
    pct = lambda w: f"{100 * w / total:.1f}%"

    return (
        '<div class="proof">'
        '<div class="proof-top">'
        f'<div class="proof-num">{result["evidence_score"]}%</div>'
        '<div class="proof-label">evidence-backed match</div></div>'
        '<div class="proof-track">'
        f'<i class="p-ok" style="width:{pct(ok)}"></i>'
        f'<i class="p-listed" style="width:{pct(listed)}"></i>'
        f'<i class="p-missing" style="width:{pct(missing)}"></i></div>'
        '<div class="proof-meta">'
        f'<span><b>{len(proven_skills)}</b> proven</span>'
        f'<span><b>{len(result["unproven"])}</b> listed only</span>'
        f'<span><b>{len(result["missing"])}</b> missing</span>'
        f'<span>Keyword match <b>{result["score"]}%</b></span>'
        "</div></div>"
    )


def demand_rows(gaps: list[dict]) -> str:
    """How many of your target jobs ask for each gap."""
    rows = "".join(
        '<div class="demand">'
        f'{chip(g["skill"], GAP_CHIP[g["status"]])}'
        f'<div class="demand-bar"><i style="width:{100 * g["demand"] / g["n_jobs"]:.0f}%"></i></div>'
        f'<div class="demand-meta">{g["demand"]} of {g["n_jobs"]} jobs, {g["required"]} required</div>'
        "</div>"
        for g in gaps
    )
    return f'<div class="panel">{rows}</div>'


def column_head(status: str, count: int) -> str:
    color = STATUS_COLORS.get(status, "#172033")
    return f'<div class="col-head" style="--c:{color}">{esc(status)}<span>{count}</span></div>'


# ------------------------- state that survives pages ------------------------ #

def persistent(widget, label, key, default, *args, **kwargs):
    """Draw a widget whose value survives navigating to another page.

    Streamlit deletes a widget's state when the widget is not drawn on the current
    page. We mirror the value into a plain session key and restore it on return.
    """
    store = f"_saved_{key}"
    if key not in st.session_state:
        st.session_state[key] = st.session_state.get(store, default)
    value = widget(label, *args, key=key, **kwargs)
    st.session_state[store] = value
    return value


def _store_resume(text: str, name: str) -> None:
    st.session_state["resume_text"] = text
    st.session_state["resume_name"] = name
    st.session_state["_replace_resume"] = False
    st.rerun()


def resume_loader() -> str | None:
    """Shared resume widget. Once loaded, the resume stays loaded on every page.

    (A file uploader cannot be pre-filled, so after loading we show a status card
    with Replace/Remove instead of an empty uploader.)
    """
    text = st.session_state.get("resume_text")
    replacing = st.session_state.get("_replace_resume", False)

    if text and not replacing:
        name = st.session_state.get("resume_name", "resume")
        with st.container(border=True):
            st.markdown(f"**{md_escape(name)}** is loaded ({len(text.split())} words)")
            st.caption("It stays loaded while you move between pages.")
            c1, c2 = st.columns(2)
            if c1.button("Replace resume", key="resume_replace"):
                st.session_state["_replace_resume"] = True
                st.rerun()
            if c2.button("Remove resume", key="resume_remove"):
                for key in ("resume_text", "resume_name"):
                    st.session_state.pop(key, None)
                st.rerun()
        return text

    uploaded = st.file_uploader(
        "Upload a PDF or DOCX",
        type=["pdf", "docx"],
        key="resume_file",
        help="Use a file with selectable text. Multi-column PDFs may extract "
             "out of order; single-column layouts work best.",
    )
    with st.expander("Or paste your resume text"):
        pasted = st.text_area("Resume text", height=140, key="resume_paste",
                              label_visibility="collapsed")
        use_pasted = st.button("Use pasted text", key="resume_use_paste",
                               disabled=not pasted.strip())
    if text and st.button("Cancel", key="resume_cancel"):
        st.session_state["_replace_resume"] = False
        st.rerun()

    if uploaded is not None:
        try:
            _store_resume(extract_text(uploaded.name, uploaded.getvalue()), uploaded.name)
        except ResumeError as error:
            st.error(str(error))
    elif use_pasted:
        _store_resume(pasted, "pasted text")
    return text
