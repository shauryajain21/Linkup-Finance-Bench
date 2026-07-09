#!/usr/bin/env python3
"""
Hand-graded verdicts for the 33 additional T3 questions (from the wave run that was
stopped). Same method as t3_smoke_grade.py: read each full answer vs the FinSearchComp
rubric (all key points correct; marginal errors allowed). Prints a combined T3 score
(smoke 20 + these 33 = 53 graded). Re-grade with an LLM judge later; answers are stored.
"""
import json, os

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# idx (0-based) -> (score, note)
VERDICTS = {
    20: (1, "Tesla D&A/net income lowest 2022 29.84% — exact"),
    21: (1, "Apple/Tesla inv turnover ratio 4 yrs — all exact"),
    22: (1, "WF/Nvidia net income multiple 4 yrs — all exact"),
    23: (0, "debt/asset ranking wrong (Apple 29.22 vs gold WF 90.62/Apple 84.40/Tesla 39.64)"),
    24: (1, "Apple vs Nvidia gross margin gap 4 yrs — all exact"),
    25: (1, "highest Facebook 33.38 / lowest Tesla 10.25 — exact"),
    26: (1, "KOSPI peak 2021 3316.08 — exact"),
    27: (1, "Nikkei positive months — all 5 exact"),
    28: (0, "FTSE add/delete incomplete (only CCEP/BLND; missing HL.L, BAB.L)"),
    29: (0, "S&P100B+ company count 115 vs gold 97 (share-diff 75.03 ok)"),
    30: (0, "top-3 ROE wrong (Colgate 531 vs gold Home Depot 1450.48)"),
    31: (0, "wrong constituents (Newmont vs GOOG/AMZN/FTNT/DXCM/TSLA)"),
    32: (0, "wrong ETFs (UVIX/UVXY vs Direxion China set)"),
    33: (1, "Tesla share-accumulation puzzle 70,000 — exact"),
    34: (1, "Nvidia highest-volume day change -16.97% — exact"),
    35: (0, "wrong stock (Comcast vs PDD 1183.87B)"),
    36: (1, "Tesla post-election high $358.64 — exact"),
    37: (1, "Magnificent-7 excess return 190.69% — exact"),
    38: (1, "S&P max drawdown 20.83% + peak/trough dates — exact"),
    39: (0, "IPO top-3: Arm ok but Mobileye/Lineage wrong (vs WBD/Ferrovial)"),
    40: (0, "BTC 5-day streak count 0 vs gold 2 periods"),
    41: (0, "Lilly/Google liab-asset gap 0.52 vs gold 48-54%/yr"),
    42: (0, "UnitedHealth ROIC 27.77 vs 22.19 (definition mismatch)"),
    43: (0, "J&J intl revenue change: 2023 -2.06 vs gold -3.37"),
    44: (1, "Oracle total-asset growth 4 yrs — all exact"),
    45: (1, "Pfizer turnover on settlement day 0.55% — exact"),
    46: (0, "highest-return-by-year: only 2024 AppLovin right (vs Vaxcyte/Affirm)"),
    47: (0, "DJIA PE-TTM 36.86 vs 36.37 (outside 0.1 margin)"),
    48: (1, "Nasdaq100 avg daily volume Tesla 17474.14 ~ 17477.42 (rounding)"),
    49: (1, "index spread Dec 31 2024 0.80% — exact"),
    50: (0, "Exxon chem growth: 2021/2022 wrong (23.9/-3.5 vs 59.62/-25.07)"),
    51: (1, "Amazon financing cash flow decrease 10,708 — exact"),
    53: (1, "Powell-speech-day Nasdaq range 475 — exact"),
}


def load(path):
    return {json.loads(l)["idx"]: json.loads(l) for l in open(path)}


def main():
    rest = load(os.path.join(RESULTS, "t3_research_xl_rest.jsonl"))
    graded, total = [], 0
    for idx in sorted(rest):
        score, note = VERDICTS[idx]
        total += score
        graded.append({"idx": idx, "question_no": idx + 1, "score": score, "note": note})
        print(f"[{'PASS' if score else 'FAIL'}] {idx+1:02d}  {note}")
    n = len(graded)
    print("=" * 62)
    print(f"T3 rest (n={n}): {total}/{n} = {100*total/n:.1f}%")

    # combined with smoke
    smoke = json.load(open(os.path.join(RESULTS, "t3_research_xl_smoke_graded.json")))
    combo_score = total + smoke["score"]
    combo_n = n + smoke["n"]
    print(f"T3 COMBINED (smoke {smoke['score']}/{smoke['n']} + rest {total}/{n}): "
          f"{combo_score}/{combo_n} = {100*combo_score/combo_n:.1f}%")
    print("=" * 62)

    json.dump({"dataset": "fin_search_comp_t3_global",
               "judge": "manual (Claude) vs FinSearchComp rubric",
               "rest": {"n": n, "score": total},
               "combined_with_smoke": {"n": combo_n, "score": combo_score,
                                       "accuracy": combo_score / combo_n},
               "graded": graded},
              open(os.path.join(RESULTS, "t3_research_xl_rest_graded.json"), "w"), indent=2)
    print(f"saved -> {os.path.join(RESULTS, 't3_research_xl_rest_graded.json')}")


if __name__ == "__main__":
    main()
