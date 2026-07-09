#!/usr/bin/env python3
"""
Hand-graded verdicts for the T3 (complex) smoke test.

T3 answers are multi-part (orderings, ranges, several required figures), which the
deterministic numeric judge in grade_stored.py cannot score correctly. These verdicts
were assigned by reading each full answer against the FinSearchComp rubric (all key
points must be correct; marginal errors allowed). Reads the stored answers and writes
results/t3_research_xl_smoke_graded.json. Re-grade with an LLM judge (gpt-5-mini) later
for an independent pass -- the raw answers are stored, no Linkup re-run needed.
"""
import json, os

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# idx (0-based) -> (score, note)
VERDICTS = {
    0:  (1, "3 rates + ordering exact (7.34>7.30>7.19)"),
    1:  (1, "USDCNH highest, 7.43"),
    2:  (1, "8.12"),
    3:  (1, "0.02%"),
    4:  (1, "No + April 8 + all 3 values exact (7.9155/0.9270/7.2038)"),
    5:  (1, "Nasdaq, 5.33%"),
    6:  (0, "said NOT same (Nasdaq vs CSI1000); gold: SAME, CSI 1000"),
    7:  (0, "S&P500 50.40; gold: Nasdaq 60.77T"),
    8:  (0, "110.50 higher; gold: 8,847,105.72 billion yuan (couldn't source data)"),
    9:  (1, "0.67"),
    10: (0, "Sunrun -43.84%; gold: NTCL -68.80%"),
    11: (1, "2.56 pp lower"),
    12: (1, "339.34, +138.35 vs Amazon"),
    13: (0, "Tesla + turnover 15.69~15.67 ok, but trading value 171.78 vs 172.67 off beyond rounding"),
    14: (0, "ROIC 24.62%; gold 22.19% (definition mismatch)"),
    15: (1, "184.53, 43.18%"),
    16: (1, "4-year Oracle growth table exact"),
    17: (1, "TSMC 0.42 / Boeing 7.44 / Goldman 0.23 all exact"),
    18: (0, "Boeing -9.91; gold -11.51 (beyond 0.01 margin)"),
    19: (1, "TSMC 856.29 ~ 856.30"),
}


def main():
    recs = {json.loads(l)["idx"]: json.loads(l) for l in open(os.path.join(RESULTS, "t3_research_xl_smoke.jsonl"))}
    graded, total = [], 0
    for idx in sorted(recs):
        score, note = VERDICTS[idx]
        total += score
        graded.append({"idx": idx, "question_no": idx + 1, "question": recs[idx]["question"],
                       "gold_answer": recs[idx]["gold_answer"], "score": score, "note": note})
        print(f"[{'PASS' if score else 'FAIL'}] {idx+1:02d}  {note}")
    n = len(graded)
    print("=" * 60)
    print(f"FinSearchComp T3 Global smoke (n={n}) | Linkup research XL | hand-graded")
    print(f"SCORE: {total}/{n} = {100*total/n:.1f}%")
    print("=" * 60)
    json.dump({"dataset": "fin_search_comp_t3_global (first 20)",
               "sampler": "linkup_research (mode=answer, reasoningDepth=XL)",
               "judge": "manual (Claude) vs FinSearchComp rubric — multi-part answers",
               "n": n, "score": total, "accuracy": total / n, "graded": graded},
              open(os.path.join(RESULTS, "t3_research_xl_smoke_graded.json"), "w"), indent=2)
    print(f"saved -> {os.path.join(RESULTS, 't3_research_xl_smoke_graded.json')}")


if __name__ == "__main__":
    main()
