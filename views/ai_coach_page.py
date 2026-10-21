import streamlit as st

import ai
import ui
from ai import OllamaClient, OllamaError
from analyzer import analyze_resume


def shorten(text: str, limit: int = 90) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


@st.cache_data(ttl=10, show_spinner=False)
def check_ollama(host: str):
    try:
        return OllamaClient(host, timeout=3).list_models(), None
    except OllamaError as error:
        return [], str(error)


def pick(label: str, options: list[str], default: str | None, key: str) -> str | None:
    if not options:
        return None
    index = options.index(default) if default in options else 0
    return st.selectbox(label, options, index=index, key=key)


ui.hero(
    "Local AI Career Coach",
    "Private, on-device intelligence for bullet rewriting, semantic requirement matching, fit explanations, and tailored interview coaching. Your resume never leaves your computer.",
    badge="AI Module · 100% On-Device",
    icon_html=ui.ai_coach_logo(52),
)

# ------------------------------- inputs ------------------------------------ #
left, right = st.columns(2, gap="medium")
with left:
    st.markdown("#### 1. Your Resume")
    resume_text = ui.resume_loader()
with right:
    c_ai_job_title, c_ai_job_sample = st.columns([1, 1], vertical_alignment="center")
    with c_ai_job_title:
        st.markdown("#### 2. Target Job")
    with c_ai_job_sample:
        if st.button("Load sample job (1-click)", icon=":material/work:", key="btn_sample_job_ai"):
            ui.load_sample_job()

    # Same key as the Analyzer page, so the job description is shared between them.
    job_text = ui.persistent(
        st.text_area, "Job description", "job_text_input", "", height=220,
        label_visibility="collapsed", placeholder="Paste the job description here...",
    )

# ------------------------------ Ollama setup -------------------------------- #
with st.expander("Local Ollama AI Settings & Status", expanded=not st.session_state.get("_ollama_ok")):
    host = st.text_input("Ollama Server Address", value=ai.normalize_host(None), key="ollama_host")
    models, error = check_ollama(host)
    st.session_state["_ollama_ok"] = error is None

    if error:
        st.markdown(
            f'<div style="background:var(--red-bg); border:1px solid var(--red-border); border-radius:8px; padding:12px 16px; margin:8px 0; color:var(--red-text); font-size:0.9rem;">'
            f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;"><span class="inline-icon-wrap">{ui.icon("alert-triangle", size=16, color="var(--red-text)")}</span><b>Ollama connection issue:</b></div>'
            f'{ui.esc(error)}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "**Quick Setup Instructions (Free & Private):**\n"
            "1. Download and install Ollama from [https://ollama.com](https://ollama.com)\n"
            "2. Open your terminal and run:\n"
            "   ```bash\n"
            "   ollama pull llama3.2\n"
            "   ollama pull nomic-embed-text\n"
            "   ```\n"
            "3. Ensure the Ollama app is running, then refresh this page."
        )
        chat_model = embed_model = None
    else:
        st.markdown(
            f'<div style="background:var(--green-bg); border:1px solid var(--green-border); border-radius:8px; padding:10px 14px; margin-bottom:12px; color:var(--green-text); font-size:0.9rem; display:flex; align-items:center; gap:8px;">'
            f'<span class="inline-icon-wrap">{ui.icon("check-circle-2", size=16, color="var(--green-text)")}</span> <b>Ollama is connected and running locally.</b> Resumes are processed in private memory.'
            f'</div>',
            unsafe_allow_html=True,
        )
        default_chat, default_embed = ai.pick_defaults(models)
        embedding_models = [m for m in models if "embed" in m.lower()]
        chat_models = [m for m in models if m not in embedding_models]
        c1, c2 = st.columns(2)
        with c1:
            chat_model = pick("Chat Model", chat_models, default_chat, "chat_model")
        with c2:
            embed_model = pick("Embedding Model", embedding_models, default_embed, "embed_model")
        if not chat_models:
            st.warning("No chat model installed. Run `ollama pull llama3.2` in your terminal.", icon=":material/warning:")

if error:
    st.stop()
if not resume_text:
    st.info("Please upload or paste your resume above to begin using the AI Coach.", icon=":material/info:")
    st.stop()

client = OllamaClient(host, timeout=180)


def llm(system: str, user: str, temperature: float = 0.2) -> str:
    return client.chat(chat_model, system, user, temperature=temperature)


def need_job() -> bool:
    if job_text.strip():
        return False
    st.info("Paste a target job description above to unlock this tool.", icon=":material/info:")
    return True


analysis = analyze_resume(resume_text, job_text) if job_text.strip() else None

tab_rewrite, tab_semantic, tab_summary, tab_interview = st.tabs(
    ["Fact-Checked Bullet Rewriter", "Semantic Matching", "Plain-Language Fit Summary", "Tailored Interview Prep"]
)

# ------------------------------ bullet rewriter ------------------------------ #
with tab_rewrite:
    st.markdown(
        '<p style="color:var(--muted); font-size:0.92rem; margin-top:4px;">'
        'Strengthen your impact without hallucinations. Rewrites are strictly constrained to facts in your bullet. '
        'Any new numbers or skills are automatically flagged for fact-checking.'
        '</p>',
        unsafe_allow_html=True,
    )
    bullets = ai.candidate_bullets(resume_text)
    choice = st.selectbox("Select a bullet from your resume", bullets, format_func=shorten) if bullets else None
    custom = st.text_area("…or paste a specific bullet to rewrite", height=80, key="custom_bullet", placeholder="e.g. Developed API endpoints for our user onboarding process.")
    bullet = custom.strip() or choice

    if st.button("Generate Fact-Checked Rewrite", icon=":material/auto_awesome:", type="primary", disabled=not bullet or not chat_model):
        targets = list(analysis["job"])[:10] if analysis else []
        try:
            with st.spinner("Analyzing context and polishing bullet..."):
                st.session_state["ai_rewrite"] = ai.rewrite_bullet(bullet, targets, llm)
        except OllamaError as exc:
            st.error(str(exc))

    result = st.session_state.get("ai_rewrite")
    if result:
        st.write("")
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            with st.container(border=True):
                st.markdown("**Original Bullet:**")
                st.code(result["original"], language=None)
        with c2:
            with st.container(border=True):
                st.markdown("**AI Optimized Suggestion:**")
                st.code(result["rewrite"], language=None)
        if result["problems"]:
            for problem in result["problems"]:
                st.warning(f"Fact-check alert: {problem}", icon=":material/warning:")
        else:
            st.success("Passed strict fact check: No unverified claims, skills, or metrics added.", icon=":material/verified:")
        if "[" in result["rewrite"]:
            st.info("Tip: Replace each bracketed [placeholder] with your genuine metrics, or remove it.", icon=":material/lightbulb:")

# ------------------------------ semantic matching ----------------------------- #
with tab_semantic:
    st.markdown(
        '<p style="color:var(--muted); font-size:0.92rem; margin-top:4px;">'
        'Traditional keyword match misses synonyms (e.g. "built REST services" vs "API engineering"). '
        'This tool compares contextual embeddings locally to identify semantic alignment.'
        '</p>',
        unsafe_allow_html=True,
    )
    if not need_job():
        if not embed_model:
            st.warning("No embedding model installed. Run `ollama pull nomic-embed-text` in your terminal.", icon=":material/warning:")
        else:
            with st.expander("Model Match Sensitivity Thresholds"):
                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    strong = st.slider("Strong Match Threshold", 0.30, 0.95, 0.62, 0.01)
                with c_s2:
                    partial = st.slider("Partial Match Threshold", 0.20, 0.90, 0.50, 0.01)

            requirements = ai.extract_requirements(job_text)
            items = ai.candidate_bullets(resume_text)
            st.caption(f"Detected {len(requirements)} requirements from job description · {len(items)} bullets from resume")

            if st.button("Run Semantic Embeddings Analysis", icon=":material/bolt:", type="primary", disabled=not requirements or not items or partial >= strong):
                try:
                    with st.spinner("Computing high-dimensional text embeddings..."):
                        st.session_state["ai_semantic"] = ai.semantic_match(
                            requirements, items, lambda texts: client.embed(embed_model, texts),
                            strong=strong, partial=partial,
                        )
                except OllamaError as exc:
                    st.error(str(exc))
            if partial >= strong:
                st.warning("Partial threshold must be lower than strong threshold.", icon=":material/warning:")

            semantic = st.session_state.get("ai_semantic")
            if semantic:
                groups = ai.categorize(semantic)
                st.markdown(
                    ui.stat_row([
                        ("Strong Semantic Matches", sum(r["label"] == "strong" for r in semantic)),
                        ("Partial Matches", sum(r["label"] == "partial" for r in semantic)),
                        ("No Direct Support", len(groups["unsupported"])),
                    ]),
                    unsafe_allow_html=True,
                )

                st.markdown("#### Matched by Context & Meaning")
                if not groups["by_meaning"]:
                    st.caption("Standard keyword matching already covers the detected alignments.")
                for r in groups["by_meaning"]:
                    with st.container(border=True):
                        st.markdown(f"**Job Requirement:** {ui.md_escape(r['requirement'])}")
                        st.markdown(
                            f'<div style="font-size:0.86rem; color:var(--muted);">'
                            f'Top resume match (Similarity: <b>{r["similarity"]}</b>, status: <b style="color:var(--primary);">{r["label"]}</b>):<br>'
                            f'<i>"{ui.esc(r["best_item"])}"</i>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                st.markdown("#### Unsupported Job Requirements")
                if not groups["unsupported"]:
                    st.caption("Every requirement has at least a partial match in your resume.")
                for r in groups["unsupported"]:
                    with st.container(border=True):
                        st.markdown(f"**Missing Coverage:** {ui.md_escape(r['requirement'])}")
                        st.caption(f"Highest similarity bullet was only {r['similarity']}: “{shorten(r['best_item'])}”")

# ------------------------------- fit summary -------------------------------- #
with tab_summary:
    st.markdown(
        '<p style="color:var(--muted); font-size:0.92rem; margin-top:4px;">'
        'A clear, objective narrative explaining your qualifications against this job post based strictly on verified skill evidence.'
        '</p>',
        unsafe_allow_html=True,
    )
    if not need_job():
        if analysis["score"] is None:
            st.warning("No supported skills were detected in this job description.", icon=":material/warning:")
        elif st.button("Synthesize Fit Summary", icon=":material/description:", type="primary", disabled=not chat_model):
            try:
                with st.spinner("Writing objective fit overview..."):
                    st.session_state["ai_summary"] = ai.fit_summary(analysis, llm)
            except OllamaError as exc:
                st.error(str(exc))

        summary = st.session_state.get("ai_summary")
        if summary:
            if summary["problems"]:
                for problem in summary["problems"]:
                    st.warning(f"Note: {problem}", icon=":material/warning:")
            with st.container(border=True):
                st.markdown(summary["summary"])
            st.caption("Generated strictly from deterministic skill evidence. Your match scores are unaltered.")
            with st.expander("View Input Facts Passed to AI"):
                st.json(summary["facts"])

# ------------------------------ interview prep ------------------------------ #
with tab_interview:
    st.markdown(
        '<p style="color:var(--muted); font-size:0.92rem; margin-top:4px;">'
        'Targeted technical and behavioral questions tailored specifically to probe your identified skill gaps and unproven competencies.'
        '</p>',
        unsafe_allow_html=True,
    )
    if not need_job():
        c_q1, c_q2 = st.columns([3, 1], vertical_alignment="center")
        with c_q1:
            count = st.slider("Target Number of Questions", 3, 10, 5)
        with c_q2:
            gen_btn = st.button("Generate Prep Questions", icon=":material/quiz:", type="primary", disabled=not chat_model, use_container_width=True)

        if gen_btn:
            try:
                with st.spinner("Drafting tailored interview questions..."):
                    st.session_state["ai_questions"] = ai.interview_questions(
                        analysis, job_text, lambda s, u: llm(s, u, temperature=0.6), n=count
                    )
            except OllamaError as exc:
                st.error(str(exc))

        questions = st.session_state.get("ai_questions")
        if questions:
            if questions["focus"]:
                st.markdown(
                    f'<div style="margin:10px 0 16px;">'
                    f'<b style="font-size:0.85rem; color:var(--muted);">FOCUSED SKILL GAPS:</b> '
                    f'{" ".join([ui.chip(s, "missing") for s in questions["focus"]])}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            for number, question in enumerate(questions["questions"], start=1):
                with st.container(border=True):
                    st.markdown(f"**Q{number}:** {ui.md_escape(question)}")
            st.markdown(
                f'<div style="font-size:0.82rem; color:var(--muted); margin-top:8px; display:flex; align-items:flex-start; gap:6px;">'
                f'<span class="inline-icon-wrap" style="flex-shrink:0; margin-top:2px;">{ui.icon("lightbulb", size=13, color="var(--primary)")}</span>'
                f'<span>Best practice: When addressing skills you currently lack, articulate your conceptual foundation and reference your learning roadmap.</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
