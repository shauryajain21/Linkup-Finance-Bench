#!/usr/bin/env python3
"""
Grade the stored Linkup research answers against FinSearchComp gold answers.

This is a DETERMINISTIC numeric judge that encodes the FinSearchComp rubric's
numeric clauses: same magnitude in any format is equal ($, commas, units dropped),
rounding errors allowed, sign ignored where the gold lists both signs. It reads the
stored JSONL (no Linkup re-run) and writes a graded file. An LLM judge (e.g.
gpt-5-mini) can re-grade the same stored answers later for a second opinion.
"""
import json, os, re

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
FULL = os.path.join(RESULTS, "t2_research_xl_full.jsonl")


def nums(text):
    """All numeric values in a string, normalized (drop $ and thousands separators)."""
    cleaned = text.replace(",", "")
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", cleaned)]


def extracted_answer(linkup_text):
    """The number the model put after '**Answer:**' (fallback: first number)."""
    m = re.search(r"\*\*Answer:\*\*\s*\$?\s*(-?[\d,]+(?:\.\d+)?)", linkup_text)
    if m:
        return float(m.group(1).replace(",", ""))
    n = nums(linkup_text)
    return n[0] if n else None


def matches(pred, gold_text):
    if pred is None:
        return False
    for g in nums(gold_text):
        # rounding-tolerant, sign-insensitive (gold sometimes lists both signs)
        if abs(abs(pred) - abs(g)) <= max(1.0, abs(g) * 0.005):
            return True
    return False


def main():
    recs = [json.loads(l) for l in open(FULL)]
    recs.sort(key=lambda r: r["idx"])
    graded = []
    total = 0
    for r in recs:
        ans = r.get("linkup_answer") or ""
        pred = extracted_answer(ans)
        ok = r["status"] == "completed" and matches(pred, r["gold_answer"])
        score = 1 if ok else 0
        total += score
        graded.append({
            "idx": r["idx"], "question": r["question"], "gold_answer": r["gold_answer"],
            "extracted_answer": pred, "score": score, "status": r["status"],
            "latency_s": r.get("elapsed_s"),
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {r['idx']+1:02d}  pred={pred}  gold={r['gold_answer'][:40]}")

    n = len(graded)
    acc = total / n if n else 0
    print("=" * 60)
    print(f"FinSearchComp T2 Global (n={n}) | Linkup research XL")
    print(f"SCORE: {total}/{n} = {100*acc:.1f}%")
    print("=" * 60)

    out = os.path.join(RESULTS, "t2_research_xl_graded.json")
    json.dump({
        "dataset": "fin_search_comp_t2_global",
        "sampler": "linkup_research (mode=answer, reasoningDepth=XL, sourcedAnswer)",
        "judge": "deterministic numeric match (FinSearchComp rubric)",
        "n": n, "score": total, "accuracy": acc,
        "avg_latency_s": round(sum(g["latency_s"] or 0 for g in graded) / n, 1),
        "graded": graded,
    }, open(out, "w"), indent=2)
    print(f"saved -> {out}")


if __name__ == "__main__":
    main()
