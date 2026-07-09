# Linkup Finance Bench

A home for finance benchmarks we use (or could use) to measure Linkup against other
web-search and research APIs.

The goal is simple: find fair, reproducible finance benchmarks, add Linkup as a
contestant, and see where it lands.

## Structure

- **[`benchmarks/`](benchmarks/)** — a survey of the finance benchmarks that exist, each
  rated on the same three simple rules:
  - **Context** — what it actually is and how it works
  - **Cost** — roughly what it costs to run
  - **Reproducibility** — can we actually download and re-run it, or is it just a blog?
- **[`analysis/`](analysis/)** — deeper looks at specific harnesses:
  - [`you-com-harness-audit.md`](analysis/you-com-harness-audit.md) — fairness audit of You.com's `web-search-api-evals` + full comparator config matrix
  - [`comparator-matrix.html`](analysis/comparator-matrix.html) — the same config matrix as a visual reference
- **[`finsearchcomp/`](finsearchcomp/)** — run plan + runners for FinSearchComp with Linkup, and results:
  - [`RESULTS_T2.md`](finsearchcomp/RESULTS_T2.md) — full T2 Global: **96/119 = 80.7%** (→ 82.4% after [`RERUN.md`](finsearchcomp/RERUN.md))
  - [`T3_SMOKE.md`](finsearchcomp/T3_SMOKE.md) — T3 (hard tier) smoke: **13/20 = 65%**

More folders (runners, results) will be added as we start running them.
