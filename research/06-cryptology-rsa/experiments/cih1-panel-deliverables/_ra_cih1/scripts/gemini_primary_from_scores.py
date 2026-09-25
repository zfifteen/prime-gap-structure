#!/usr/bin/env python3
"""Compute Gemini freeze primary metric from ChatGPT case_scores.jsonl."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-scores", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--alpha", type=float, default=0.05)
    args = ap.parse_args()

    rows = [
        json.loads(line)
        for line in args.case_scores.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    included = [r for r in rows if not r.get("excluded")]
    deltas = []
    for r in included:
        dc = r.get("D_c")
        du = r.get("control_median_D_u")
        if dc is None or du is None:
            continue
        deltas.append(du - dc)

    if not deltas:
        summary = {
            "n_total": len(rows),
            "n_included": 0,
            "median_delta_distance": None,
            "mean_delta_distance": None,
            "n_positive_delta": 0,
            "n_negative_delta": 0,
            "n_zero_delta": 0,
            "decision_gemini_text_rule": "aborted_insufficient_n",
            "allowed_claim_language": [
                "measured on hold-out corpus",
                "hypothesis",
                "no verified/validated language",
                "no factorization claim",
            ],
        }
    else:
        med = statistics.median(deltas)
        mean = statistics.fmean(deltas)
        pos = sum(1 for d in deltas if d > 0)
        neg = sum(1 for d in deltas if d < 0)
        zero = sum(1 for d in deltas if d == 0)
        # Exact one-sided sign test on nonzero deltas (same family as ChatGPT tooling).
        from math import comb

        n = pos + neg
        if n == 0:
            p_one = 1.0
        else:
            # P(X >= pos) under Binomial(n, 0.5), one-sided carrier-better
            p_one = sum(comb(n, k) for k in range(pos, n + 1)) / (2**n)
        gemini_reject = (len(included) >= 30) and (med > 0) and (p_one < args.alpha)
        decision = "carrier_better" if gemini_reject else (
            "aborted_insufficient_n" if len(included) < 30 else "no_difference_or_control"
        )
        summary = {
            "n_total": len(rows),
            "n_included": len(included),
            "n_excluded": len(rows) - len(included),
            "n_deltas": len(deltas),
            "median_delta_distance": med,
            "mean_delta_distance": mean,
            "n_positive_delta": pos,
            "n_negative_delta": neg,
            "n_zero_delta": zero,
            "sign_test_one_sided_p": p_one,
            "alpha": args.alpha,
            "decision_gemini_text_rule": decision,
            "gemini_rule": "Reject H0 if p < 0.05 and median_delta_distance > 0 (sign-test stand-in; freeze named Wilcoxon)",
            "note": "Wilcoxon signed-rank not implemented in stdlib; exact sign test used as transparent substitute. Label as measured/hypothesis only.",
            "allowed_claim_language": [
                "measured on hold-out corpus",
                "hypothesis",
                "no verified/validated language",
                "no factorization claim",
            ],
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
