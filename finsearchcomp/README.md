# FinSearchComp — Run Plan (with Linkup)

How we'd run the [FinSearchComp](https://arxiv.org/abs/2509.13160) financial-search
benchmark with Linkup as a contestant.

> ✅ **Full T2 done:** Linkup research (XL) scored **96/119 = 80.7%** on all of T2 Global
> — see [`RESULTS_T2.md`](RESULTS_T2.md). Pilot (first 20) was 20/20 — see
> [`SMOKE_TEST.md`](SMOKE_TEST.md). Runners: `run_t2_research_xl.py`,
> `run_t2_research_xl_batch.py`, `grade_stored.py`.

## The benchmark

- 635 expert-written finance questions, single objective gold answer each, graded **1/0**.
- Three tiers: **T1** time-sensitive (live prices), **T2** simple historical lookup, **T3** complex multi-step investigation.
- Two markets: Global (Western) and Greater China.
- Official harness: [`randomtutu/FinSearchComp`](https://github.com/randomtutu/FinSearchComp).

## Two ways to run it

| Route | What it takes | Notes |
|---|---|---|
| **You.com `web-search-api-evals`** | Add a Linkup "sampler" | Least code — the search-swap machinery already exists. Only ships **T2/T3 Global**. See [`../analysis/you-com-harness-audit.md`](../analysis/you-com-harness-audit.md). |
| **Official FinSearchComp harness** | Build a Linkup retrieval/agent layer | Canonical + full 635 Qs, but the official harness has **no swappable retrieval step** (it relies on Gemini's built-in `google_search`), so we'd have to add one. |

**Recommendation:** start with the You.com repo route.

## Dataset sizes (You.com repo, bundled CSVs)

| Set | Questions |
|---|---|
| `fin_search_comp_t2_global` | 120 |
| `fin_search_comp_t3_global` | 250 |
| **Total** | **370** |

> T1 (live prices) is **not** in the You.com repo, and can't be reproduced faithfully
> after the fact — the gold answers were pinned to a moment in 2025.

## Call counts

One research call per question, per sampler.

| Run | Research calls |
|---|---|
| Pilot (T2, `--limit 20`) | 20 |
| Linkup only, T2 | 120 |
| Linkup only, T3 | 250 |
| Linkup only, both sets | **370** |
| Linkup, both variants (raw + direct) | 740 |
| Full field (~13 research configs + Linkup) | ~5,000 |

Plus cheap grader calls (`gpt-5-mini`, 1/question/sampler) and synthesizer calls
(`gpt-5.4-nano`, only for the raw-search variant).

## Plan

1. **Fork** `youdotcom-oss/web-search-api-evals`.
2. **Add two Linkup samplers** (see audit doc for why two):
   - `linkup_search` — raw search results, `needs_synthesis=True`
   - `linkup_research` — `sourcedAnswer` / `/research`, `needs_synthesis=False` (direct)
3. **Pilot**: `--datasets fin_search_comp_t2_global --limit 20` → sanity-check the sampler (~20 calls).
4. **Full Linkup run**: both sets → the headline accuracy number (370 calls).
5. **Fair comparison** (optional but recommended for anything public): re-run 1–2 rivals
   (Exa Research Pro, Perplexity deep) ourselves so every score comes from the same
   harness on the same day — don't just diff against You.com's published numbers.

## Does 370 calls give a comparable score?

Yes — same 0/1 grading, same grader (`gpt-5-mini`), same prompt as every competitor, so
the accuracy % is directly comparable **in format**. The caveat is *who ran the
competitors' numbers*: comparing against You.com's published figures is cheap but trusts
their (self-favoring) runs; re-running the key rivals yourself is the defensible version.
