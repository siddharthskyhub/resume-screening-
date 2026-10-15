import streamlit as st

import ai
import ui
from ai import OllamaClient, OllamaError
from analyzer import analyze_resume


def shorten(text: str, limit: int = 100) -> str:
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
    "AI coach",
    "Local AI that rewrites bullets, matches by meaning, explains your fit, and preps you for interviews. "
    "Your scores never come from the AI.",
)

# ------------------------------- inputs ------------------------------------ #
left, right = st.columns(2)
with left:
    st.subheader("Your resume")
    resume_text = ui.resume_loader()
with right:
    st.subheader("Target job")
    # Same key as the Analyzer page, so the job description is shared between them.
    job_text = ui.persistent(
        st.text_area, "Job description", "job_text_input", "", height=220,
        label_visibility="collapsed", placeholder="Paste the job description here...",
    )

# ------------------------------ Ollama setup -------------------------------- #
with st.expander("Ollama settings", expanded=not st.session_state.get("_ollama_ok")):
    host = st.text_input("Ollama address", value=ai.normalize_host(None), key="ollama_host")
    models, error = check_ollama(host)
    st.session_state["_ollama_ok"] = error is None

    if error:
        st.error(error)
        st.markdown(
            "**Set up local AI (free, runs on your machine):**\n"
            "1. Install Ollama from https://ollama.com\n"
            "2. `ollama pull llama3.2`  (chat model)\n"
            "3. `ollama pull nomic-embed-text`  (embedding model)\n"
            "4. Make sure Ollama is running, then reload this page."
        )
        chat_model = embed_model = None
    else:
        default_chat, default_embed = ai.pick_defaults(models)
        embedding_models = [m for m in models if "embed" in m.lower()]
        chat_models = [m for m in models if m not in embedding_models]
        c1, c2 = st.columns(2)
        with c1:
            chat_model = pick("Chat model", chat_models, default_chat, "chat_model")
        with c2:
            embed_model = pick("Embedding model", embedding_models, default_embed, "embed_model")
        if not chat_models:
            st.warning("No chat model installed. Run `ollama pull llama3.2`.")
        if ai.is_local_host(host):
            st.caption("Running locally: your resume text stays on your machine.")
        else:
            st.warning(f"{host} is not on this machine. Your resume text will be sent to it.")

if error:
    st.stop()
if not resume_text:
    st.info("Load your resume above to use the AI Coach.")
    st.stop()

client = OllamaClient(host, timeout=180)


def llm(system: str, user: str, temperature: float = 0.2) -> str:
    return client.chat(chat_model, system, user, temperature=temperature)


def need_job() -> bool:
    if job_text.strip():
        return False
    st.info("Paste a job description above to use this tool.")
    return True


analysis = analyze_resume(resume_text, job_text) if job_text.strip() else None

tab_rewrite, tab_semantic, tab_summary, tab_interview = st.tabs(
    ["Bullet rewriter", "Semantic match", "Fit summary", "Interview prep"]
)

# ------------------------------ bullet rewriter ------------------------------ #
with tab_rewrite:
    st.caption(
        "Improves wording using only facts already in your bullet. Every suggestion is fact-checked: "
        "new numbers or skills are flagged. Missing metrics appear as [placeholders] for you to fill in."
    )
    bullets = ai.candidate_bullets(resume_text)
    choice = st.selectbox("Pick a bullet", bullets, format_func=shorten) if bullets else None
    custom = st.text_area("…or paste a bullet", height=80, key="custom_bullet")
    bullet = custom.strip() or choice

    if st.button("Rewrite bullet", disabled=not bullet or not chat_model):
        targets = list(analysis["job"])[:10] if analysis else []
        try:
            with st.spinner("Rewriting..."):
                st.session_state["ai_rewrite"] = ai.rewrite_bullet(bullet, targets, llm)
        except OllamaError as exc:
            st.error(str(exc))

    result = st.session_state.get("ai_rewrite")
    if result:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Original**")
            st.code(result["original"], language=None)
        with c2:
            st.markdown("**Suggestion**")
            st.code(result["rewrite"], language=None)
        if result["problems"]:
            for problem in result["problems"]:
                st.warning(f"Check before using: {problem}")
        else:
            st.success("Passed the fact check: no new numbers or skills were added.")
        if "[" in result["rewrite"]:
            st.info("Replace each [placeholder] with a real number, or delete it. Never guess a metric.")

# ------------------------------ semantic matching ----------------------------- #
with tab_semantic:
    st.caption(
        "Keyword matching misses synonyms, like “built REST services” vs “API development”. "
        "This compares meaning using embeddings. It is a reading aid: your scores do not change."
    )
    if not need_job():
        if not embed_model:
            st.warning("No embedding model installed. Run `ollama pull nomic-embed-text`.")
        else:
            with st.expander("Sensitivity (depends on the embedding model)"):
                strong = st.slider("Strong match at or above", 0.30, 0.95, 0.62, 0.01)
                partial = st.slider("Partial match at or above", 0.20, 0.90, 0.50, 0.01)

            requirements = ai.extract_requirements(job_text)
            items = ai.candidate_bullets(resume_text)
            st.caption(f"{len(requirements)} requirements found · {len(items)} resume bullets")

            if st.button("Run semantic match", disabled=not requirements or not items or partial >= strong):
                try:
                    with st.spinner("Comparing meaning..."):
                        st.session_state["ai_semantic"] = ai.semantic_match(
                            requirements, items, lambda texts: client.embed(embed_model, texts),
                            strong=strong, partial=partial,
                        )
                except OllamaError as exc:
                    st.error(str(exc))
            if partial >= strong:
                st.warning("The partial threshold must be lower than the strong threshold.")

            semantic = st.session_state.get("ai_semantic")
            if semantic:
                groups = ai.categorize(semantic)
                st.markdown(
                    ui.stat_row([
                        ("Strong", sum(r["label"] == "strong" for r in semantic)),
                        ("Partial", sum(r["label"] == "partial" for r in semantic)),
                        ("No clear support", len(groups["unsupported"])),
                    ]),
                    unsafe_allow_html=True,
                )

                st.subheader("Found by meaning, missed by keywords")
                if not groups["by_meaning"]:
                    st.caption("Nothing extra: keyword matching already covers what matches.")
                for r in groups["by_meaning"]:
                    st.markdown(f"**{ui.md_escape(r['requirement'])}**")
                    st.caption(f"Closest resume line ({r['similarity']}, {r['label']}): “{r['best_item']}”")

                st.subheader("No clear support in your resume")
                if not groups["unsupported"]:
                    st.caption("Every requirement has at least a partial match.")
                for r in groups["unsupported"]:
                    st.markdown(f"**{ui.md_escape(r['requirement'])}**")
                    st.caption(f"Closest line was only {r['similarity']} similar: “{shorten(r['best_item'])}”")

# ------------------------------- fit summary -------------------------------- #
with tab_summary:
    st.caption(
        "A plain-language explanation of your deterministic analysis. The AI only sees the facts below "
        "and any skill it mentions outside them is flagged."
    )
    if not need_job():
        if analysis["score"] is None:
            st.warning("No supported skills were detected in this job description.")
        elif st.button("Explain my fit", disabled=not chat_model):
            try:
                with st.spinner("Writing summary..."):
                    st.session_state["ai_summary"] = ai.fit_summary(analysis, llm)
            except OllamaError as exc:
                st.error(str(exc))

        summary = st.session_state.get("ai_summary")
        if summary:
            for problem in summary["problems"]:
                st.warning(f"Check this summary: {problem}")
            st.markdown(summary["summary"])
            st.caption("Written by a local AI from your analysis. Your scores above are unchanged.")
            with st.expander("What the AI was given"):
                st.json(summary["facts"])

# ------------------------------ interview prep ------------------------------ #
with tab_interview:
    st.caption("Practice questions that probe the skills you are missing or have not yet proven.")
    if not need_job():
        count = st.slider("Number of questions", 3, 10, 6)
        if st.button("Generate questions", disabled=not chat_model):
            try:
                with st.spinner("Writing questions..."):
                    st.session_state["ai_questions"] = ai.interview_questions(
                        analysis, job_text, lambda s, u: llm(s, u, temperature=0.6), n=count
                    )
            except OllamaError as exc:
                st.error(str(exc))

        questions = st.session_state.get("ai_questions")
        if questions:
            if questions["focus"]:
                st.caption("Focus skills: " + ", ".join(questions["focus"]))
            for number, question in enumerate(questions["questions"], start=1):
                st.markdown(f"**{number}.** {ui.md_escape(question)}")
            st.caption("Answer honestly: for a skill you lack, explain how you would learn it.")
