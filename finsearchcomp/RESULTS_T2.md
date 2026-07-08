# Result — Linkup Research (XL) on Full FinSearchComp T2 Global

Full run of all **119** T2 Global questions (the earlier 20-question smoke test +
the remaining 99), answered by Linkup's async research endpoint in XL mode.

## Score

# 96 / 119 = 80.7%

- **Dataset:** FinSearchComp T2 Global (all 119)
- **Sampler:** `linkup_research` · `mode=answer` · `reasoningDepth=XL` · `sourcedAnswer`
- **Judge:** deterministic numeric match (FinSearchComp rubric) — *approximate, see caveat*
- Pilot subset (first 20, the easy filing lookups) was **20/20**; the full set drops to
  80.7% because the back half is harder (macro ratios, OECD/World Bank indicators,
  definitional accounting items).

## Where it missed (23 fails)

Question #s: 21, 22, 25, 31, 32, 38, 39, 46, 48, 56, 62, 75, 78, 86, 88, 89, 93, 94, 95, 98, 99, 107, 115

Most failures are **genuine**, and cluster into:
- **Definition / interpretation mismatches** — e.g. "passenger car registrations" answered as total registered vehicles vs new registrations (#93, #94); NVIDIA "total deferred tax assets" net vs gross (#86). The metric was found but under the wrong definition.
- **Close numeric misses** on macro indicators — e.g. GDP/hour 85.0 vs 87.01 (#88), NNI index 65.95 vs 64.65 (#95).
- **One empty answer** — #99 returned no answer.

## Latency — and a real operational finding ⚠️

| Run | Concurrency | Median latency | Max |
|---|---|---|---|
| Pilot | 20 tasks at once | **59.5s** | 597s |
| Batch | 99 tasks at once | **3,434s (~57 min)** | 3,497s |

Firing **99 XL research jobs at once queued them hard** — median jumped from ~60s to
~57 min. That's a **throughput/queue artifact, not per-query latency**: an XL research
call in isolation is ~60s (as the pilot shows), but Linkup throttles many simultaneous
XL jobs.

**Takeaway:** submit XL research in **waves of ~20**, not 100 at once, to keep per-query
latency near ~60s. (The whole 99-batch still finished under our 60-min safety cap and all
99 completed successfully — just slowly.)

## Judge caveat

The deterministic grader is a rough proxy: it's **lenient on percentages** (a 1.0
absolute tolerance can pass near-misses like 4.5 vs 4.9%) and can't apply per-question
"Scoring Criteria" / ranges the way the official FinSearchComp LLM judge (`gpt-5-mini`)
does. So **80.7% is approximate** — a proper LLM judge could move it a few points either
way. Every raw answer is stored, so re-grading needs no Linkup re-run.

## How it compares (rough)

~80% on full T2 puts Linkup at the **top end** of the typical ~60–85% band for search/
research APIs on this tier. Not a verified head-to-head — that needs the same questions
run through competitors' research endpoints with the same judge.

## Files

| File | Contents |
|---|---|
| `results/t2_research_xl_full.jsonl` | pilot 20 — full answers + sources + raw task objects |
| `results/t2_research_xl_remaining.jsonl` | remaining 99 — same |
| `results/t2_research_xl_graded.json` | per-question verdicts, scores, latency (all 119) |
| `results/t2_research_xl*tasks.json` | Linkup task IDs |
| `results/run_xl*.log` | run logs |

## Reproduce

```bash
caffeinate -i -s python3 run_t2_research_xl.py --limit 20                    # pilot
caffeinate -i -s python3 run_t2_research_xl_batch.py --start 20 --end 120 --qps 10  # remaining
python3 grade_stored.py                                                       # grade all 119
```
