"""Summaries and markdown generation."""
import json
import statistics

def build_baseline_summary(results: dict):
    """
    results dict keys:
      contamination_rows (list of dicts)
      fermat_rows (list of dicts with 'case_id','fermat_steps','near_square_flag')
      floor_rows (list of dicts with 'case_id','pass_rate')
      decoy_rows (list of dicts with 'case_id','decoy_count')
      official_replay_ok (bool)
      floor_window (int)
      floor_stride (int)
      n_cases (int)
    Returns summary dict.
    """
    contamination = results['contamination_rows']
    fermat = results['fermat_rows']
    floor = results['floor_rows']
    decoy = results['decoy_rows']

    n_near = sum(1 for c in contamination if c['near_square_flag'])
    n_non = len(contamination) - n_near
    audit_fail = sum(1 for c in contamination if c.get('audit_integrity_fail'))
    fermat_near_steps = [r['fermat_steps'] for r in fermat if r['near_square_flag'] and r['fermat_steps'] is not None]
    fermat_non_steps = [r['fermat_steps'] for r in fermat if not r['near_square_flag'] and r['fermat_steps'] is not None]
    floor_rates = [r['pass_rate'] for r in floor]
    decoy_cases = sum(1 for d in decoy if d['decoy_count'] > 0)

    summary = {
        "package": "pgs_cih1_baselines_deepseek_v1",
        "n_cases": len(contamination),
        "n_near_square": n_near,
        "n_non_near_square": n_non,
        "near_square_rate": n_near / len(contamination) if contamination else 0.0,
        "audit_integrity_failures": audit_fail,
        "fermat_steps_median_non_near_square": statistics.median(fermat_non_steps) if fermat_non_steps else None,
        "fermat_steps_median_near_square": statistics.median(fermat_near_steps) if fermat_near_steps else None,
        "floor_pass_rate_median": statistics.median(floor_rates) if floor_rates else None,
        "floor_window": results['floor_window'],
        "floor_stride": results['floor_stride'],
        "decoy_cases_with_at_least_one": decoy_cases,
        "official_replay_ok": results['official_replay_ok'],
        "warnings": [
            "All results are audit baselines, not factorisation claims.",
            "High floor density implies reciprocity alone is not a discriminating signal.",
            "Near-square semiprimes factor in 0 Fermat steps – exclude from general hardness claims."
        ],
        "allowed_claim_language": [
            "audit baseline only",
            "hypothesis support for CIH-1 interpretation",
            "no PGS factorisation claim"
        ]
    }
    return summary

def write_markdown_summary(summary: dict, path: str):
    lines = [
        "# CIH‑1 Baseline Summary (DeepSeek)",
        "",
        f"**Package:** {summary['package']}",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Cases processed | {summary['n_cases']} |",
        f"| Near-square semiprimes | {summary['n_near_square']} (rate {summary['near_square_rate']:.2%}) |",
        f"| Non‑near‑square | {summary['n_non_near_square']} |",
        f"| Audit integrity failures | {summary['audit_integrity_failures']} |",
        f"| Fermat median steps (near‑square) | {summary['fermat_steps_median_near_square']} |",
        f"| Fermat median steps (non‑near‑square) | {summary['fermat_steps_median_non_near_square']} |",
        f"| Floor reciprocity median pass rate | {summary['floor_pass_rate_median']:.4f} (window={summary['floor_window']}, stride={summary['floor_stride']}) |",
        f"| Cases with decoy reciprocal pairs | {summary['decoy_cases_with_at_least_one']} |",
        f"| Official fixture replay OK | {summary['official_replay_ok']} |",
        "",
        "### Warnings",
    ]
    for w in summary['warnings']:
        lines.append(f"- {w}")
    lines.append("")
    lines.append("### Allowed claim language")
    for a in summary['allowed_claim_language']:
        lines.append(f"- {a}")
    with open(path, 'w') as fh:
        fh.write('\n'.join(lines))
