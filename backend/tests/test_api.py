import pytest
from fastapi.testclient import TestClient

from app.core import settings
from app.designs import DESIGNS, FUNDAMENTALS, Design
from app.main import app

# No `with` block: the lifespan (Mongo indexes + seeding) never runs, so only requests
# rejected before touching the database are testable here.
client = TestClient(app, base_url="http://localhost")
SESSION = "0123456789abcdef01234567"


@pytest.mark.parametrize("path", ["/api/sessions/not-an-id/stats", "/api/sessions/123/problems/two-sum/submissions"])
def test_malformed_session_id_is_404(path: str) -> None:
    resp = client.get(path)
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Session not found"}


def test_unknown_problem_is_404() -> None:
    resp = client.get("/api/problems/no-such-problem")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Problem not found"}


@pytest.mark.parametrize(
    "body",
    [
        {"code": "x" * (settings.max_code_bytes + 1), "cases": [[1]]},
        {"code": "pass", "cases": []},
        {"code": "pass", "cases": [[1]] * (settings.max_custom_cases + 1)},
    ],
)
def test_run_rejects_oversized_or_empty_input(body: dict[str, object]) -> None:
    assert client.post(f"/api/sessions/{SESSION}/problems/two-sum/run", json=body).status_code == 422


def test_create_session_validates_target() -> None:
    assert client.post("/api/sessions", json={"name": "x", "target": "amazon"}).status_code == 422


def test_unknown_host_is_rejected() -> None:
    assert TestClient(app, base_url="http://attacker.example").get("/api/problems").status_code == 400


def test_submissions_limit_must_be_positive() -> None:
    assert client.get(f"/api/sessions/{SESSION}/problems/two-sum/submissions?limit=0").status_code == 422


def test_designs_list_every_question() -> None:
    slugs = [d["slug"] for d in client.get("/api/designs").json()]
    assert slugs == [d.slug for d in DESIGNS]
    assert len(set(slugs)) == len(slugs)


def test_design_detail_hides_the_rubric() -> None:
    body = client.get("/api/designs/rate-limiter").json()
    assert body["title"] == "Distributed rate limiter"
    assert body["scene"] is None and body["notes"] == ""
    assert "rubric" not in body


def test_unknown_design_is_404() -> None:
    assert client.get("/api/designs/no-such-design").status_code == 404


@pytest.mark.parametrize("d", DESIGNS, ids=lambda d: d.slug)
def test_design_links_only_known_fundamentals(d: Design) -> None:
    assert d.fundamentals and set(d.fundamentals) <= set(FUNDAMENTALS)
    assert d.functional and d.non_functional and d.scale and d.rubric


def test_design_draft_rejects_oversized_scene() -> None:
    body = {"scene": "x" * (settings.max_scene_bytes + 1)}
    assert client.put(f"/api/sessions/{SESSION}/designs/url-shortener/draft", json=body).status_code == 422
