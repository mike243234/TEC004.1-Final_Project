"""
api/ai_routes.py
------------------
FastAPI endpoints that expose the AI features to your existing dashboard.

Mount this router in your main app file, e.g.:

    from api.ai_routes import router as ai_router
    app.include_router(ai_router, prefix="/api/ai")

That gives you:
    GET  /api/ai/similar-jobs/{job_id}   -> jobs similar to one job
    POST /api/ai/recommend               -> jobs matching a free-text profile
    POST /api/ai/embeddings/backfill     -> embed any jobs missing one
    GET  /api/ai/insights/latest         -> narrative market summary
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai.embeddings import backfill_embeddings, recommend_for_profile, recommend_similar_jobs
from ai.insights import generate_market_insight

router = APIRouter()

DB_PATH = "jobs.db"  # TODO: point this at your existing database path / settings module


class ProfileQuery(BaseModel):
    profile_text: str
    top_k: int = 10


@router.get("/similar-jobs/{job_id}")
def similar_jobs(job_id: int, top_k: int = 5):
    try:
        results = recommend_similar_jobs(DB_PATH, job_id, top_k)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return [{"job_id": jid, "score": round(score, 4)} for jid, score in results]


@router.post("/recommend")
def recommend(query: ProfileQuery):
    results = recommend_for_profile(DB_PATH, query.profile_text, query.top_k)
    return [{"job_id": jid, "score": round(score, 4)} for jid, score in results]


@router.post("/embeddings/backfill")
def run_backfill():
    count = backfill_embeddings(DB_PATH)
    return {"embedded": count}


@router.get("/insights/latest")
def latest_insight():
    # TODO: replace this stub with a real aggregation query against your
    # jobs table (skill frequency, salary trend, etc.) -- whatever your
    # existing analytics module already computes.
    stats = {
        "period": "last 7 days",
        "total_new_postings": 0,
        "top_skills": [],
        "avg_salary_change_pct": 0,
        "top_hiring_companies": [],
    }
    narrative = generate_market_insight(stats)
    return {"narrative": narrative, "stats": stats}
