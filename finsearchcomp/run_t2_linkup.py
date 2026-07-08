#!/usr/bin/env python3
"""
Run FinSearchComp T2 (Global) through Linkup's deep ("research") tier and grade
with the original FinSearchComp LLM-judge prompt.

Design guarantees (per requirements):
- NO restraints on Linkup: no request timeout, no token cap, full answer stored.
- NO restraints on the judge: no max_tokens, the judge always receives the FULL
  Linkup answer (never truncated), full judge response stored.
- EVERYTHING is stored incrementally to a JSONL as each item finishes, plus a
  final summary JSON -- so nothing ever needs to be re-run.

Retrieval/answer: Linkup /v1/search, depth="deep", outputType="sourcedAnswer".
Grader: OpenAI, verbatim FinSearchComp scoring prompt (score 1/0).

Usage: caffeinate -i -s python3 run_t2_linkup.py --limit 20
"""
import argparse, concurrent.futures as cf, csv, json, os, re, threading, time
import requests

ENV_PATH = "/Users/shaurya/Benchmarking/linkup-comparison/.env"
T2_CSV = "/private/tmp/claude-501/-Users-shaurya/6c666560-d933-4918-9eaa-48e3be114e70/scratchpad/web-search-api-evals/data/fin_search_comp_t2_global.csv"
GRADER_MODELS = ["gpt-5-mini", "gpt-4.1-mini", "gpt-4o-mini"]

# Verbatim FinSearchComp grader prompt (arXiv 2509.13160).
FIN_GRADER = """You are an intelligent judge and scorer for answers to financial questions. You will receive a <Question>, its <Reference Answer>, and a <Student Answer>. Some <Reference Answer>s may be supplemented with "Scoring Criteria". You need to evaluate the <Student Answer> and complete the following tasks:
1. Identify the final answer in the <Student Answer> (identification only). If the <Student Answer> is empty, assign a score of 0 directly.
2. Compare the final answer from the <Reference Answer> with the one from the <Student Answer>.
3. Judge whether the <Student Answer> is correct and assign a score of 1 or 0 only.
**Notes:**
1. Do not solve the question yourself. Only judge and score.
2. The <Reference Answer> is accurate and correct.
3. If the <Reference Answer> has 2+ key points, all must be present and correct for a 1.
4. If the <Student Answer> is empty or an error message, score 0.
5. Numerical values of the same magnitude in different formats are the same (12.45% vs 0.1245, 120,400,000 vs 120.4 million, 2/5 vs 0.4).
6. An answer is correct if its numerical component matches, even if the unit is omitted. Rounding errors are allowed where the reference says so.
**Output format:**
- Scoring Basis: (brief reason)
- JSON:
```
{{"answer_score": your score}}
```

<Question>:
{question}
<Reference Answer>:
{target}
<Student Answer>:
{predicted_answer}
"""


def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def linkup_deep(query, api_key):
    """No timeout, no token cap. Returns (answer_text, full_raw_json)."""
    r = requests.post(
        "https://api.linkup.so/v1/search",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"q": query, "depth": "deep", "outputType": "sourcedAnswer"},
        timeout=None,  # no timeout -- do not restrict Linkup
    )
    r.raise_for_status()
    data = r.json()
    return (data.get("answer", "") or ""), data


def grade(question, target, predicted, api_key, model_holder):
    """No max_tokens; judge receives the FULL predicted answer. Returns (score, full_prompt, full_raw)."""
    prompt = FIN_GRADER.format(question=question, target=target, predicted_answer=predicted)
    body = {"model": model_holder[0], "messages": [{"role": "user", "content": prompt}]}
    for attempt in range(len(GRADER_MODELS) + 1):
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=body, timeout=None,  # no timeout
        )
        if r.status_code == 200:
            txt = r.json()["choices"][0]["message"]["content"]
            m = re.findall(r'"answer_score"\s*:\s*([01])', txt)
            return (int(m[-1]) if m else 0), prompt, txt
        if r.status_code in (400, 404) and attempt < len(GRADER_MODELS):
            idx = min(attempt + 1, len(GRADER_MODELS) - 1)
            model_holder[0] = GRADER_MODELS[idx]
            body["model"] = model_holder[0]
            continue
        r.raise_for_status()
    return 0, prompt, "grader failed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    env = load_env(ENV_PATH)
    linkup_key = env.get("LINKUP_API_KEY")
    openai_key = env.get("OPENAI_API_KEY")
    assert linkup_key and openai_key, "missing keys in .env"

    with open(T2_CSV) as f:
        rows = list(csv.DictReader(f))[: args.limit]
    n_total = len(rows)
    print(f"Loaded {n_total} T2 questions | Linkup deep | no timeouts, no token caps\n", flush=True)

    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(outdir, exist_ok=True)
    jsonl_path = os.path.join(outdir, "t2_linkup_deep_full.jsonl")
    summary_path = os.path.join(outdir, "t2_linkup_deep_summary.json")

    def run_one(i_row):
        i, row = i_row
        q, gold = row["problem"], row["answer"]
        t0 = time.time()
        try:
            ans, raw = linkup_deep(q, linkup_key)
            err = None
        except Exception as e:
            ans, raw, err = "", None, f"{type(e).__name__}: {e}"
        return i, row, q, gold, ans, raw, err, round(time.time() - t0, 1)

    results = []
    model_holder = [GRADER_MODELS[0]]
    lock = threading.Lock()
    jf = open(jsonl_path, "w")
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, row, q, gold, ans, raw, err, dt in ex.map(run_one, list(enumerate(rows))):
            predicted = ans if ans else (err or "")
            score, judge_prompt, judge_raw = grade(q, gold, predicted, openai_key, model_holder)
            rec = {
                "idx": i,
                "dataset_id": row.get("id"),
                "question": q,
                "gold_answer": gold,
                "linkup_answer": ans,               # FULL, untruncated
                "linkup_raw_response": raw,          # FULL raw Linkup JSON (answer + sources)
                "linkup_error": err,
                "linkup_latency_s": dt,
                "judge_model": model_holder[0],
                "judge_prompt": judge_prompt,        # exact prompt sent
                "judge_raw_response": judge_raw,     # FULL judge output
                "score": score,
                "run_ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            with lock:
                jf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                jf.flush()
            results.append(rec)
            mark = "PASS" if score == 1 else "FAIL"
            print(f"[{mark}] {i+1:02d}/{n_total} ({dt}s) {q[:66]}", flush=True)
            print(f"        gold  : {gold[:80]}", flush=True)
            print(f"        linkup: {(ans or err)[:120].strip()}\n", flush=True)
    jf.close()

    total = sum(r["score"] for r in results)
    n = len(results)
    acc = total / n if n else 0
    print("=" * 62, flush=True)
    print(f"T2 Global (n={n}) | Linkup deep | grader={model_holder[0]}", flush=True)
    print(f"SCORE: {total}/{n} = {100*acc:.1f}%", flush=True)
    print("=" * 62, flush=True)

    with open(summary_path, "w") as f:
        json.dump({
            "dataset": "fin_search_comp_t2_global",
            "sampler": "linkup_deep_sourcedAnswer",
            "grader": model_holder[0],
            "n": n, "score": total, "accuracy": acc,
            "restraints": "none (no timeout, no token cap, full answer graded)",
            "per_question_scores": [{"idx": r["idx"], "score": r["score"]} for r in results],
        }, f, indent=2)
    print(f"full outputs -> {jsonl_path}", flush=True)
    print(f"summary      -> {summary_path}", flush=True)


if __name__ == "__main__":
    main()
