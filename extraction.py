"""
ai/extraction.py
-----------------
Turns one raw scraped job-posting string into structured fields: skills,
seniority level, years of experience, salary range, job type, and a
one-sentence summary. This is the "job analysis" half of the assignment.

WHY AN LLM HERE (and not just regex/keyword matching)?
Job descriptions are unstructured text written by hundreds of different
companies in different styles and, on a Vietnamese job board, often mixed
Vietnamese/English. A fixed list of keyword rules breaks the moment a
company phrases something differently ("5+ nam kinh nghiem" vs "5 years
experience" vs "senior level, 5 yrs+"). An LLM generalizes across that
variation because it was trained on language, not a fixed vocabulary —
and it needs zero labeled training data from you to do it.

COST: $0. Ollama runs a small open-source model entirely on your own
machine. No API key, no internet required after the model is downloaded,
no rate limit, no bill.

SETUP:
    1. Install Ollama:  https://ollama.com/download  (Windows installer)
    2. Open a terminal and pull a model once:   ollama pull llama3.2
       (about 2GB download, ~3B parameters, runs fine on a laptop CPU)
    3. pip install ollama --break-system-packages   (or just `pip install ollama`
       inside your venv)
    4. That's it — Ollama runs a background server on localhost:11434
       automatically after install.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional

import ollama

MODEL_NAME = "llama3.2"

EXTRACTION_PROMPT = """You are an information-extraction engine for a job \
board. Read the job posting below and return ONLY a JSON object -- no \
prose, no markdown code fences -- matching exactly this shape:

{{
  "skills": ["skill1", "skill2"],
  "seniority_level": "intern" | "junior" | "mid" | "senior" | "lead",
  "min_experience_years": <number or null>,
  "salary_min": <number or null, in millions VND>,
  "salary_max": <number or null, in millions VND>,
  "job_type": "fulltime" | "parttime" | "contract" | "remote" | "hybrid" | "onsite",
  "summary": "<one plain-English sentence describing the role>"
}}

If a field isn't mentioned in the posting, use null (or an empty list for skills).

Job posting:
\"\"\"
{posting_text}
\"\"\"
"""


@dataclass
class JobAnalysis:
    skills: list = field(default_factory=list)
    seniority_level: Optional[str] = None
    min_experience_years: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = None
    summary: str = ""


def _strip_code_fence(text: str) -> str:
    """Small local models sometimes wrap JSON in ```json ... ``` even when
    told not to. Strip it before parsing rather than fail on it."""
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()


def analyze_job_posting(posting_text: str, retries: int = 2) -> JobAnalysis:
    """Send one job posting to the local LLM and parse its structured reply.

    Retries on malformed JSON -- small local models occasionally add stray
    text around the JSON object, so we give it a couple of extra tries
    before giving up.
    """
    prompt = EXTRACTION_PROMPT.format(posting_text=posting_text[:4000])

    last_error = None
    for _attempt in range(retries + 1):
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            format="json",                  # tells Ollama to constrain output to valid JSON
            options={"temperature": 0.1},   # low temperature = consistent, repeatable extraction
        )
        raw = _strip_code_fence(response["message"]["content"])
        try:
            data = json.loads(raw)
            return JobAnalysis(
                skills=data.get("skills") or [],
                seniority_level=data.get("seniority_level"),
                min_experience_years=data.get("min_experience_years"),
                salary_min=data.get("salary_min"),
                salary_max=data.get("salary_max"),
                job_type=data.get("job_type"),
                summary=data.get("summary", ""),
            )
        except (json.JSONDecodeError, KeyError) as e:
            last_error = e
            continue

    raise ValueError(f"Could not parse LLM output after {retries + 1} attempts: {last_error}")


def analyze_batch(postings: dict) -> dict:
    """postings: {job_id: raw_text}. Returns {job_id: JobAnalysis}.

    Sequential on purpose: local inference is the bottleneck, not network
    I/O, so threading won't speed this up unless you run multiple Ollama
    processes -- not worth the complexity for a class project.
    """
    results = {}
    for job_id, text in postings.items():
        try:
            results[job_id] = analyze_job_posting(text)
        except ValueError as e:
            print(f"[extraction] skipped job_id={job_id}: {e}")
    return results
