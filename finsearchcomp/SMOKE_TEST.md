# Smoke Test — Linkup Research (XL) on FinSearchComp T2

First pilot run: 20 questions from FinSearchComp T2 Global, answered by Linkup's async
research endpoint in XL mode, graded against gold.

## Result

# ✅ 20 / 20 = 100%

- **Dataset:** FinSearchComp T2 Global (first 20 of 120)
- **Avg latency:** 91.3s / question (range 33s–597s; most under 90s, one ~10 min outlier)
- **Every answer matched the gold figure exactly** (not just within rounding tolerance)

## Config (no restraints)

| Piece | Value |
|---|---|
| Endpoint | `POST /v1/research` → poll `GET /v1/research/{id}` |
| Mode | `answer` |
| Reasoning depth | **XL** (exhaustive) |
| Output | `sourcedAnswer` (answer + sources, direct — no external synthesizer) |
| Timeout | none |
| Token cap | none |
| Judge | deterministic numeric match (FinSearchComp rubric: magnitude match, rounding/format tolerant) |

## Per-question

| # | Company · metric · period | Gold | Linkup | ✔ |
|---|---|---|---|---|
| 1 | Uber — R&D expenses, FY2019 | 4,836 | 4836 | ✅ |
| 2 | Uber — marketing expenses, FY2019 | 4,626 | 4626 | ✅ |
| 3 | Uber — total costs & expenses, FY2019 | 22,743 | 22743 | ✅ |
| 4 | Walmart — prepaid expenses, FY2018 | 3,511 | 3511 | ✅ |
| 5 | Walmart — inventories, FY2018 | 43,783 | 43783 | ✅ |
| 6 | Walmart — cost of sales, FY2018 | 373,396 | 373396 | ✅ |
| 7 | GameStop — total liabilities, Jan 29 2022 | 1,896.8 | 1896.8 | ✅ |
| 8 | GameStop — property & equipment, net | 163.6 | 163.6 | ✅ |
| 9 | GameStop — current assets | 2,598.8 | 2598.8 | ✅ |
| 10 | Apple — cash used in financing, FY2021 | 93,353 | 93353 | ✅ |
| 11 | Apple — cash used in investing, FY2021 | -14,545 / 14,545 | 14545 | ✅ |
| 12 | Apple — cash from operations, FY2021 | 104,038 | 104038 | ✅ |
| 13 | AMC — accounts receivable (net), FY2013 | 106,148 | 106148 | ✅ |
| 14 | AMC — diluted EPS, FY2013 | 4.76 | 4.76 | ✅ |
| 15 | Microsoft — operating income, FY2018 | 35,058 | 35058 | ✅ |
| 16 | Microsoft — shareholder equity, Jun 30 2018 | 82,718 | 82718 | ✅ |
| 17 | Starbucks — long-term debt (incl. current), Sep 27 2020 | 15,909.5 | 15909.5 | ✅ |
| 18 | Starbucks — total assets, Sep 27 2020 | 29,374.5 | 29374.5 | ✅ |
| 19 | Facebook — cash & equivalents, FY2019 | 19,079 | 19079 | ✅ |
| 20 | Facebook — total revenue, FY2019 | 70,697 | 70697 | ✅ |

## How to read it

- **T2 is the easy tier** (single point-in-time figures from filings). 100% here says
  Linkup XL reliably finds and returns exact 10-K numbers. **T3 (complex, multi-step) is
  the real differentiator** — not yet run.
- **20 is a pilot.** Full T2 Global is 120; T2+T3 is 370.
- Not yet a head-to-head: to compare against other APIs, we need to run their research
  endpoints on the **same** questions with the **same** judge.

## Files (everything stored — no re-run needed)

| File | Contents |
|---|---|
| `results/t2_research_xl_full.jsonl` | every question, gold, **full Linkup answer + sources + raw task object** |
| `results/t2_research_xl_graded.json` | per-question verdict, score, latency |
| `results/t2_research_xl_tasks.json` | the 20 Linkup task IDs |
| `results/run_xl.log` | full run log |

## Reproduce

```bash
# retrieval (async XL research, stores everything)
caffeinate -i -s python3 run_t2_research_xl.py --limit 20
# grade the stored answers (no Linkup re-run)
python3 grade_stored.py
```

Because the raw answers are stored, an LLM judge (e.g. `gpt-5-mini`) can re-grade the
same file later for a second opinion without spending any Linkup calls.
