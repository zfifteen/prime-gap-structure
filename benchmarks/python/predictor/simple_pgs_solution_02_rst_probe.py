"""Test Gemini Solution 2: Residual Symmetry Termination."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor.simple_pgs_generator import (  # noqa: E402
    DEFAULT_CANDIDATE_BOUND,
    DEFAULT_VISIBLE_DIVISOR_BOUND,
    PGS_SOURCE,
    WHEEL_OPEN_RESIDUES_MOD30,
    closure_reason,
)


DEFAULT_INPUT = (
    ROOT / "output" / "simple_pgs_shadow_seed_gwr_solution_probe" / "rows.jsonl"
)
DEFAULT_OUTPUT_DIR = ROOT / "output" / "simple_pgs_solution_02_rst_probe"
DEFAULT_SCALES = [10**15, 10**18]


def read_jsonl(path: Path) -> list[dict[str, object]]:
    """Read JSONL rows."""
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    """Write LF-terminated CSV rows."""
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_json(record: dict[str, object], path: Path) -> None:
    """Write LF-terminated JSON."""
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def closure_bit(p: int, n: int, visible_divisor_bound: int) -> int:
    """Return one binary PGS closure state for n relative to p."""
    offset = int(n) - int(p)
    return 1 if closure_reason(int(p), offset, int(visible_divisor_bound)) else 0


def closure_state_map(
    p: int,
    lo: int,
    hi: int,
    visible_divisor_bound: int,
) -> dict[int, int]:
    """Return cached closure states on [lo, hi)."""
    return {
        n: closure_bit(int(p), n, int(visible_divisor_bound))
        for n in range(int(lo), int(hi))
    }


def closure_vector(
    cache: dict[int, int],
    lo: int,
    hi: int,
) -> list[int]:
    """Return binary closure states on [lo, hi)."""
    return [cache[n] for n in range(int(lo), int(hi))]


def pre_shadow_vector(
    mode: str,
    cache: dict[int, int],
    p: int,
    seed_q0: int,
    vector_length: int,
) -> list[int]:
    """Return the pre-shadow vector for one RST mode."""
    if mode == "fixed_128_pre_shadow":
        return closure_vector(
            cache,
            int(seed_q0) - int(vector_length),
            int(seed_q0),
        )
    if mode == "anchor_prefix_to_seed":
        return closure_vector(
            cache,
            int(p) + 1,
            int(seed_q0) + 1,
        )
    raise ValueError(f"unknown vector mode: {mode}")


def candidate_window(
    domain: str,
    p: int,
    seed_q0: int,
    candidate_bound: int,
) -> list[int]:
    """Return candidate x values for one RST domain."""
    if domain == "all_integer_anchor_bound":
        upper = int(p) + int(candidate_bound)
        return list(range(int(seed_q0) + 1, upper + 1))
    if domain == "all_integer_seed_bound":
        upper = int(seed_q0) + int(candidate_bound)
        return list(range(int(seed_q0) + 1, upper + 1))
    if domain == "visible_open_anchor_bound":
        upper = int(p) + int(candidate_bound)
        return [
            candidate
            for candidate in range(int(seed_q0) + 1, upper + 1)
            if is_visible_open(int(p), candidate)
        ]
    if domain == "visible_open_seed_bound":
        upper = int(seed_q0) + int(candidate_bound)
        return [
            candidate
            for candidate in range(int(seed_q0) + 1, upper + 1)
            if is_visible_open(int(p), candidate)
        ]
    raise ValueError(f"unknown candidate domain: {domain}")


def is_visible_open(p: int, n: int) -> bool:
    """Return whether n is wheel-open and not visibly closed."""
    return (
        int(n) % 30 in WHEEL_OPEN_RESIDUES_MOD30
        and closure_reason(int(p), int(n) - int(p), DEFAULT_VISIBLE_DIVISOR_BOUND)
        is None
    )


def hamming(left: list[int], right: list[int]) -> int:
    """Return Hamming distance between equal-length vectors."""
    if len(left) != len(right):
        raise ValueError("vectors must have equal length")
    return sum(1 for a, b in zip(left, right) if a != b)


def rst_pick(
    p: int,
    seed_q0: int,
    cache: dict[int, int],
    vector_mode: str,
    candidate_domain: str,
    vector_length: int,
    candidate_bound: int,
    visible_divisor_bound: int,
) -> dict[str, object]:
    """Return the first minimum-CSR candidate for one row and mode."""
    anchor = pre_shadow_vector(
        vector_mode,
        cache,
        int(p),
        int(seed_q0),
        int(vector_length),
    )
    candidates = candidate_window(
        candidate_domain,
        int(p),
        int(seed_q0),
        int(candidate_bound),
    )
    if not anchor or not candidates:
        return {
            "selected_q": None,
            "selected_csr": None,
            "min_tie_count": 0,
            "candidate_count": len(candidates),
            "vector_length_used": len(anchor),
        }

    scores: list[tuple[int, int]] = []
    width = len(anchor)
    for candidate in candidates:
        window = closure_vector(
            cache,
            int(candidate) - width,
            int(candidate),
        )
        scores.append((hamming(anchor, window), int(candidate)))
    min_score = min(score for score, _candidate in scores)
    min_candidates = [candidate for score, candidate in scores if score == min_score]
    return {
        "selected_q": min(min_candidates),
        "selected_csr": min_score,
        "min_tie_count": len(min_candidates),
        "candidate_count": len(candidates),
        "vector_length_used": width,
    }


def failure_mode(selected_q: int | None, true_q: int) -> str:
    """Classify one selected candidate."""
    if selected_q is None:
        return "no_selection"
    if int(selected_q) == int(true_q):
        return "correct"
    if int(selected_q) < int(true_q):
        return "selected_too_early"
    return "selected_too_late"


def build_selection_rows(
    source_rows: list[dict[str, object]],
    scales: set[int],
    vector_length: int,
    candidate_bound: int,
    visible_divisor_bound: int,
) -> list[dict[str, object]]:
    """Build one selected row per mode/domain/shadow row."""
    vector_modes = ["fixed_128_pre_shadow", "anchor_prefix_to_seed"]
    candidate_domains = [
        "all_integer_anchor_bound",
        "visible_open_anchor_bound",
        "all_integer_seed_bound",
        "visible_open_seed_bound",
    ]
    out: list[dict[str, object]] = []
    for row in source_rows:
        if row.get("source") != "shadow_seed_recovery":
            continue
        scale = int(row["scale"])
        if scale not in scales:
            continue
        p = int(row["p"])
        seed_q0 = int(row["chain_seed"])
        true_q = int(row["q"])
        cache_lo = min(
            p + 1,
            seed_q0 - int(vector_length),
            seed_q0 + 1 - int(vector_length),
        )
        cache_hi = max(
            p + int(candidate_bound),
            seed_q0 + int(candidate_bound),
        ) + 1
        cache = closure_state_map(
            p,
            cache_lo,
            cache_hi,
            int(visible_divisor_bound),
        )
        for vector_mode in vector_modes:
            for candidate_domain in candidate_domains:
                pick = rst_pick(
                    p,
                    seed_q0,
                    cache,
                    vector_mode,
                    candidate_domain,
                    int(vector_length),
                    int(candidate_bound),
                    int(visible_divisor_bound),
                )
                selected_q = pick["selected_q"]
                out.append(
                    {
                        "scale": scale,
                        "vector_mode": vector_mode,
                        "candidate_domain": candidate_domain,
                        "anchor_p": p,
                        "seed_q0": seed_q0,
                        "true_q_for_audit_only": true_q,
                        "selected_q": "" if selected_q is None else selected_q,
                        "selected_delta_from_true": ""
                        if selected_q is None
                        else int(selected_q) - true_q,
                        "selected_csr": ""
                        if pick["selected_csr"] is None
                        else pick["selected_csr"],
                        "min_tie_count": pick["min_tie_count"],
                        "candidate_count": pick["candidate_count"],
                        "vector_length_used": pick["vector_length_used"],
                        "failure_mode": failure_mode(
                            None if selected_q is None else int(selected_q),
                            true_q,
                        ),
                    }
                )
    return out


def rate(count: int, total: int) -> float:
    """Return count / total."""
    return 0.0 if int(total) == 0 else int(count) / int(total)


def summarize(
    source_rows: list[dict[str, object]],
    selection_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Summarize RST outcomes by scale and mode/domain."""
    emitted_by_scale: dict[int, int] = {}
    base_pgs_by_scale: dict[int, int] = {}
    for row in source_rows:
        scale = int(row["scale"])
        if row.get("q") is not None:
            emitted_by_scale[scale] = emitted_by_scale.get(scale, 0) + 1
        if row.get("source") == PGS_SOURCE:
            base_pgs_by_scale[scale] = base_pgs_by_scale.get(scale, 0) + 1

    groups: dict[tuple[int, str, str], list[dict[str, object]]] = {}
    for row in selection_rows:
        key = (
            int(row["scale"]),
            str(row["vector_mode"]),
            str(row["candidate_domain"]),
        )
        groups.setdefault(key, []).append(row)

    out: list[dict[str, object]] = []
    for (scale, vector_mode, candidate_domain), rows in sorted(groups.items()):
        correct = sum(1 for row in rows if row["failure_mode"] == "correct")
        no_selection = sum(1 for row in rows if row["failure_mode"] == "no_selection")
        too_early = sum(1 for row in rows if row["failure_mode"] == "selected_too_early")
        too_late = sum(1 for row in rows if row["failure_mode"] == "selected_too_late")
        audit_failed = len(rows) - correct - no_selection
        emitted = emitted_by_scale.get(scale, 0)
        projected_pgs = base_pgs_by_scale.get(scale, 0) + correct
        out.append(
            {
                "scale": scale,
                "vector_mode": vector_mode,
                "candidate_domain": candidate_domain,
                "shadow_seed_rows": len(rows),
                "correct": correct,
                "correct_percent": rate(correct, len(rows)) * 100.0,
                "no_selection": no_selection,
                "selected_too_early": too_early,
                "selected_too_late": too_late,
                "audit_failed_if_promoted": audit_failed,
                "emitted_count": emitted,
                "projected_pgs_count": projected_pgs,
                "projected_pgs_percent": rate(projected_pgs, emitted) * 100.0,
                "promotion_eligible": (
                    no_selection == 0
                    and audit_failed == 0
                    and emitted > 0
                    and rate(projected_pgs, emitted) >= 0.50
                ),
            }
        )
    return out


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Test Residual Symmetry Termination on shadow rows."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--scales", type=int, nargs="+", default=DEFAULT_SCALES)
    parser.add_argument("--vector-length", type=int, default=128)
    parser.add_argument("--candidate-bound", type=int, default=DEFAULT_CANDIDATE_BOUND)
    parser.add_argument(
        "--visible-divisor-bound",
        type=int,
        default=DEFAULT_VISIBLE_DIVISOR_BOUND,
    )
    return parser.parse_args()


def main() -> int:
    """Run the RST probe."""
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    source_rows = read_jsonl(args.input)
    selection_rows = build_selection_rows(
        source_rows,
        set(int(scale) for scale in args.scales),
        int(args.vector_length),
        int(args.candidate_bound),
        int(args.visible_divisor_bound),
    )
    summary_rows = summarize(source_rows, selection_rows)
    payload = {
        "solution_id": "gemini_solution_02_residual_symmetry_termination",
        "generator_changed": False,
        "vector_length": int(args.vector_length),
        "candidate_bound": int(args.candidate_bound),
        "visible_divisor_bound": int(args.visible_divisor_bound),
        "scales": [int(scale) for scale in args.scales],
        "selection_rows": len(selection_rows),
        "summary_rows": summary_rows,
        "promotion_eligible": any(
            bool(row["promotion_eligible"]) for row in summary_rows
        ),
        "verdict": "candidate_found"
        if any(bool(row["promotion_eligible"]) for row in summary_rows)
        else "rejected",
        "reason": (
            "RST did not select the terminal boundary with zero failures on "
            "the tested high-scale shadow rows."
        ),
    }
    write_csv(selection_rows, args.output_dir / "rst_selection_rows.csv")
    write_csv(summary_rows, args.output_dir / "rst_summary.csv")
    write_json(payload, args.output_dir / "summary.json")
    print(
        "rst selection_rows={rows} promotion_eligible={eligible}".format(
            rows=len(selection_rows),
            eligible=str(payload["promotion_eligible"]).lower(),
        )
    )
    for row in summary_rows:
        print(
            "scale={scale} vector={vector_mode} domain={candidate_domain} "
            "correct={correct}/{shadow_seed_rows} audit_failed_if_promoted="
            "{audit_failed_if_promoted} projected_pgs_percent="
            "{projected_pgs_percent:.2f}% promotion_eligible="
            "{promotion_eligible}".format(**row)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
