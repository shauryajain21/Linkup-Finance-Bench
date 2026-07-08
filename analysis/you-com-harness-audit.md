# You.com `web-search-api-evals` — Harness Audit

An audit of [`youdotcom-oss/web-search-api-evals`](https://github.com/youdotcom-oss/web-search-api-evals)
— the framework we'd use to benchmark Linkup against other search APIs on FinSearchComp.
It's You.com's own repo, so we checked it for anything that favors them.

See [`comparator-matrix.html`](comparator-matrix.html) for the same config data as a
visual reference.

## How the harness works (per question)

1. **Search** — the sampler calls its provider's API.
2. **Answer** — one of two paths:
   - **Direct** (`needs_synthesis=False`): the provider's own finished answer goes straight to the grader.
   - **Via synthesizer** (`needs_synthesis=True`): raw results are rewritten into an answer by a **deliberately weak** shared model (`gpt-5.4-nano`).
3. **Grade** — an LLM judge scores the answer **1 or 0** against the gold answer.

## Shared harness config (`constants.py`)

| Piece | Value | Notes |
|---|---|---|
| Synthesizer (weak) | `gpt-5.4-nano` | only runs for "via synthesizer" rows |
| Grader — general | `gpt-5.4-mini` | SimpleQA / FRAMES / etc. |
| Grader — finance | `gpt-5-mini` | FinSearchComp T2 / T3 |
| Search-result cap | 265,000 tokens | trim budget before synthesis |
| Excluded from default runs | `*research*`, `parallel_pro`, `parallel_ultra`, `perplexity_finance_historical_lookup` | cost / latency |

## The comparator matrix — 20 configs, 6 providers

**Answer path:** 🟢 DIRECT = provider answer → grader · 🟡 SYNTH = raw results → `gpt-5.4-nano` → grader

### You.com — `YOU_API_KEY` — 8 configs
| Sampler | Endpoint | Reasoning model | Key config | Path | Timeout |
|---|---|---|---|---|---|
| `you_search_with_livecrawl` | SDK search.unified | — snippets | count 10 · livecrawl WEB · markdown · news off | 🟡 | 60s |
| `you_search` | SDK search.unified | — snippets | count 10 · news off | 🟡 | 60s |
| `you_research_lite` | SDK research() | You research | effort LITE · concurrency 5 | 🟢 | 60s |
| `you_research_standard` | SDK research() | You research | effort STANDARD | 🟢 | 120s |
| `you_research_deep` | SDK research() | You research | effort DEEP | 🟢 | 200s |
| `you_research_exhaustive` | SDK research() | You research | effort EXHAUSTIVE | 🟢 | 400s |
| `you_finance_research_deep` | POST /v1/finance_research | You finance | effort "deep" · concurrency 5 | 🟢 | 300s |
| `you_finance_research_exhaustive` | POST /v1/finance_research | You finance | effort "exhaustive" | 🟢 | 600s |

### Perplexity — `PERPLEXITY_API_KEY` — 3 configs
| Sampler | Endpoint | Reasoning model | Key config | Path | Timeout |
|---|---|---|---|---|---|
| `perplexity_finance_historical_lookup` | POST /v1/agent | `openai/gpt-5.5` | tools: finance_search + web_search + fetch_url · max_steps 5 · max_tokens 2048 · reasoning_effort **low** | 🟢 | 120s |
| `perplexity_finance_multi_step_research` | POST /v1/agent | `anthropic/claude-opus-4-7` | tools: finance_search + web_search + fetch_url · max_steps 10 · max_tokens 4096 | 🟢 | 180s |
| `perplexity_sonar_deep_research_high` | POST /chat/completions | `sonar-deep-research` | reasoning_effort **high** | 🟡 | 3000s |

### Exa — `EXA_API_KEY` — 2 configs
| Sampler | Endpoint | Reasoning model | Key config | Path | Timeout |
|---|---|---|---|---|---|
| `exa_search_with_text` | SDK search() | — excerpts | num_results 10 · text max_chars 20,000 | 🟡 | 60s |
| `exa_research_pro` | SDK research.create() | `exa-research-pro` | poll every 10s until done | 🟢 | 3000s |

### Parallel — `PARALLEL_API_KEY` — 3 configs
| Sampler | Endpoint | Reasoning model | Key config | Path | Timeout |
|---|---|---|---|---|---|
| `parallel_search_basic` | Search API search() | — excerpts | mode basic · max_results 10 | 🟡 | 60s |
| `parallel_pro` | Task API task_run | processor: pro | task_spec omitted → plain text | 🟢 | 3000s |
| `parallel_ultra` | Task API task_run | processor: ultra | task_spec omitted → plain text | 🟢 | 3000s |

### Tavily — `TAVILY_API_KEY` — 3 configs
| Sampler | Endpoint | Reasoning model | Key config | Path | Timeout |
|---|---|---|---|---|---|
| `tavily_basic` | SDK search() | — results | search_depth basic · max_results 10 | 🟡 | 60s |
| `tavily_advanced` | SDK search() | — results | search_depth advanced · max_results 10 | 🟡 | 60s |
| `tavily_research_pro` | SDK research() | Tavily "pro" | poll every 10s until done | 🟢 | 3000s |

### Google (SerpAPI) — `SERP_API_KEY` — 1 config
| Sampler | Endpoint | Reasoning model | Key config | Path | Timeout |
|---|---|---|---|---|---|
| `google_search` | GET serpapi.com/search | — snippets | engine google · num 10 | 🟡 | 60s |

## What to watch before trusting the scoreboard

1. **"Apples to apples" is only half true.** The repo claims a shared model + prompt makes it fair, but that shared synthesizer only touches the 🟡 SYNTH rows. Every 🟢 DIRECT row is judged on the provider's own answer — a fundamentally different generation path.
2. **Perplexity's flagship is handicapped.** `sonar-deep-research` is left on the synthesis path (`needs_synthesis` defaults to `True`), so its finished deep-research report gets re-compressed by `gpt-5.4-nano` — while You.com's research answers bypass that step entirely.
3. **You.com sets its rivals' knobs.** Perplexity's finance agent runs on `gpt-5.5` at `reasoning_effort=low`, 5 steps — choices made by You.com, not Perplexity. Under-tuning a competitor here is invisible in the final score.
4. **Most shots on goal.** You.com fields 8 configs vs 1–3 for everyone else. Any "best config per provider" ranking rewards having more attempts.
5. **Latency isn't measured the same way.** You.com and Tavily report their own *internal* latency; everyone else is timed wall-clock (incl. network + queue). Speed claims flatter the two exceptions.
6. **Fair parts, for the record.** The grader is an OpenAI model (no self-judging), the FinSearchComp grader prompt is the paper's original, and a weak synthesizer + stronger grader is a sound design.

## Implications for adding Linkup

- Add **two Linkup samplers**: a raw-search one (🟡, goes through `gpt-5.4-nano`) *and* a direct-answer one using `sourcedAnswer`/`/research` (🟢) — so Linkup competes on the same footing as You.com's research endpoints, not just the nano-bottlenecked tier.
- We control Linkup's config, so tune it properly (unlike how they set Perplexity).
- Ignore their latency methodology; measure wall-clock uniformly if we report speed.
- Treat any win as "Linkup did well on You.com's home turf" — cross-check against the official FinSearchComp harness for a neutral referee.
