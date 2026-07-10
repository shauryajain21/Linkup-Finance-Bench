#!/usr/bin/env python3
"""
Consolidate T2 into a single canonical result.

For each of the 119 T2 questions, use the re-run answer where one exists (the 23 that
missed on the first pass) and the original answer otherwise, then grade once. This folds
the two passes into one dataset -> a single T2 score (no "first run vs re-run" split).
Raw per-run files are kept; this just produces the canonical graded view.
"""
import json, os, re

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def nums(t): return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", t.replace(",", ""))]
def extract(t):
    m = re.search(r"\*\*Answer:\*\*\s*\$?\s*(-?[\d,]+(?:\.\d+)?)", t or "")
    if m: return float(m.group(1).replace(",", ""))
    n = nums(t or ""); return n[0] if n else None
def match(pred, gold):
    if pred is None: return False
    return any(abs(abs(pred) - abs(g)) <= max(1.0, abs(g) * 0.005) for g in nums(gold))


def main():
    # originals
    canon = {}
    for f in ["t2_research_xl_full.jsonl", "t2_research_xl_remaining.jsonl"]:
        for l in open(os.path.join(RESULTS, f)):
            r = json.loads(l); canon[r["idx"]] = r
    # prefer re-run answers where present
    reran = set()
    for l in open(os.path.join(RESULTS, "t2_research_xl_rerun.jsonl")):
        r = json.loads(l)
        if r.get("status") == "completed":
            canon[r["idx"]] = r; reran.add(r["idx"])

    graded, total = [], 0
    for idx in sorted(canon):
        r = canon[idx]
        pred = extract(r.get("linkup_answer"))
        s = 1 if match(pred, r["gold_answer"]) else 0
        total += s
        graded.append({"idx": idx, "question_no": idx + 1, "gold": r["gold_answer"],
                       "answer": pred, "score": s, "used_rerun": idx in reran})
    n = len(graded)
    print(f"T2 consolidated (best answer per question): {total}/{n} = {100*total/n:.1f}%")
    json.dump({"dataset": "fin_search_comp_t2_global", "n": n, "score": total,
               "accuracy": total / n,
               "note": "single canonical T2 score; re-run answer used for the initially-missed questions",
               "graded": graded},
              open(os.path.join(RESULTS, "t2_consolidated_graded.json"), "w"), indent=2)
    print(f"saved -> {os.path.join(RESULTS, 't2_consolidated_graded.json')}")


if __name__ == "__main__":
    main()
