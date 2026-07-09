# Smoke Test — Linkup Research (XL) on FinSearchComp T3

First pilot on the **hard tier**: 20 questions from FinSearchComp T3 Global (complex,
multi-step investigations), answered by Linkup research (XL), hand-graded against gold.

## Result

# 13 / 20 = 65%

- **Dataset:** FinSearchComp T3 Global (first 20 of 84)
- **Sampler:** `linkup_research` · `mode=answer` · `reasoningDepth=XL` · `sourcedAnswer`
- **Judge:** manual (read each full answer vs the FinSearchComp rubric) — the deterministic
  numeric judge can't score T3's multi-part answers, so these were graded by hand.
- **Latency:** median ~366s (~6 min), max ~1,705s (~28 min) — higher than T2 because
  these need multi-step retrieval + calculation over many sources.

## Why T3 is different (and why 65% is a strong showing)

T3 is where scores collapse for everyone — multi-period aggregation, cross-currency
conversion, orderings, and calculations, not single lookups. For reference, the public
T3 leaderboard's one entry (Kimi K2-Thinking) sits at **47.4%**, and the FinSearchComp
paper notes search adds far less on T3 than T2. So **65% on the hard tier is encouraging**
— though it's a 20-question pilot, hand-graded, and not yet a verified head-to-head.

## What it nailed (13)

Genuinely hard, multi-part answers returned exactly:
- **#5** — "did rates move in unison?" → correct *No*, correct date (April 8), **all three
  central-parity values exact** (7.9155 / 0.9270 / 7.2038)
- **#17** — Oracle's YoY total-asset growth for **four fiscal years**, all exact
- **#18** — filtered 5 stocks to the 3 with positive April moves, **all three % exact**
- **#1** — three exchange rates + correct ordering; **#6, #13, #16, #20** comparative/calc questions

## Where it missed (7)

| # | Linkup | Gold | Why |
|---|---|---|---|
| 7 | "not the same" (Nasdaq vs CSI 1000) | **same**, CSI 1000 | wrong relationship |
| 8 | S&P 500, 50.40 | Nasdaq, 60.77T | wrong index + value |
| 9 | 110.50 higher | 8,847,105.72 B yuan | couldn't source the volume data |
| 11 | Sunrun −43.84% | NTCL −68.80% | missed an obscure biggest-decliner |
| 14 | Tesla, 171.78B, 15.69% | Tesla, 172.67B, 15.67% | stock right, trading value off beyond rounding *(borderline)* |
| 15 | ROIC 24.62% | 22.19% | ROIC definition mismatch |
| 19 | Boeing −9.91 | Boeing −11.51 | right stock, P/E value off |

The misses cluster in **trading-volume aggregation** (#8, #9), **definitional metrics**
(ROIC #15, P/E #19), and **hard-to-source obscure data** (#11) — not basic retrieval.
#14 is borderline (lenient grading would make it 14/20 = 70%).

## Caveats

- **Hand-graded, 20 questions** — indicative, not final. An LLM judge (`gpt-5-mini`) pass
  and the full 84 would firm it up. Raw answers are stored, so re-grading needs no re-run.
- **No verified competitor T3 numbers** for the search APIs in hand yet — the ~65% reads
  well against the T3 leaderboard context but isn't a same-questions head-to-head.

## Files
- `results/t3_research_xl_smoke.jsonl` — full answers + sources + raw task objects
- `results/t3_research_xl_smoke_graded.json` — per-question verdicts + notes
- `t3_smoke_grade.py` — the verdict record (re-runnable)

## Reproduce
```bash
caffeinate -i -s python3 run_t2_research_xl_batch.py \
  --csv <path>/fin_search_comp_t3_global.csv \
  --indices 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 --qps 10 \
  --out results/t3_research_xl_smoke.jsonl --tasks results/t3_research_xl_smoke_tasks.json
python3 t3_smoke_grade.py
```
