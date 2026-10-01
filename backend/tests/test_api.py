import pytest
from fastapi.testclient import TestClient

from app.core import settings
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
