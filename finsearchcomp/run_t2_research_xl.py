#!/usr/bin/env python3
"""
FinSearchComp T2 (Global) via Linkup's ASYNC RESEARCH endpoint in XL mode.

Linkup call: POST /v1/research  {q, outputType: sourcedAnswer, mode: answer, reasoningDepth: XL}
             then poll GET /v1/research/{id} until completed/failed.

Guarantees (per requirements):
- NO restraints on Linkup: XL reasoning, no token cap, poll until the task truly
  completes (never truncate the answer), full raw output stored.
- EVERYTHING stored incrementally so nothing is ever re-run:
    results/t2_research_xl_tasks.json   <- submitted task ids (resume-safe)
    results/t2_research_xl_full.jsonl   <- one full record per question
- Grading is a separate phase (reads the JSONL); Linkup outputs are stored so the
  judge can run later without re-hitting Linkup.

Usage: caffeinate -i -s python3 run_t2_research_xl.py --limit 20
"""
import argparse, csv, json, os, time
import requests

ENV_PATH = "/Users/shaurya/Benchmarking/linkup-comparison/.env"
T2_CSV = "/private/tmp/claude-501/-Users-shaurya/6c666560-d933-4918-9eaa-48e3be114e70/scratchpad/web-search-api-evals/data/fin_search_comp_t2_global.csv"
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

POLL_EVERY_S = 8          # >1s to respect rate limit
MAX_WAIT_S = 3600         # safety net per task (~60 min); does not cap answer quality


def load_env(path):
    env = {}
    for line in open(path):
        s = line.strip()
        if s and not s.startswith("#") and "=" in s:
            k, v = s.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def submit(q, key):
    r = requests.post(
        "https://api.linkup.so/v1/research",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"q": q, "outputType": "sourcedAnswer", "mode": "answer", "reasoningDepth": "XL"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def poll(task_id, key):
    r = requests.get(
        f"https://api.linkup.so/v1/research/{task_id}",
        headers={"Authorization": f"Bearer {key}"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()

    env = load_env(ENV_PATH)
    key = env.get("LINKUP_API_KEY")
    assert key, "missing LINKUP_API_KEY"
    os.makedirs(RESULTS, exist_ok=True)

    rows = list(csv.DictReader(open(T2_CSV)))[: args.limit]
    print(f"Submitting {len(rows)} T2 questions -> Linkup research (mode=answer, reasoningDepth=XL)\n", flush=True)

    # ---- submit all (async, returns immediately) ----
    tasks = []
    for i, row in enumerate(rows):
        q, gold = row["problem"], row["answer"]
        try:
            resp = submit(q, key)
            tid = resp.get("id")
            print(f"  submitted {i+1:02d}/{len(rows)}  id={tid}", flush=True)
        except Exception as e:
            tid, resp = None, {"error": f"{type(e).__name__}: {e}"}
            print(f"  SUBMIT FAILED {i+1:02d}: {e}", flush=True)
        tasks.append({"idx": i, "id": tid, "question": q, "gold_answer": gold,
                      "dataset_id": row.get("id"), "submit_response": resp,
                      "submitted_ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    json.dump(tasks, open(os.path.join(RESULTS, "t2_research_xl_tasks.json"), "w"), indent=2)
    print(f"\nAll submitted. Polling every {POLL_EVERY_S}s until each completes...\n", flush=True)

    # ---- poll to completion, storing each full result as it lands ----
    jsonl = open(os.path.join(RESULTS, "t2_research_xl_full.jsonl"), "w")
    pending = {t["idx"]: t for t in tasks if t["id"]}
    for t in tasks:
        if not t["id"]:
            rec = {**t, "status": "submit_failed", "linkup_answer": "", "linkup_sources": [],
                   "final_response": t["submit_response"]}
            jsonl.write(json.dumps(rec, ensure_ascii=False) + "\n"); jsonl.flush()

    start = {idx: time.time() for idx in pending}
    done = 0
    while pending:
        time.sleep(POLL_EVERY_S)
        for idx in list(pending):
            t = pending[idx]
            try:
                state = poll(t["id"], key)
            except Exception as e:
                print(f"  poll error idx={idx}: {e}", flush=True)
                continue
            status = state.get("status")
            if status in ("completed", "failed") or (time.time() - start[idx]) > MAX_WAIT_S:
                out = state.get("output") or {}
                rec = {
                    "idx": t["idx"], "dataset_id": t["dataset_id"],
                    "question": t["question"], "gold_answer": t["gold_answer"],
                    "task_id": t["id"], "status": status,
                    "linkup_answer": out.get("answer", "") if isinstance(out, dict) else "",
                    "linkup_sources": out.get("sources", []) if isinstance(out, dict) else [],
                    "linkup_error": state.get("error"),
                    "final_response": state,           # FULL raw research task object
                    "completed_ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "elapsed_s": round(time.time() - start[idx], 1),
                }
                jsonl.write(json.dumps(rec, ensure_ascii=False) + "\n"); jsonl.flush()
                done += 1
                ans = (rec["linkup_answer"] or rec["linkup_error"] or "")[:110].replace("\n", " ")
                print(f"  [{status}] {idx+1:02d}/{len(rows)} ({rec['elapsed_s']}s)  {ans}", flush=True)
                del pending[idx]
    jsonl.close()
    print(f"\nDONE. {done} tasks stored -> {os.path.join(RESULTS, 't2_research_xl_full.jsonl')}", flush=True)
    print("Next: grade the stored answers (judge phase).", flush=True)


if __name__ == "__main__":
    main()
