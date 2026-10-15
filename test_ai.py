import json
import socket
import threading
import zlib
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer

import ai
from analyzer import analyze_resume
from test_analyzer import RESUME


# ---------------------------- fake Ollama server ---------------------------- #
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/tags":
            self._send(200, {"models": [{"name": "llama3.2:latest"}, {"name": "nomic-embed-text:latest"}]})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/api/chat":
            if body["model"] == "missing":
                self._send(404, {"error": "model 'missing' not found"})
            elif body["model"] == "empty":
                self._send(200, {"message": {"content": "  "}})
            else:
                self._send(200, {"message": {"content": "echo: " + body["messages"][-1]["content"]}})
        elif self.path == "/api/embed":
            self._send(200, {"embeddings": [[1.0, 0.0] for _ in body["input"]]})
        else:
            self._send(404, {"error": "not found"})


@contextmanager
def fake_ollama():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()


def raises_ollama_error(fn):
    try:
        fn()
    except ai.OllamaError as exc:
        return str(exc)
    raise AssertionError("expected OllamaError")


# --------------------------------- client ---------------------------------- #
def test_client_against_fake_server():
    with fake_ollama() as host:
        client = ai.OllamaClient(host, timeout=5)
        assert client.list_models() == ["llama3.2:latest", "nomic-embed-text:latest"]
        assert client.chat("llama3.2", "sys", "hello").startswith("echo:")
        assert client.embed("nomic-embed-text", ["a", "b"]) == [[1.0, 0.0], [1.0, 0.0]]


def test_client_friendly_errors():
    with fake_ollama() as host:
        client = ai.OllamaClient(host, timeout=5)
        assert "ollama pull missing" in raises_ollama_error(lambda: client.chat("missing", "s", "u"))
        assert "empty" in raises_ollama_error(lambda: client.chat("empty", "s", "u"))

    sock = socket.socket(); sock.bind(("127.0.0.1", 0)); port = sock.getsockname()[1]; sock.close()
    dead = ai.OllamaClient(f"127.0.0.1:{port}", timeout=2)  # scheme added automatically
    assert "Could not reach Ollama" in raises_ollama_error(dead.list_models)


def test_host_helpers_and_defaults():
    assert ai.normalize_host("localhost:11434") == "http://localhost:11434"
    assert ai.is_local_host("http://localhost:11434") and not ai.is_local_host("https://example.com")
    chat, embed = ai.pick_defaults(["nomic-embed-text:latest", "mistral:7b", "llama3.2:latest"])
    assert (chat, embed) == ("llama3.2:latest", "nomic-embed-text:latest")
    assert ai.pick_defaults(["nomic-embed-text"]) == (None, "nomic-embed-text")


# ----------------------------- bullet rewriting ----------------------------- #
ORIGINAL = "Built a FastAPI service handling 2,000 requests per day"


def test_check_rewrite_catches_invented_facts():
    ok = "Built a FastAPI service handling 2000 requests per day, reducing latency by [X%]"
    assert ai.check_rewrite(ORIGINAL, ok) == []                       # placeholders and 2,000 vs 2000 are fine
    bad = "Built a FastAPI service handling 2000 requests per day, cutting latency 40% with Docker"
    problems = ai.check_rewrite(ORIGINAL, bad)
    assert any("40" in p for p in problems) and any("Docker" in p for p in problems)


def test_rewrite_retries_with_feedback_then_passes():
    calls = []

    def llm(system, user):
        calls.append(user)
        if len(calls) == 1:
            return '"Rewritten: Engineered a FastAPI service for 5000 requests per day."'
        return "- Engineered a FastAPI service handling 2000 requests per day"

    result = ai.rewrite_bullet(ORIGINAL, ["FastAPI", "Docker"], llm)
    assert result["attempts"] == 2 and result["problems"] == []
    assert result["rewrite"].startswith("Engineered")
    assert "rejected" in calls[1] and "5000" in calls[1]               # feedback reached the model


def test_rewrite_that_keeps_failing_is_flagged_not_hidden():
    result = ai.rewrite_bullet(ORIGINAL, [], lambda s, u: "Built it with Docker for 99 users")
    assert result["attempts"] == 2 and result["problems"]


def test_candidate_bullets_come_from_experience_and_projects():
    bullets = ai.candidate_bullets(RESUME)
    assert any("FastAPI" in b for b in bullets)
    assert not any(b.startswith("Python, SQL") for b in bullets)       # skills list excluded


# ---------------------------- semantic matching ----------------------------- #
def fake_embed(texts):
    vectors = []
    for text in texts:
        vec = [0.0] * 256
        for word in text.lower().replace(",", " ").split():
            word = word.rstrip("s")
            vec[zlib.crc32(word.encode()) % 256] += 1
        vectors.append(vec)
    return vectors


def test_extract_requirements_drops_headings_and_boilerplate():
    jd = "Requirements:\n- Experience building REST services at scale\nNice to have:\nWe are a friendly team of dreamers and doers."
    reqs = ai.extract_requirements(jd)
    assert reqs == ["Experience building REST services at scale"]


def test_semantic_match_and_categories():
    reqs = ["Experience building REST services at scale", "Knowledge of Kubernetes orchestration"]
    items = ["Built REST service handling 2000 requests per day", "Wrote data pipelines in Pandas"]
    results = ai.semantic_match(reqs, items, fake_embed, strong=0.25, partial=0.15)
    assert [r["label"] for r in results] == ["strong", "none"]
    assert results[0]["best_item"] == items[0] and results[1]["keyword_skills"] == ["Kubernetes"]
    cats = ai.categorize(results)
    assert [r["requirement"] for r in cats["by_meaning"]] == [reqs[0]]  # no catalog keyword, matched by meaning
    assert [r["requirement"] for r in cats["unsupported"]] == [reqs[1]]


def test_semantic_match_handles_empty_input_and_bad_embedder():
    assert ai.semantic_match([], ["x"], fake_embed) == []
    raises_ollama_error(lambda: ai.semantic_match(["a b c d"], ["x"], lambda texts: [[1.0]]))


# --------------------------- summary and questions --------------------------- #
def test_fit_summary_rejects_skills_outside_the_facts():
    analysis = analyze_resume(RESUME, "Requirements: Python, Docker, Kubernetes")
    replies = iter([
        "You match Python well, and your Redis work stands out.",        # Redis is not in the facts
        "You match Python well; prove Docker and learn Kubernetes next.",
    ])
    result = ai.fit_summary(analysis, lambda s, u: next(replies))
    assert result["attempts"] == 2 and result["problems"] == []
    facts = result["facts"]
    assert facts["missing_required"] == ["Kubernetes"] and facts["listed_but_unproven"] == ["Docker"]


def test_interview_questions_parsing_and_focus():
    analysis = analyze_resume(RESUME, "Requirements: Python, Docker, Kubernetes")
    reply = "Here are some questions:\n1. How would you deploy a service with Kubernetes?\n2) Tell me about a Docker image you built.\n- Short?"
    result = ai.interview_questions(analysis, "Requirements: Python, Docker, Kubernetes", lambda s, u: reply, n=5)
    assert result["questions"] == [
        "How would you deploy a service with Kubernetes?",
        "Tell me about a Docker image you built.",
    ]
    assert result["focus"] == ["Kubernetes", "Docker"]
    raises_ollama_error(lambda: ai.interview_questions(analysis, "x", lambda s, u: "ok", n=3))
