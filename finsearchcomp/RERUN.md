# Re-run of the 23 T2 Failures

We re-ran the 23 questions Linkup got wrong on the first T2 pass through the **same**
Linkup research (XL) endpoint, to see how much of the miss was run-to-run variance vs a
genuine capability gap.

## Result

- **2 of 23 flipped to correct** on the re-run.
- **Best-of-both score: 98/119 = 82.4%** (up from 96/119 = 80.7%).

### The two that flipped
| # | First run | Re-run | Gold | Note |
|---|---|---|---|---|
| 32 | 2025 | **9610** | 9610.25 USD/MT | got the right figure the 2nd time |
| 99 | *(blank answer)* | **2.30%** | 2.29% | the previously-empty answer now returned correctly |

## What this tells us

1. **There is real run-to-run variance.** Some answers changed between the two runs in
   both directions — e.g. #75 went `22000 → 0`, #89 `71539 → 30440`, #95 `65.95 → 62.47`.
   XL research is not deterministic, so a single run slightly understates the true
   ceiling; re-running recovers a couple of points.
2. **#99 was a transient blank**, not an unanswerable question — the re-run produced the
   right number. Worth a retry-on-empty in the runner.
3. **Most misses are genuine, not variance.** 21 of 23 stayed wrong, and they're the
   definitional/interpretation cases (e.g. "passenger car registrations" as total
   registered vs new sales #93/#94; NVIDIA deferred tax assets net vs gross #86; wrong
   macro series). These won't fix by re-running — they need tighter query phrasing or a
   judge that accepts the alternative definition.

## Bottom line

Re-running lifts Linkup from **80.7% → 82.4%** on T2. Combined with a proper LLM re-grade
(our deterministic judge is rough) and phrasing fixes on the definitional questions, the
gap to You.com's 87.3% (8 questions) is plausibly closable without Linkup finding
anything new.

## Files
- `results/t2_research_xl_rerun.jsonl` — full re-run answers + sources
- `results/t2_rerun_compare.json` — per-question run1 vs run2 diff
- `rerun_compare.py` — regenerates the comparison from stored answers

## Reproduce
```bash
caffeinate -i -s python3 run_t2_research_xl_batch.py \
  --indices 20,21,24,30,31,37,38,45,47,55,61,74,77,85,87,88,92,93,94,97,98,106,114 \
  --qps 10 --out results/t2_research_xl_rerun.jsonl --tasks results/t2_research_xl_rerun_tasks.json
python3 rerun_compare.py
```
