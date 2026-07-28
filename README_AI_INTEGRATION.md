# Adding AI to the job market system — integration guide

## What you're adding, and why it's structured this way

A grader reading "we added AI" usually means one of two things happened:
someone wrapped a single API call around ChatGPT, or someone actually
combined a few different AI/ML techniques for a reason. This module does
the second one, on purpose, because it's both more defensible in a
presentation and more useful in practice. Three techniques, each doing
the job it's actually good at:

| Technique | Used for | Why this technique and not another |
|---|---|---|
| LLM structured extraction (`ai/extraction.py`) | Turning messy posting text into clean fields (skills, seniority, salary) | Postings are unstructured natural language in two languages — no fixed rule list survives contact with real data |
| Sentence embeddings (`ai/embeddings.py`) | Job recommendation, "similar jobs" | Fast, explainable, deterministic. You can show a grader the actual similarity score and defend it. An LLM call per comparison would be slower and non-reproducible |
| LLM narrative generation (`ai/insights.py`) | Turning your existing SQL aggregates into a readable dashboard blurb | This is the one place free text generation is actually the right tool — nobody wants to read a JSON blob of stats |

Everything runs for **$0**. `ai/extraction.py` and `ai/insights.py` call a
model through [Ollama](https://ollama.com), which runs entirely on your
own machine — no API key, no billing, no rate limit, and it keeps
working if the wifi at your demo drops. `ai/embeddings.py` uses
`sentence-transformers`, also fully local.

## Setup

1. **Install Ollama** (free): https://ollama.com/download — there's a
   normal Windows installer.
2. **Pull a model**, once, from a terminal:
   ```
   ollama pull llama3.2
   ```
   That's a ~2GB download, a 3-billion-parameter model. It runs on CPU
   at a few seconds per request, which is fine for a project demo. If
   your laptop is slow, `ollama pull qwen2.5:3b` is a smaller/faster
   alternative with similar quality.
3. **Install the Python packages** into your existing venv:
   ```
   pip install -r requirements-ai.txt --break-system-packages
   ```
   (drop `--break-system-packages` if you're inside a venv already,
   which your existing project already sets up).
4. **Create the new tables** — run `database/schema_ai.sql` against
   your existing database once. If your `jobs` table's primary key
   isn't literally called `id`, edit the `FOREIGN KEY` lines in that
   file first.
5. **Copy the `ai/` and `api/` folders** into your project root, next
   to your existing `database.py` / scraper modules.
6. **Mount the router** in your main FastAPI app file:
   ```python
   from api.ai_routes import router as ai_router
   app.include_router(ai_router, prefix="/api/ai")
   ```
7. **Point `DB_PATH`** in `api/ai_routes.py` at your actual database
   file (or import it from your existing config/settings module instead
   of hardcoding it).

## Running it after a scrape

Two calls, typically run right after your scraper finishes a batch:

```python
from ai.embeddings import backfill_embeddings
from ai.extraction import analyze_batch

backfill_embeddings("jobs.db")          # embeds any job missing a vector
# analyze_batch({job_id: text, ...})    # run over new postings, then
                                          # write results into job_analysis
```

The dashboard then calls the new endpoints on demand — recommendations
and similar-jobs are cheap (just a dot product over stored vectors), so
they can run per-request rather than needing to be pre-computed.

## Plain-English glossary (for your write-up / presentation)

- **Embedding** — a list of a few hundred numbers that represents what a
  piece of text is *about*. Similar meanings end up with similar
  numbers, even without shared words ("backend developer" and
  "server-side engineer" land close together).
- **Cosine similarity** — a score from -1 to 1 for how close two
  embeddings point in the same direction. This is the actual math behind
  "jobs similar to this one" and "jobs matching your profile."
- **LLM (large language model)** — the kind of model behind ChatGPT,
  here running locally through Ollama instead of over the internet.
  Good at reading messy text and either restructuring it (extraction) or
  writing new text about it (insights).
- **Structured output / JSON mode** — asking an LLM to reply in a fixed
  JSON shape instead of free-flowing prose, so your code can parse the
  response reliably.
- **Prompt engineering** — the wording of the instructions you send the
  LLM. Small changes (e.g. "return ONLY JSON, no prose") measurably
  change output reliability, which is why the prompts in this module are
  explicit about format.
- **Vector / semantic search** — searching by *meaning* (via embeddings
  and cosine similarity) instead of exact keyword matching.

## Things that make this score well in a project review

- **Multiple distinct techniques, each justified** — the table above is
  effectively your "design decisions" section already written.
- **Reproducibility** — cosine similarity scores are deterministic; you
  can screenshot a similarity score and explain exactly why it's what it
  is, unlike an opaque single LLM call.
- **No external dependency at demo time** — Ollama runs offline, so a
  bad venue wifi connection can't break your live demo. (If you ever do
  want a cloud fallback, Groq's free API tier runs the same kind of
  open models remotely with no cost — swapping `ollama.chat(...)` for
  Groq's client is a small change if you want to mention it as a future
  improvement.)
- **Add one evaluation, even a small one.** For example: hand-label 15
  postings with the skills they actually mention, run `analyze_batch`
  on them, and report precision/recall. Graders respond well to "we
  measured how good it is," not just "it works."

## Known assumptions to double-check against your actual code

- `jobs` table has an integer primary key called `id` and a text column
  called `description` — adjust `embeddings.py`'s SQL and
  `schema_ai.sql`'s `FOREIGN KEY` lines if yours differ.
- Salary fields assume millions of VND, matching typical Vietnamese IT
  postings — adjust the prompt in `extraction.py` if your data uses a
  different currency or unit.
