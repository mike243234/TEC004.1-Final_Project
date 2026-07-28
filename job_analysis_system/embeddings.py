"""
ai/embeddings.py
-----------------
Turns job postings (and free-text user queries or resumes) into numeric
vectors -- "embeddings" -- so jobs can be ranked by *meaning* instead of
exact keyword overlap. This module is what powers the recommendation
engine.

TERMS, PLAIN-ENGLISH VERSION:
  - Embedding: a list of ~384 numbers that represents what a piece of
    text is *about*. Two texts about similar things end up with similar
    numbers, even if they don't share a single word in common (e.g.
    "backend developer" and "server-side engineer" land close together).
  - Cosine similarity: a score from -1 to 1 measuring how closely two
    embeddings point in the same direction. 1 = same meaning, 0 =
    unrelated, -1 = opposite. Under the hood it's just the angle between
    two vectors -- when both vectors are length-normalized, it's the same
    as taking their dot product, which is why the code below can just do
    `vectors @ query_vec` instead of anything fancier.

MODEL: sentence-transformers/all-MiniLM-L6-v2
  - Free, open-source, ~80MB. Downloads once the first time you run this,
    then works fully offline.
  - Small but strong general-purpose semantic search quality -- the
    standard "good default" for student projects and production systems
    that don't need the biggest model available.

SETUP:  pip install sentence-transformers numpy --break-system-packages
"""

import sqlite3
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None  # lazy-loaded singleton -- loading the model takes a couple
               # of seconds, so we only want to do it once per process


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_text(text: str) -> np.ndarray:
    # normalize_embeddings=True makes cosine similarity equal to a plain
    # dot product, which is much cheaper to compute across thousands of
    # jobs than the full cosine similarity formula.
    return get_model().encode(text, normalize_embeddings=True)


def embed_and_store(db_path: str, job_id: int, description: str) -> None:
    vector = embed_text(description)
    blob = vector.astype(np.float32).tobytes()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """INSERT INTO job_embeddings (job_id, embedding, model_name)
               VALUES (?, ?, ?)
               ON CONFLICT(job_id) DO UPDATE SET
                   embedding=excluded.embedding,
                   model_name=excluded.model_name""",
            (job_id, blob, MODEL_NAME),
        )


def backfill_embeddings(db_path: str) -> int:
    """Embed every job that doesn't have an embedding yet. Call this once
    after each scrape run (or wire it into a scheduled task).

    Assumes a `jobs` table with columns `id` and `description` -- adjust
    the column names in the query below to match your actual schema.
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT j.id, j.description FROM jobs j
               LEFT JOIN job_embeddings e ON e.job_id = j.id
               WHERE e.job_id IS NULL"""
        ).fetchall()

    count = 0
    for row in rows:
        embed_and_store(db_path, row["id"], row["description"])
        count += 1
    return count


def _load_all_embeddings(db_path: str) -> Tuple[List[int], np.ndarray]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT job_id, embedding FROM job_embeddings").fetchall()
    ids = [r[0] for r in rows]
    vectors = np.array([np.frombuffer(r[1], dtype=np.float32) for r in rows])
    return ids, vectors


def recommend_similar_jobs(db_path: str, job_id: int, top_k: int = 5) -> List[Tuple[int, float]]:
    """'People who viewed this job might also like...' -- jobs whose
    descriptions are semantically closest to the given job."""
    ids, vectors = _load_all_embeddings(db_path)
    if job_id not in ids:
        raise ValueError(f"No embedding stored for job_id={job_id}. Run backfill_embeddings() first.")
    idx = ids.index(job_id)
    query_vec = vectors[idx]

    similarities = vectors @ query_vec
    ranked = sorted(
        ((ids[i], float(similarities[i])) for i in range(len(ids)) if ids[i] != job_id),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return ranked[:top_k]


def recommend_for_profile(db_path: str, profile_text: str, top_k: int = 10) -> List[Tuple[int, float]]:
    """The core recommendation feature: given free text describing a
    user's skills/interests (a pasted CV summary, or something like
    'Python backend developer, 2 years, interested in fintech startups'),
    rank every scraped job by relevance to that profile."""
    ids, vectors = _load_all_embeddings(db_path)
    query_vec = embed_text(profile_text)

    similarities = vectors @ query_vec
    ranked = sorted(zip(ids, similarities.tolist()), key=lambda pair: pair[1], reverse=True)
    return ranked[:top_k]
