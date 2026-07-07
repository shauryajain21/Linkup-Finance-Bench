# Finance Benchmarks — Landscape

A catalog of the finance search / QA benchmarks we've looked at for benchmarking Linkup.

Each one is rated on the same three simple rules:

- **Context** — what it is and how it works, in plain words
- **Cost** — roughly what it takes to run
- **Reproducibility** — can we actually re-run it, or is it just a description?

## Summary

| Benchmark | What it tests | Reproducible? | Rough cost | Linkup included? |
|---|---|---|---|---|
| **BigFinanceBench** | Agentic research over filings, rubric-graded | ✅ Yes — 50 public items (928 total, 878 held out) | Medium | No |
| **FinanceBench** | Answering questions from SEC filings | ✅ Yes — 150 public Q&A with gold answers | Cheap (a few $) | No |
| **FinSearchComp** | Financial search & reasoning (live + historical) | ✅ Yes — 635 public Q&A with gold answers | Low–medium ($tens) | No |
| **You.com web-search-api-evals** | Search APIs head-to-head (uses FinSearchComp + others) | ✅ Yes — runnable framework | Medium ($100–300 full field) | No — *the opening for us* |
| **Hebbia "Who Evaluates the Evaluator"** | Model-vs-model over private docs | ❌ No — method only, no data released | N/A | No |

---

## BigFinanceBench (Rogo AI)

**Context.** An **agentic research** benchmark: an agent has to find the right evidence
inside SEC filings (10-Ks, proxies, 13-Fs) and then do the analyst work — pick the right
source, identify the right fiscal period, apply accounting definitions, and run the
calculation (weighted averages, pro forma, CAGR, leverage ratios). What makes it stand
out is the grading: instead of a single gold answer, each item has a **point-weighted
rubric with ordered checkpoints** (~16 rubric lines per question), so partial credit and
the *reasoning path* both count — including a "source choice" dimension. Scoring is
earned points ÷ total points.

**Links.**
- Dataset: https://huggingface.co/datasets/RogoAI/big-finance-benchmark

**Cost.** Medium. It's agentic (multi-step search + calculation per question) and graded
by strong LLM judges (Gemini / Claude Opus), so per-question cost is higher than a
single-lookup benchmark. The public set is only 50 questions, though, so a Linkup run
stays modest.

**Reproducibility.** ✅ **Yes**, with a caveat. 50 items are public with reference answers,
rubrics, and sample traces, under **CC BY 4.0** (JSONL). The full 928-item benchmark
holds back 878 items to prevent contamination — so we can reproduce the public slice but
not the full leaderboard.

**How Linkup fits.** This is the closest match to what Linkup actually does — an agent
searching filings from the open web. Linkup would be the retrieval/search layer feeding
the agent, and the rubric would score whether it surfaced the right sources and figures.

---

## FinanceBench (Patronus AI)

**Context.** The classic open finance benchmark. 150 public question-and-answer pairs
about real companies, drawn from SEC filings (10-Ks, 10-Qs, 8-Ks, earnings). Each
question has a **gold answer plus the evidence string** it came from, so grading is
straightforward. The original setup is "open-book": give the model the filing and see if
it answers correctly. The famous headline: GPT-4-Turbo with retrieval got **81% of
answers wrong or refused**.

**Links.**
- Dataset: https://huggingface.co/datasets/PatronusAI/financebench
- Code: https://github.com/patronus-ai/financebench
- Announcement: https://www.patronus.ai/announcements/patronus-ai-launches-financebench-the-industrys-first-benchmark-for-llm-performance-on-financial-questions

**Cost.** Cheap. 150 questions × (one search/answer call + one judge call) is a few
dollars if we route retrieval through Linkup.

**Reproducibility.** ✅ **Yes.** The 150-question sample is public with gold answers. The
full 10,231-question set is gated, but the 150 sample is what everyone uses.

**How Linkup fits.** Replace the "given document" with Linkup retrieval: question →
Linkup finds the answer from public filings → LLM answers → judge against gold.

---

## FinSearchComp (ByteDance)

**Context.** A newer, harder benchmark built for **financial search**, not closed-book
reading. 635 questions written by 70 professional financial analysts, each with a single
objective gold answer (a number, sometimes with a tolerance range), graded right/wrong.
Three difficulty tiers:
- **T1 – Time-Sensitive Data Fetching** — live values ("Nvidia's closing price yesterday")
- **T2 – Simple Historical Lookup** — a fixed past figure ("Starbucks' total assets on Sept 27, 2020")
- **T3 – Complex Historical Investigation** — multi-step ("which month from 2010–2025 did the S&P 500 rise most")

Split across two markets: **Global (Western)** and **Greater China** (bilingual).

**Links.**
- Paper: https://arxiv.org/abs/2509.13160
- Dataset: https://huggingface.co/datasets/ByteSeedXpert/FinSearchComp
- Site: https://randomtutu.github.io/FinSearchComp/
- T3 leaderboard: https://llm-stats.com/benchmarks/finsearchcomp-t3

**Cost.** Low–medium. Each question needs a search call + an LLM synthesizer + an LLM
judge. The catch: the hard tiers (T2/T3) are meant to run on **deep-research / agentic
endpoints**, which cost more per call ($0.05–0.30 each on some providers). Linkup alone
across the ~600 questions is still $tens; the expense only shows up when running the full
competitor field.

**Reproducibility.** ✅ **Yes.** Fully open dataset with deterministic gold answers and an
open-source grading harness.

**How Linkup fits.** Linkup's equivalent of the deep-research endpoints is `depth: deep`
search or the `/research` endpoint.

---

## You.com — web-search-api-evals

**Context.** Not a dataset — a **runnable framework** that turns benchmarks into a
scoreboard for web-search APIs. For each question it: (1) calls a search API, (2) has an
LLM write the answer from the results, (3) has a second LLM judge grade it. It already
wires up **Exa, Perplexity, Tavily, Parallel, You.com, and Google**, and ships several
datasets including **FinSearchComp (T2/T3 Global)**, SimpleQA, FRAMES, DeepSearchQA, and
BrowseComp. For the finance tiers it points every provider at its **deep-research /
agentic endpoint** (Exa `research_pro`, Perplexity Sonar deep research, Parallel
`pro`/`ultra`, Tavily `research_pro`, You.com finance research).

**Links.**
- Repo: https://github.com/youdotcom-oss/web-search-api-evals

**Cost.** Medium. The LLM synth + judge calls are a few dollars total; the cost is the
deep-research search calls. Full head-to-head across all providers × the finance sets is
ballpark **$100–300**, mostly Perplexity deep research, Parallel Ultra, and Exa Research
Pro. Running **just Linkup** is a few dollars.

**Reproducibility.** ✅ **Yes.** Clone, add API keys, run one command; results write to
per-provider CSVs plus an aggregate.

**How Linkup fits.** **Linkup is not in it yet** — this is the opening. Fork it, add a
Linkup "sampler," and run it head-to-head against the others on the finance sets. Caveat:
it's You.com's own repo, so treat their framing as friendly-to-them — but we run it
ourselves, so we control the setup.

---

## Hebbia — "Who Evaluates the Evaluator"

**Context.** Often referred to as a "finance benchmark," but it is **not a benchmark you
can run** — it's a **grading method**. Two AIs get the *same* documents, answer questions,
and a third "evaluator" AI scores each answer 1–5 on things like accuracy, insight, and
conciseness (using token log-probabilities for a smooth score), repeated many times with
a permutation test for statistical significance. The variable being tested is the
**model**, not a search API — Linkup is nowhere in their loop.

**Links.**
- Blog: https://www.hebbia.com/blog/which-model-will-give-me-the-edge
- Methodology PDF: *Who Evaluates the Evaluator: Reaching Autonomous Consensus on Agentic Outputs* (Hebbia Research)

**Cost.** N/A — nothing to run.

**Reproducibility.** ❌ **No.** They published only the *method* and a few sample
questions. The actual question set, the documents, and the scored data were **not
released**, so their numbers can't be reproduced.

**How Linkup fits.** We can't reproduce their result, but we *can* borrow their grading
method: make Linkup one of the two contestants (Linkup vs a competitor over a shared
question set) and reuse the 1–5 log-prob scoring + permutation test to get a
statistically solid "Linkup wins" number.
