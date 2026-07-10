# Result — Linkup Research (XL) on FinSearchComp T3 (complete)

T3 is the **hard tier** (complex, multi-step investigations). **All 84 T3 Global questions
answered and graded.**

## Score

# 49 / 84 = 58.3%

| Batch | Score |
|---|---|
| Smoke (first 20) | 13/20 = 65% |
| Rest (next 33) | 18/33 = 54.5% |
| Final (last 31) | 18/31 = 58.1% |
| **Complete T3 (84)** | **49/84 = 58.3%** |

Judge is manual (T3 answers are multi-part, so the numeric grader can't score them) —
indicative, not final. A `gpt-5-mini` re-grade could shift it a few points.

## Latency (accurate, server-side)

- **Median ~295s (~4.9 min)**, mean ~548s, max ~29 min
- From Linkup's `createdAt → updatedAt` timestamps, on runs kept in waves under the
  concurrency cap — no queue artifact. This is the real per-query T3 latency.

## What Linkup is good at (the passes)

Strong on **single-company / specific-value computations** — returned exactly:
- Multi-year ratio tables (Apple/Tesla turnover, WF/Nvidia net income, gross-margin gaps,
  Oracle asset growth — 4 fiscal years each, all values exact)
- Specific derived facts: KOSPI peak, Nikkei positive months, S&P max drawdown + dates,
  gold >$80-drop dates (all 5), AMD/Intel quarterly margins, a BTC-strategy P&L within 1%,
  China sex ratio, a calendar-day-diff puzzle, an East-Asia calling-code sum

## Where it fails (the misses)

Failures cluster in **cross-universe screening / ranking** and **definitional metrics** —
not single-company retrieval:
- Rank/screen a whole index: top-3 ROE, best ETFs, debt-to-asset ranking, top-3 gainers,
  Nth-by-net-income, S&P/Nasdaq/NYSE constituent filters
- Definitional: ROIC, "diluted ROE"
- Incomplete lists (missed one of two names) or one year off in a multi-year answer
- Couldn't source paywalled index data (SPBTC)

**Pattern:** great at "compute this figure from one company's filings"; weaker when it must
screen/rank hundreds of stocks or the answer hinges on a metric definition.

## How 58.3% reads

T3 is brutal — the public T3 leaderboard's one entry (Kimi K2-Thinking) is **47.4%**, and
the paper notes search helps far less on T3 than T2. So **~58% on the hard tier is a strong
showing** — caveat: hand-graded, not a verified same-harness head-to-head.

## Files
- `results/t3_research_xl_{smoke,rest}.jsonl` — full answers + sources + server timestamps
- `results/t3_research_xl_{smoke,rest,final}_graded.json` — per-question verdicts
- `t3_{smoke,rest,final}_grade.py` — the verdict records
