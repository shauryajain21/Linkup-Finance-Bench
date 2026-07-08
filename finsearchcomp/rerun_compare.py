#!/usr/bin/env python3
"""
Compare the re-run of the 23 failed T2 questions against the first attempt.
Reads stored answers only (no Linkup re-run) and writes results/t2_rerun_compare.json.
"""
import json, os, re

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def nums(t):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", t.replace(",", ""))]


def extract(t):
    m = re.search(r"\*\*Answer:\*\*\s*\$?\s*(-?[\d,]+(?:\.\d+)?)", t or "")
    if m:
        return float(m.group(1).replace(",", ""))
    n = nums(t or "")
    return n[0] if n else None


def match(pred, gold):
    if pred is None:
        return False
    return any(abs(abs(pred) - abs(g)) <= max(1.0, abs(g) * 0.005) for g in nums(gold))


def main():
    orig = {}
    for f in ["t2_research_xl_full.jsonl", "t2_research_xl_remaining.jsonl"]:
        for l in open(os.path.join(RESULTS, f)):
            r = json.loads(l); orig[r["idx"]] = r
    rerun = {}
    for l in open(os.path.join(RESULTS, "t2_research_xl_rerun.jsonl")):
        r = json.loads(l); rerun[r["idx"]] = r

    rows, flipped = [], 0
    for idx in sorted(rerun):
        g = orig[idx]["gold_answer"]
        p1, p2 = extract(orig[idx].get("linkup_answer")), extract(rerun[idx].get("linkup_answer"))
        s1, s2 = match(p1, g), match(p2, g)
        if not s1 and s2:
            flipped += 1
        rows.append({"idx": idx, "question_no": idx + 1, "gold": g,
                     "run1_pred": p1, "run1_correct": s1,
                     "run2_pred": p2, "run2_correct": s2,
                     "newly_correct": (not s1 and s2), "regressed": (s1 and not s2)})

    out = {
        "reran": len(rows), "newly_correct_on_rerun": flipped,
        "original_score": "96/119 = 80.7%",
        "best_of_both_score": f"{96 + flipped}/119 = {100*(96+flipped)/119:.1f}%",
        "rows": rows,
    }
    json.dump(out, open(os.path.join(RESULTS, "t2_rerun_compare.json"), "w"), indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))
    print(f"saved -> {os.path.join(RESULTS, 't2_rerun_compare.json')}")


if __name__ == "__main__":
    main()
