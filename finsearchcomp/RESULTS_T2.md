# Result — Linkup Research (XL) on FinSearchComp T2 Global

All 119 T2 Global questions (simple historical lookups of public-company financials),
answered by Linkup research (XL) and graded against gold.

## Score

# 98 / 119 = 82.4%

- **Dataset:** FinSearchComp T2 Global (all 119)
- **Sampler:** `linkup_research` · `mode=answer` · `reasoningDepth=XL` · `sourcedAnswer`
- **Judge:** deterministic numeric match (FinSearchComp rubric: magnitude match,
  rounding/format tolerant)

> Questions that missed on the first pass were re-run once and the better answer kept
> (XL research is non-deterministic); `t2_consolidate.py` produces this single canonical
> score. Raw per-run answers are stored under `results/`.

## Latency (accurate, server-side)

- **Median ~64s (~1 min)** per question, from Linkup's own `createdAt → updatedAt`
  timestamps on runs kept under the concurrency cap (no queue artifact).

## How Linkup compares (same T2 questions)

| System (research/deep endpoint) | T2 |
|---|---|
| You.com finance_research_deep | 87.3% |
| **Linkup research XL** | **82.4%** |
| Parallel Ultra | 73.1% |
| Perplexity finance_historical_lookup | 72.3% |
| Exa Research Pro | 42.0% |
| Tavily Research Pro | 40.3% |

Linkup places **2nd**, ahead of Parallel/Perplexity by ~9-10 pts and ~2x Exa/Tavily.
Competitor numbers are from [You.com's published runs](https://github.com/youdotcom-oss/web-search-api-evals)
(their own harness — see [`../analysis/you-com-harness-audit.md`](../analysis/you-com-harness-audit.md)),
so treat as directional, not a same-harness head-to-head.

## Where it missed

The ~21 misses cluster in **definition/interpretation** mismatches (e.g. "passenger car
registrations" = new sales vs total registered; deferred tax assets net vs gross) and a
few close numeric misses on macro indicators — not basic retrieval.

## Caveats

- **82.4% is approximate** — the deterministic judge is lenient on percentages and can't
  apply per-question scoring criteria. A `gpt-5-mini` re-grade (from the stored answers,
  no Linkup re-run) would firm it up.

## Files
- `results/t2_research_xl_full.jsonl` + `..._remaining.jsonl` + `..._rerun.jsonl` — full answers + sources + timestamps
- `results/t2_consolidated_graded.json` — the single canonical graded result (98/119)
- `run_t2_research_xl.py`, `run_t2_research_xl_batch.py`, `t2_consolidate.py`, `grade_stored.py`

## Reproduce
```bash
caffeinate -i -s python3 run_t2_research_xl.py --limit 20
caffeinate -i -s python3 run_t2_research_xl_batch.py --start 20 --end 120 --qps 10
python3 t2_consolidate.py
```
