"""Local-LLM helpers (Ollama). Standard library only, no Streamlit imports.

Design rules:
  * Scores never come from the model. They stay deterministic (see analyzer.py).
  * Every model output is checked against facts from the deterministic analysis,
    so the model cannot add numbers or skills that are not already there.
  * Model calls are passed in as plain callables, which keeps everything testable.
"""

from __future__ import annotations

import json
import math
import os
import re
import urllib.error
import urllib.request
from urllib.parse import urlparse

from analyzer import (
    BULLET_CHARS,
    EVIDENCE_SECTIONS,
    LABEL_LINE,
    find_skills,
    split_resume_items,
)

DEFAULT_HOST = "http://localhost:11434"


class OllamaError(Exception):
    """A problem talking to Ollama, with a message that is safe to show users."""


# --------------------------------------------------------------------------- #
# Ollama client
# --------------------------------------------------------------------------- #

def normalize_host(host: str | None = None) -> str:
    host = (host or "").strip() or os.environ.get("OLLAMA_HOST", "").strip() or DEFAULT_HOST
    if not re.match(r"^https?://", host):
        host = "http://" + host
    return host.rstrip("/")


def is_local_host(host: str) -> bool:
    return (urlparse(normalize_host(host)).hostname or "") in {
        "localhost", "127.0.0.1", "::1", "0.0.0.0",
    }


class OllamaClient:
    def __init__(self, host: str | None = None, timeout: float = 120):
        self.host = normalize_host(host)
        self.timeout = timeout

    def _request(self, path: str, payload: dict | None = None) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.host + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="GET" if payload is None else "POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = json.loads(exc.read().decode("utf-8")).get("error", "")
            except Exception:
                pass
            model = (payload or {}).get("model")
            if exc.code == 404 and model:
                raise OllamaError(
                    f"Model '{model}' is not installed. Run: ollama pull {model}"
                ) from exc
            raise OllamaError(detail or f"Ollama returned HTTP {exc.code}.") from exc
        except urllib.error.URLError as exc:
            raise OllamaError(
                f"Could not reach Ollama at {self.host}. Is it installed and running?"
            ) from exc
        except TimeoutError as exc:
            raise OllamaError(
                "Ollama took too long to respond. Try a smaller model or run it again."
            ) from exc
        except json.JSONDecodeError as exc:
            raise OllamaError("Ollama sent a response that could not be understood.") from exc

    def list_models(self) -> list[str]:
        data = self._request("/api/tags")
        return [m["name"] for m in data.get("models", []) if "name" in m]

    def chat(self, model: str, system: str, user: str, temperature: float = 0.2) -> str:
        data = self._request("/api/chat", {
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {"temperature": temperature},
        })
        text = ((data.get("message") or {}).get("content") or "").strip()
        if not text:
            raise OllamaError("The model returned an empty response.")
        return text

    def embed(self, model: str, texts: list[str]) -> list[list[float]]:
        data = self._request("/api/embed", {"model": model, "input": texts})
        vectors = data.get("embeddings") or []
        if len(vectors) != len(texts):
            raise OllamaError(
                f"Model '{model}' did not return embeddings. "
                "Try an embedding model such as nomic-embed-text."
            )
        return vectors


def pick_defaults(models: list[str]) -> tuple[str | None, str | None]:
    """Choose sensible (chat_model, embedding_model) from installed models."""
    embedding = [m for m in models if "embed" in m.lower()]
    chat = [m for m in models if m not in embedding]
    chat_default = None
    for prefix in ("llama3.2", "llama3.1", "llama3", "qwen2.5", "mistral", "gemma"):
        chat_default = next((m for m in chat if m.lower().startswith(prefix)), None)
        if chat_default:
            break
    return chat_default or (chat[0] if chat else None), (embedding[0] if embedding else None)


# --------------------------------------------------------------------------- #
# 1. Grounded bullet rewriting
# --------------------------------------------------------------------------- #
REWRITE_SYSTEM = (
    "You improve resume bullet points.\n"
    "Rules:\n"
    "- Use ONLY facts stated in the original bullet.\n"
    "- Never add numbers, tools, technologies, employers, or outcomes that are not in the original.\n"
    "- If a metric would help but is missing, insert a placeholder in square brackets, "
    "like [X%] or [number of users], for the candidate to fill in.\n"
    "- Start with a strong past-tense action verb. Keep it under 30 words.\n"
    "- Mention a target skill only if the original bullet already involves it.\n"
    "Return ONLY the rewritten bullet: no quotes, no explanation."
)

_NUMBER = re.compile(r"\d+(?:\.\d+)?")


def _strip_placeholders(text: str) -> str:
    return re.sub(r"\[[^\]]*\]", " ", text)


def _numbers(text: str) -> set[str]:
    return set(_NUMBER.findall(_strip_placeholders(text).replace(",", "")))


def check_rewrite(original: str, rewrite: str) -> list[str]:
    """Deterministic fact check: what did the rewrite add that was not in the original?"""
    if not rewrite.strip():
        return ["The rewrite is empty."]
    problems = []
    new_numbers = sorted(_numbers(rewrite) - _numbers(original))
    if new_numbers:
        problems.append("Adds numbers that are not in the original: " + ", ".join(new_numbers) + ".")
    new_skills = sorted(set(find_skills(_strip_placeholders(rewrite))) - set(find_skills(original)))
    if new_skills:
        problems.append("Mentions skills that are not in the original: " + ", ".join(new_skills) + ".")
    if len(rewrite.split()) > 45:
        problems.append("Too long for a resume bullet.")
    return problems


def clean_bullet_output(text: str) -> str:
    """Take the first real line and strip labels, bullets, and quotes."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^(?:rewritten(?: bullet)?|improved(?: bullet)?|suggestion)\s*:\s*", "", line, flags=re.I)
        line = line.lstrip(BULLET_CHARS + " \t").strip()
        return line.strip("\"'“”‘’ ")
    return ""


def rewrite_bullet(bullet: str, target_skills: list[str], llm, max_attempts: int = 2) -> dict:
    """Rewrite one bullet. llm(system, user) -> str. Retries once with the fact-check feedback."""
    bullet = bullet.strip()
    feedback = ""
    result: dict = {}
    for attempt in range(1, max_attempts + 1):
        user = (
            f"Original bullet:\n{bullet}\n\n"
            f"Target job skills (mention one only if the bullet already involves it): "
            f"{', '.join(target_skills) or 'none'}"
        )
        if feedback:
            user += f"\n\nYour previous attempt was rejected: {feedback} Fix this."
        rewrite = clean_bullet_output(llm(REWRITE_SYSTEM, user))
        problems = check_rewrite(bullet, rewrite)
        result = {"original": bullet, "rewrite": rewrite, "problems": problems, "attempts": attempt}
        if not problems:
            break
        feedback = " ".join(problems)
    return result


def candidate_bullets(resume_text: str, limit: int = 40) -> list[str]:
    """Resume lines that look like experience/project bullets."""
    bullets = []
    for section, text in split_resume_items(resume_text):
        if LABEL_LINE.match(text):
            continue
        words = len(text.split())
        if (section in EVIDENCE_SECTIONS and words >= 5) or (section == "other" and words >= 8):
            bullets.append(text)
    return bullets[:limit]


# --------------------------------------------------------------------------- #
# 2. Semantic matching (embeddings): meaning, not just keywords
# --------------------------------------------------------------------------- #
_REQ_CUES = re.compile(
    r"experience|proficien|knowledge|familiar|ability|skilled|skills?|understanding|"
    r"expertise|build|develop|design|implement|manage|maintain|collaborat|"
    r"years|strong|degree|must|should",
    re.I,
)


def extract_requirements(job_text: str, max_items: int = 40) -> list[str]:
    """Pull requirement-like lines out of a job description."""
    requirements, seen = [], set()
    for chunk in re.split(r"[\r\n]+|(?<=[.!?])\s+", job_text):
        stripped = chunk.strip()
        if not stripped:
            continue
        bulleted = stripped[0] in BULLET_CHARS
        line = stripped.lstrip(BULLET_CHARS + " \t").strip()
        if not 4 <= len(line.split()) <= 40:
            continue
        if not (bulleted or _REQ_CUES.search(line) or find_skills(line)):
            continue
        key = line.lower()
        if key not in seen:
            seen.add(key)
            requirements.append(line)
    return requirements[:max_items]


def _unit(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vector))
    return [x / norm for x in vector] if norm else list(vector)


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def semantic_match(requirements: list[str], items: list[str], embed,
                   strong: float = 0.62, partial: float = 0.50) -> list[dict]:
    """For each requirement, find the closest resume line by meaning.

    embed(list[str]) -> list[list[float]]. Thresholds depend on the embedding model,
    so the UI lets the user adjust them.
    """
    if not requirements or not items:
        return []
    texts = [t[:500] for t in requirements + items]
    vectors = embed(texts)
    if len(vectors) != len(texts):
        raise OllamaError("The embedding model returned the wrong number of vectors.")

    req_vecs = [_unit(v) for v in vectors[: len(requirements)]]
    item_vecs = [_unit(v) for v in vectors[len(requirements):]]

    results = []
    for requirement, rvec in zip(requirements, req_vecs):
        best_index, best = max(
            ((i, _dot(rvec, ivec)) for i, ivec in enumerate(item_vecs)), key=lambda p: p[1]
        )
        label = "strong" if best >= strong else "partial" if best >= partial else "none"
        results.append({
            "requirement": requirement,
            "best_item": items[best_index],
            "similarity": round(best, 2),
            "label": label,
            "keyword_skills": sorted(find_skills(requirement)),
        })
    return results


def categorize(results: list[dict]) -> dict:
    return {
        # Matched by meaning even though no catalog keyword appears in the requirement.
        "by_meaning": [r for r in results if r["label"] != "none" and not r["keyword_skills"]],
        # No resume line comes close to this requirement.
        "unsupported": [r for r in results if r["label"] == "none"],
    }


# --------------------------------------------------------------------------- #
# 3. Fit summary: plain-language explanation of the deterministic analysis
# --------------------------------------------------------------------------- #
SUMMARY_SYSTEM = (
    "You write a short, honest fit summary (at most 4 sentences) for a job seeker.\n"
    "Use ONLY the facts provided. Do not mention any skill that is not in the facts. "
    "Do not predict hiring outcomes. Be encouraging but truthful, and end with the single "
    "most useful next step."
)


def build_fit_facts(analysis: dict) -> dict:
    job, unproven = analysis["job"], set(analysis["unproven"])
    return {
        "keyword_match_percent": analysis["score"],
        "evidence_backed_match_percent": analysis["evidence_score"],
        "matched_and_proven": [s for s in analysis["matched"] if s not in unproven],
        "listed_but_unproven": analysis["unproven"],
        "missing_required": [s for s in analysis["missing"] if job[s]["level"] == "required"],
        "missing_nice_to_have": [s for s in analysis["missing"] if job[s]["level"] != "required"],
        "extra_strengths": analysis["extra"][:8],
    }


def fit_summary(analysis: dict, llm, max_attempts: int = 2) -> dict:
    facts = build_fit_facts(analysis)
    allowed = set(analysis["job"]) | set(analysis["resume_skills"])
    feedback, result = "", {}
    for attempt in range(1, max_attempts + 1):
        user = "Facts (JSON):\n" + json.dumps(facts, indent=2)
        if feedback:
            user += f"\n\nYour previous attempt was rejected: {feedback} Fix this."
        text = llm(SUMMARY_SYSTEM, user).strip()
        extra = sorted(set(find_skills(text)) - allowed)
        problems = [f"Mentions skills that are not in the facts: {', '.join(extra)}."] if extra else []
        result = {"summary": text, "problems": problems, "facts": facts, "attempts": attempt}
        if not problems:
            break
        feedback = " ".join(problems)
    return result


# --------------------------------------------------------------------------- #
# 4. Interview practice questions
# --------------------------------------------------------------------------- #
INTERVIEW_SYSTEM = (
    "You are an experienced interviewer. Write practice interview questions for a candidate. "
    "Mix technical and behavioral questions, and probe the focus skills in a way that lets the "
    "candidate answer honestly about what they have and have not done. "
    "Output one question per line, numbered, with no other text."
)


def parse_questions(text: str, limit: int) -> list[str]:
    """Prefer numbered/bulleted lines (we ask for them); ignore preamble like 'Here are...'."""
    prefix = re.compile(r"^\s*(?:\d+[.)]|[-*•])\s*")
    listed, plain = [], []
    for raw in text.splitlines():
        line = prefix.sub("", raw).strip()
        if len(line) < 15:
            continue
        (listed if prefix.match(raw) else plain).append(line)
    questions = listed or [l for l in plain if "?" in l] or plain
    return questions[:limit]


def interview_questions(analysis: dict, job_text: str, llm, n: int = 6) -> dict:
    focus = []
    for skill in analysis["missing"][:3] + analysis["unproven"][:3]:
        if skill not in focus:
            focus.append(skill)
    user = (
        f"Job description excerpt:\n{job_text.strip()[:1500]}\n\n"
        f"Focus skills: {', '.join(focus) or 'general fit for the role'}\n\n"
        f"Write {n} questions."
    )
    questions = parse_questions(llm(INTERVIEW_SYSTEM, user), n)
    if not questions:
        raise OllamaError("The model did not return any questions. Try again.")
    return {"questions": questions, "focus": focus}
