"""Audit-feasible high-scale probe for the PGS shadow-chain bridge."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from sympy import factorint, isprime, prevprime


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "src" / "python"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from z_band_prime_predictor.simple_pgs_controller import (  # noqa: E402
    write_json,
    write_jsonl,
)
from z_band_prime_predictor.simple_pgs_generator import (  # noqa: E402
    CHAIN_FALLBACK_SOURCE,
    DEFAULT_CHAIN_LIMIT,
    DEFAULT_VISIBLE_DIVISOR_BOUND,
    FALLBACK_SOURCE,
    PGS_SOURCE,
    pgs_probe_certificate,
    visible_open_chain_offsets,
)


def sampled_anchors_near(scale: int, sample_size: int) -> list[int]:
    """Return deterministic prime anchors immediately below scale."""
    anchors: list[int] = []
    cursor = int(scale)
    while len(anchors) < int(sample_size):
        anchor = int(prevprime(cursor))
        anchors.append(anchor)
        cursor = anchor
    return anchors


def audit_confirms_next_prime(p: int, q: int) -> bool:
    """Return True when downstream audit confirms q is next after p."""
    if int(q) <= int(p) or not bool(isprime(int(q))):
        return False
    return not any(isprime(candidate) for candidate in range(int(p) + 1, int(q)))


def factorization_accepts_candidate(n: int) -> bool:
    """Return True when deterministic factorization finds no nontrivial factor."""
    factors = {int(prime): int(exp) for prime, exp in factorint(int(n)).items()}
    return len(factors) == 1 and factors.get(int(n)) == 1


def chain_candidates(
    p: int,
    seed_q: int,
    candidate_bound: int,
    chain_limit: int,
    visible_divisor_bound: int,
) -> list[int]:
    """Return visible-open chain candidates after one seed."""
    seed_offset = int(seed_q) - int(p)
    return [
        int(p) + offset
        for offset in visible_open_chain_offsets(
            int(p),
            seed_offset,
            int(candidate_bound),
            int(chain_limit),
            int(visible_divisor_bound),
        )
    ]


def probe_anchor(
    p: int,
    candidate_bound: int,
    chain_limit: int,
    visible_divisor_bound: int,
) -> dict[str, object]:
    """Return one probe row with full fallback disabled."""
    certificate = pgs_probe_certificate(
        int(p),
        int(candidate_bound),
        int(visible_divisor_bound),
    )
    if certificate is None:
        return {
            "p": int(p),
            "q": None,
            "source": "unresolved",
            "audit_passed": False,
            "chain_seed": None,
            "chain_position_selected": None,
            "chain_nodes_checked": [],
            "unresolved_reason": "no_pgs_certificate",
        }

    q0 = int(certificate["q"])
    if factorization_accepts_candidate(q0):
        return {
            "p": int(p),
            "q": q0,
            "source": PGS_SOURCE,
            "audit_passed": audit_confirms_next_prime(int(p), q0),
            "chain_seed": None,
            "chain_position_selected": None,
            "chain_nodes_checked": [],
            "unresolved_reason": None,
        }

    nodes = chain_candidates(
        int(p),
        q0,
        int(candidate_bound),
        int(chain_limit),
        int(visible_divisor_bound),
    )
    checked: list[int] = []
    for position, candidate in enumerate(nodes, start=1):
        checked.append(candidate)
        if factorization_accepts_candidate(candidate):
            return {
                "p": int(p),
                "q": candidate,
                "source": CHAIN_FALLBACK_SOURCE,
                "audit_passed": audit_confirms_next_prime(int(p), candidate),
                "chain_seed": q0,
                "chain_position_selected": position,
                "chain_nodes_checked": checked,
                "unresolved_reason": None,
            }

    return {
        "p": int(p),
        "q": None,
        "source": "unresolved",
        "audit_passed": False,
        "chain_seed": q0,
        "chain_position_selected": None,
        "chain_nodes_checked": checked,
        "unresolved_reason": "chain_exhausted_full_fallback_disabled",
    }


def rate(count: int, total: int) -> float:
    """Return count / total."""
    return 0.0 if int(total) == 0 else int(count) / int(total)


def scale_summary(
    scale: int,
    rows: list[dict[str, object]],
    sample_size: int,
) -> dict[str, object]:
    """Return the requested high-scale probe summary."""
    emitted = [row for row in rows if row["q"] is not None]
    pgs_count = sum(1 for row in emitted if row["source"] == PGS_SOURCE)
    chain_count = sum(
        1 for row in emitted if row["source"] == CHAIN_FALLBACK_SOURCE
    )
    fallback_count = sum(1 for row in emitted if row["source"] == FALLBACK_SOURCE)
    unresolved_count = int(sample_size) - len(emitted)
    audit_failed = sum(1 for row in emitted if not bool(row["audit_passed"]))
    emitted_count = len(emitted)
    return {
        "scale": int(scale),
        "sample_size": int(sample_size),
        "emitted_count": emitted_count,
        "unresolved_count": unresolved_count,
        "unresolved_rate": rate(unresolved_count, sample_size),
        "unresolved_percent": rate(unresolved_count, sample_size) * 100.0,
        "audit_failed": audit_failed,
        "accuracy_status": "PASS" if audit_failed == 0 else "FAIL",
        "pgs_status": "MINIMAL_PASS"
        if audit_failed == 0 and emitted_count and rate(pgs_count, emitted_count) >= 0.50
        else "FAILING",
        "pgs_count": pgs_count,
        "chain_fallback_count": chain_count,
        "fallback_count": fallback_count,
        "pgs_rate": rate(pgs_count, emitted_count),
        "chain_fallback_rate": rate(chain_count, emitted_count),
        "fallback_rate": rate(fallback_count, emitted_count),
        "pgs_percent": rate(pgs_count, emitted_count) * 100.0,
        "chain_fallback_percent": rate(chain_count, emitted_count) * 100.0,
        "fallback_percent": rate(fallback_count, emitted_count) * 100.0,
    }


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


def run_probe(
    scales: list[int],
    sample_size: int,
    candidate_bound: int,
    chain_limit: int,
    visible_divisor_bound: int,
    output_dir: Path,
) -> list[dict[str, object]]:
    """Run the audit-feasible high-scale probe."""
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, object]] = []
    all_rows: list[dict[str, object]] = []
    for scale in scales:
        rows = [
            {
                "scale": int(scale),
                **probe_anchor(
                    anchor,
                    candidate_bound,
                    chain_limit,
                    visible_divisor_bound,
                ),
            }
            for anchor in sampled_anchors_near(scale, sample_size)
        ]
        all_rows.extend(rows)
        summaries.append(scale_summary(scale, rows, sample_size))
    write_jsonl(all_rows, output_dir / "rows.jsonl")
    write_csv(summaries, output_dir / "summary.csv")
    write_json({"rows": summaries}, output_dir / "summary.json")
    return summaries


def build_parser() -> argparse.ArgumentParser:
    """Build the high-scale chain probe CLI."""
    parser = argparse.ArgumentParser(
        description="Run high-scale PGS chain bridge probe with full fallback disabled."
    )
    parser.add_argument("--anchors", type=int, nargs="+", required=True)
    parser.add_argument("--sample-size", type=int, required=True)
    parser.add_argument("--candidate-bound", type=int, default=128)
    parser.add_argument("--chain-limit", type=int, default=DEFAULT_CHAIN_LIMIT)
    parser.add_argument(
        "--visible-divisor-bound",
        type=int,
        default=DEFAULT_VISIBLE_DIVISOR_BOUND,
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the high-scale chain probe."""
    args = build_parser().parse_args(argv)
    summaries = run_probe(
        [int(scale) for scale in args.anchors],
        int(args.sample_size),
        int(args.candidate_bound),
        int(args.chain_limit),
        int(args.visible_divisor_bound),
        args.output_dir,
    )
    for row in summaries:
        print(
            "scale={scale} emitted={emitted_count} unresolved={unresolved_count} "
            "audit_failed={audit_failed} pgs_percent={pgs_percent:.2f}% "
            "chain_fallback_percent={chain_fallback_percent:.2f}% "
            "fallback_percent={fallback_percent:.2f}% "
            "accuracy_status={accuracy_status} pgs_status={pgs_status}".format(**row)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
