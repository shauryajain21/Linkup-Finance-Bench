#!/usr/bin/env python3
"""
Hand-graded verdicts for the final 31 T3 questions (idx 52, 54-83). Same method as the
other T3 graders: full answer vs FinSearchComp rubric (all key points; marginal errors
allowed). Prints the COMPLETE T3 (84) score by combining smoke + rest + final.
"""
import json, os

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

VERDICTS = {  # idx -> (score, note)
    52: (1, "Walmart goodwill delta -901 — exact"),
    54: (1, "AMD post-announcement change 4.47% — exact"),
    55: (0, "top-3 S&P gainers: added PLTR, missed GEV (vs VST/UAL/GEV)"),
    56: (0, "Google trading value 7.31B vs 7.34B (volume 4589 ok)"),
    57: (0, "5th-by-net-income Meta vs gold MSFT"),
    58: (0, "ASX open/close/change all wrong"),
    59: (1, "AMD 2022Q3 42% + Intel 42.6% — within rounding"),
    60: (0, "growth filter: only ORLY (missed CHKP)"),
    61: (1, "JGB 1y yield quarter ordering Q4>Q3>Q2>Q1 — exact"),
    62: (0, "US fixed-asset investment 13.13% vs 6.51%"),
    63: (0, "UK CO2 emissions values off (years right)"),
    64: (1, "COVID market-cap growth 61.92% ~ 61.95%"),
    65: (1, "Tesla-day Nvidia/Apple/Tesla moves — all exact"),
    66: (0, "price-fluctuation dates/values off"),
    67: (0, "SPBTC prices not provided (paywalled)"),
    68: (0, "VIX peak wrong date (Aug 2024 vs Apr 2025)"),
    69: (1, "20-day volatility spread 253.97 — exact"),
    70: (1, "Apple split day -$371.65, 4:1 — exact"),
    71: (1, "BofA 0.58% / WF -0.21% + magnitude — exact"),
    72: (1, "Boeing -0.62% / Lockheed +0.32% — exact"),
    73: (1, "London gold >$80 drop: all 5 dates correct"),
    74: (1, "S&P largest month April 2020 12.68% — exact"),
    75: (0, "NASDAQ market-cap list: several values off + GOOG/GOOGL merged"),
    76: (1, "lowest GDP/capita Europe: Ukraine — exact"),
    77: (1, "BTC strategy P&L -16,845 ~ -16,851.7 (within 1%)"),
    78: (1, "China sex ratio 110.8:100 — exact"),
    79: (1, "date Jan 25 2024 + 181 calendar days — exact"),
    80: (0, "NYSE top-3 gainers LLY/JPM vs gold BRK.A/TSM"),
    81: (0, "MSFT shares 421,763 vs 421,852 (89 off, 10-share margin)"),
    82: (1, "East Asia code sum 167 — exact"),
    83: (1, "Apple open vs Samsung event -$0.23 — exact"),
}


def main():
    rest = {json.loads(l)["idx"]: json.loads(l) for l in open(os.path.join(RESULTS, "t3_research_xl_rest.jsonl"))}
    graded, total = [], 0
    for idx in sorted(VERDICTS):
        score, note = VERDICTS[idx]
        total += score
        graded.append({"idx": idx, "question_no": idx + 1, "score": score, "note": note})
        print(f"[{'PASS' if score else 'FAIL'}] {idx+1:02d}  {note}")
    print("=" * 62)
    print(f"T3 final 31: {total}/{len(VERDICTS)} = {100*total/len(VERDICTS):.1f}%")

    # complete T3 (84) = smoke(20) + earlier rest(33) + final(31)
    smoke = json.load(open(os.path.join(RESULTS, "t3_research_xl_smoke_graded.json")))["score"]      # 13
    rest33 = json.load(open(os.path.join(RESULTS, "t3_research_xl_rest_graded.json")))["rest"]["score"]  # 18
    full_score = smoke + rest33 + total
    print(f"COMPLETE T3 (84): {smoke} + {rest33} + {total} = {full_score}/84 = {100*full_score/84:.1f}%")
    print("=" * 62)

    json.dump({"dataset": "fin_search_comp_t3_global",
               "judge": "manual (Claude) vs FinSearchComp rubric",
               "final_31": {"n": len(VERDICTS), "score": total},
               "complete_t3": {"n": 84, "score": full_score, "accuracy": full_score / 84},
               "graded": graded},
              open(os.path.join(RESULTS, "t3_research_xl_final_graded.json"), "w"), indent=2)
    print(f"saved -> {os.path.join(RESULTS, 't3_research_xl_final_graded.json')}")


if __name__ == "__main__":
    main()
