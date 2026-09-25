"""Settings, Mongo connection and the sandbox runner client."""
import os
from datetime import datetime, timezone

import httpx
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class Settings:
    mongo_url: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    mongo_db: str = os.environ.get("MONGO_DB", "kodetrain")
    runner_url: str = os.environ.get("RUNNER_URL", "http://localhost:8080")
    runner_token: str = os.environ.get("RUNNER_TOKEN", "")
    cors_origins: list[str] = [o for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",") if o]
    max_code_bytes: int = 64 * 1024
    max_custom_cases: int = 10


settings = Settings()
_client: AsyncIOMotorClient | None = None


def db() -> AsyncIOMotorDatabase:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_url, tz_aware=True)
    return _client[settings.mongo_db]


async def ensure_indexes() -> None:
    d = db()
    await d.submissions.create_index([("session_id", 1), ("problem", 1), ("created_at", -1)])
    await d.submissions.create_index([("session_id", 1), ("created_at", -1)])
    await d.progress.create_index([("session_id", 1), ("problem", 1)], unique=True)
    await d.drafts.create_index([("session_id", 1), ("problem", 1)], unique=True)


def now() -> datetime:
    return datetime.now(timezone.utc)


class RunnerError(RuntimeError):
    pass


_http: httpx.AsyncClient | None = None


async def run_in_sandbox(job: dict) -> dict:
    """POST a job to the isolated runner service. The runner enforces all limits; we only add a network timeout."""
    global _http
    if _http is None:
        _http = httpx.AsyncClient(base_url=settings.runner_url, timeout=httpx.Timeout(60.0, connect=5.0))
    try:
        resp = await _http.post("/run", json=job, headers={"X-Runner-Token": settings.runner_token})
    except httpx.HTTPError as e:
        raise RunnerError(f"Code runner unavailable: {e}") from e
    if resp.status_code == 503:
        raise RunnerError("All sandboxes are busy. Try again in a moment.")
    if resp.status_code != 200:
        raise RunnerError(f"Code runner error ({resp.status_code})")
    return resp.json()
