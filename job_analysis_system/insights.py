"""
ai/insights.py
---------------
Generates a short, human-readable market summary from aggregated
statistics your SQL queries already produce -- e.g. "Python and AWS were
the two most in-demand skills this week, and average posted salaries
rose 8%." This is the other half of "job market analysis": turning
numbers into a narrative a non-technical reader can skim on the
dashboard's front page.

Uses the same free, local Ollama model as ai/extraction.py -- no new
dependency, no cost, no API key.
"""

import ollama

MODEL_NAME = "llama3.2"

INSIGHT_PROMPT = """You are a labor-market analyst writing a short weekly \
briefing for an IT job board's dashboard. Using ONLY the statistics \
below, write 3-4 sentences of plain-English commentary. Do not invent \
numbers that aren't given below. Do not use markdown formatting.

Statistics:
{stats}
"""


def generate_market_insight(stats: dict) -> str:
    """stats example:
    {
      "period": "2026-07-21 to 2026-07-27",
      "total_new_postings": 214,
      "top_skills": [["Python", 58], ["AWS", 41], ["React", 37]],
      "avg_salary_change_pct": 8.2,
      "top_hiring_companies": ["Company A", "Company B"],
    }

    Feed this whatever your existing analytics module already computes --
    this function only handles turning the numbers into prose.
    """
    prompt = INSIGHT_PROMPT.format(stats=stats)
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.4},  # a bit higher than extraction.py:
                                        # this is prose, not structured data,
                                        # so some variation in phrasing is fine
    )
    return response["message"]["content"].strip()
