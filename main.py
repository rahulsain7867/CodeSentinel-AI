# main.py
import os
import uvicorn
from fastapi.staticfiles import StaticFiles
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.artifacts import InMemoryArtifactService 

from fastapi import Request

# Get credentials from environment variables
from code_review_assistant.history_service import HistoryService
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
CLOUD_SQL_CONNECTION_NAME = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
ARTIFACT_BUCKET = os.environ.get("ARTIFACT_BUCKET")


def _is_valid_session_uri(uri: str) -> bool:
    candidate = uri.strip()
    return bool(candidate) and candidate not in {"vertexai://"}


def _get_session_service_uri() -> str:
    explicit_uri = os.getenv("SESSION_SERVICE_URI", "")
    if _is_valid_session_uri(explicit_uri):
        return explicit_uri.strip()

    if all([DB_USER, DB_PASSWORD, DB_NAME, CLOUD_SQL_CONNECTION_NAME]):
        return (
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}"
            f"?host=/cloudsql/{CLOUD_SQL_CONNECTION_NAME}"
        )

    return "sqlite:///./sessions.db"


def _get_artifact_service_uri() -> str:
    explicit_uri = os.getenv("ARTIFACT_SERVICE_URI", "").strip()
    if explicit_uri.startswith("gs://") and explicit_uri != "gs://":
        return explicit_uri.strip()

    if ARTIFACT_BUCKET and ARTIFACT_BUCKET.strip():
        return f"gs://{ARTIFACT_BUCKET.strip()}"

    return ""


SESSION_SERVICE_URI = _get_session_service_uri()
ARTIFACT_SERVICE_URI = _get_artifact_service_uri()

# Create the FastAPI app with ADK
app = get_fast_api_app(
    agents_dir=os.path.dirname(os.path.abspath(__file__)),
    session_service_uri=os.getenv("SESSION_SERVICE_URI", "sqlite:///./sessions.db"),
    artifact_service_uri=os.getenv("ARTIFACT_SERVICE_URI", "file:///app/artifacts"),
    allow_origins=["*"],
    web=True,
    trace_to_cloud=False
)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "frontend"), html=True))

@app.get("/api/dashboard")
async def api_dashboard():
    service = HistoryService()
    return service.get_dashboard_analytics()

@app.get("/api/history")
async def api_history(limit: int = 50):
    service = HistoryService()
    return service.get_review_history(limit=limit)

@app.get("/api/trends")
async def api_trends():
    service = HistoryService()
    return service.get_quality_trend()

@app.get("/api/recurring-issues")
async def api_recurring_issues():
    service = HistoryService()
    return service.get_recurring_issues()

@app.post("/api/review")
async def api_review(request: Request):
    payload = await request.json()
    # Placeholder: invoke review pipeline
    return {"status": "queued"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
