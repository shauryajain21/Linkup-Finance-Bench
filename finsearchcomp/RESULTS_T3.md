# Result — Linkup Research (XL) on FinSearchComp T3 (partial)

T3 is the **hard tier** (complex, multi-step investigations). We've answered and graded
**53 of 84** questions so far (smoke test + the wave run that was stopped mid-way).

## Score (53 of 84 graded)

# 31 / 53 = 58.5%

| Batch | Score |
|---|---|
| Smoke test (first 20) | 13/20 = 65% |
| Rest (next 33) | 18/33 = 54.5% |
| **Combined** | **31/53 = 58.5%** |

31 questions (idx 52, 54–83) not yet run. Judge is manual (T3 answers are multi-part, so
the numeric grader can't score them) — indicative, not final.

## Latency (accurate, server-side, clean)

- **Median ~328s (~5.5 min)**, mean ~597s, max ~29 min
- Measured from Linkup's own `createdAt → updatedAt` timestamps, on runs kept under the
  concurrency cap (waves of 16) — client and server agree within seconds, so **no queue
  artifact**. This is the real per-query T3 latency.

## What Linkup is good at (the passes)

Genuinely hard **single-company, multi-period computations** — returned exactly:
- Apple/Tesla inventory-turnover ratio, WF/Nvidia net-income multiple, Apple-vs-Nvidia
  gross-margin gap, Oracle total-asset growth — **each across 4 fiscal years, all values exact**
- Specific factual/derived answers: KOSPI 2021 peak, Nikkei positive months, S&P max
  drawdown + peak/trough dates, a share-accumulation word problem (#34), Amazon financing
  cash-flow delta

## Where it fails (the misses)

Failures cluster in **cross-universe ranking / screening** and **definitional metrics** —
not single-company retrieval:
- Ranking many stocks: debt-to-asset ranking (#24), top-3 ROE (#31), best ETFs (#33),
  top-3 IPOs (#40), S&P/Nasdaq constituent filters (#32, #47)
- Definitional: ROIC (#42/#43), "diluted ROE" (#31)
- Multi-value where one year is off (J&J #44, Exxon #51) or an incomplete list (FTSE #29)

**Pattern:** strong when the answer is a computed figure from one company's filings; weaker
when it must screen/rank a whole index universe or hinges on a metric definition.

## How 58.5% reads

T3 is where scores collapse for everyone. The public T3 leaderboard's one entry (Kimi
K2-Thinking) is **47.4%**, and the paper notes search helps far less on T3 than T2. So
**~58% on the hard tier is a solid showing** — but it's 53/84, hand-graded, not a verified
head-to-head.

## Files
- `results/t3_research_xl_smoke.jsonl` + `..._rest.jsonl` — full answers + sources + server timestamps
- `results/t3_research_xl_smoke_graded.json` + `..._rest_graded.json` — per-question verdicts
- `t3_smoke_grade.py`, `t3_rest_grade.py` — the verdict records

## To finish
31 questions remain (15 recoverable by polling stored task IDs, 16 fresh). Run with:
```bash
caffeinate -i -s python3 run_t2_research_xl_batch.py \
  --csv <path>/fin_search_comp_t3_global.csv --start 52 --end 84 --wave 16 --qps 10 \
  --out results/t3_research_xl_rest.jsonl --tasks results/t3_research_xl_rest2_tasks.json
```
