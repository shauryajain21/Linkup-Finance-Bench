#!/usr/bin/env python3
"""
Batch runner: FinSearchComp T2 Global via Linkup research (XL), for an index range,
throttled to a target QPS on both submit and poll. Appends to a JSONL so it composes
with the earlier 20-question run to cover the full 120.

Same guarantees as run_t2_research_xl.py: no timeouts, no token caps, XL reasoning,
full raw output stored incrementally, resume-safe task-id file.

Usage: caffeinate -i -s python3 run_t2_research_xl_batch.py --start 20 --end 120 --qps 10
"""
import argparse, csv, json, os, time
import requests

ENV_PATH = "/Users/shaurya/Benchmarking/linkup-comparison/.env"
T2_CSV = "/private/tmp/claude-501/-Users-shaurya/6c666560-d933-4918-9eaa-48e3be114e70/scratchpad/web-search-api-evals/data/fin_search_comp_t2_global.csv"
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

POLL_EVERY_S = 8
MAX_WAIT_S = 3600


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
        headers={"Authorization": f"Bearer {key}"}, timeout=60,
    )
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=20)
    ap.add_argument("--end", type=int, default=120)
    ap.add_argument("--indices", default=None, help="comma-separated 0-based indices; overrides start/end")
    ap.add_argument("--csv", default=T2_CSV, help="dataset CSV path (default T2 Global)")
    ap.add_argument("--qps", type=float, default=10.0)
    ap.add_argument("--out", default=os.path.join(RESULTS, "t2_research_xl_remaining.jsonl"))
    ap.add_argument("--tasks", default=os.path.join(RESULTS, "t2_research_xl_remaining_tasks.json"))
    args = ap.parse_args()
    gap = 1.0 / args.qps  # spacing to hold target QPS

    env = load_env(ENV_PATH)
    key = env.get("LINKUP_API_KEY")
    assert key, "missing LINKUP_API_KEY"
    os.makedirs(RESULTS, exist_ok=True)

    all_rows = list(csv.DictReader(open(args.csv)))
    if args.indices:
        idxs = [int(x) for x in args.indices.split(",") if x.strip() != ""]
        rows = [(i, all_rows[i]) for i in idxs]
    else:
        rows = [(i, all_rows[i]) for i in range(args.start, min(args.end, len(all_rows)))]
    print(f"Running T2 idx [{args.start},{min(args.end,len(all_rows))}) = {len(rows)} questions "
          f"| Linkup research XL | submit+poll throttled to {args.qps} QPS\n", flush=True)

    # ---- submit, throttled to QPS ----
    tasks = []
    for i, row in rows:
        q, gold = row["problem"], row["answer"]
        t0 = time.time()
        try:
            resp = submit(q, key); tid = resp.get("id")
            print(f"  submitted idx={i:03d} id={tid}", flush=True)
        except Exception as e:
            tid, resp = None, {"error": f"{type(e).__name__}: {e}"}
            print(f"  SUBMIT FAILED idx={i:03d}: {e}", flush=True)
        tasks.append({"idx": i, "id": tid, "question": q, "gold_answer": gold,
                      "dataset_id": row.get("id"), "submit_response": resp,
                      "submitted_ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
        dt = time.time() - t0
        if dt < gap:
            time.sleep(gap - dt)
    json.dump(tasks, open(args.tasks, "w"), indent=2)
    print(f"\nAll submitted. Polling (<= {args.qps} QPS) until each completes...\n", flush=True)

    # ---- poll to completion, storing each result (append) ----
    jsonl = open(args.out, "a")
    for t in tasks:
        if not t["id"]:
            jsonl.write(json.dumps({**t, "status": "submit_failed", "linkup_answer": "",
                                    "linkup_sources": [], "final_response": t["submit_response"]},
                                   ensure_ascii=False) + "\n"); jsonl.flush()
    pending = {t["idx"]: t for t in tasks if t["id"]}
    start = {idx: time.time() for idx in pending}
    done = 0
    while pending:
        sweep0 = time.time()
        for idx in list(pending):
            t = pending[idx]
            try:
                state = poll(t["id"], key)
            except Exception as e:
                print(f"  poll error idx={idx}: {e}", flush=True); time.sleep(gap); continue
            status = state.get("status")
            if status in ("completed", "failed") or (time.time() - start[idx]) > MAX_WAIT_S:
                out = state.get("output") or {}
                rec = {
                    "idx": t["idx"], "dataset_id": t["dataset_id"], "question": t["question"],
                    "gold_answer": t["gold_answer"], "task_id": t["id"], "status": status,
                    "linkup_answer": out.get("answer", "") if isinstance(out, dict) else "",
                    "linkup_sources": out.get("sources", []) if isinstance(out, dict) else [],
                    "linkup_error": state.get("error"), "final_response": state,
                    "completed_ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "elapsed_s": round(time.time() - start[idx], 1),
                }
                jsonl.write(json.dumps(rec, ensure_ascii=False) + "\n"); jsonl.flush()
                done += 1
                ans = (rec["linkup_answer"] or rec["linkup_error"] or "")[:90].replace("\n", " ")
                print(f"  [{status}] idx={idx:03d} ({rec['elapsed_s']}s) done={done}/{len(tasks)}  {ans}", flush=True)
                del pending[idx]
            time.sleep(gap)  # hold QPS across poll GETs
        rem = POLL_EVERY_S - (time.time() - sweep0)
        if rem > 0 and pending:
            time.sleep(rem)
    jsonl.close()
    print(f"\nDONE. {done} tasks stored -> {args.out}", flush=True)


if __name__ == "__main__":
    main()
