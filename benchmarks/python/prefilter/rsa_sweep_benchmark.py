#!/usr/bin/env python3
"""Deterministic RSA key-generation benchmark sweep up to a fixed maximum size."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[3]
MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import rsa_keygen_benchmark as rsa_benchmark


DEFAULT_MAX_RSA_BITS = 4096
DEFAULT_NAMESPACE = "cdl-rsa-keygen-sweep"
DEFAULT_RSA_SWEEP_SCHEDULE: tuple[tuple[int, int], ...] = (
    (512, 100),
    (1024, 100),
    (2048, 50),
    (3072, 20),
    (4096, 10),
)


def build_rsa_sweep_schedule(max_rsa_bits: int) -> list[tuple[int, int]]:
    """Return the fixed deterministic sweep schedule up to the requested RSA size."""
    if max_rsa_bits < DEFAULT_RSA_SWEEP_SCHEDULE[0][0]:
        raise ValueError(
            f"max_rsa_bits must be at least {DEFAULT_RSA_SWEEP_SCHEDULE[0][0]}"
        )

    schedule = [
        (rsa_bits, keypair_count)
        for rsa_bits, keypair_count in DEFAULT_RSA_SWEEP_SCHEDULE
        if rsa_bits <= max_rsa_bits
    ]
    if not schedule:
        raise ValueError("RSA sweep schedule is empty")
    return schedule


def run_rsa_sweep(
    schedule: Sequence[tuple[int, int]],
    public_exponent: int,
    namespace: str,
) -> list[Dict]:
    """Run the deterministic RSA key-generation benchmark on each scheduled size."""
    results: list[Dict] = []
    for rsa_bits, keypair_count in schedule:
        result = rsa_benchmark.run_rsa_keygen_benchmark(
            rsa_bits=rsa_bits,
            keypair_count=keypair_count,
            public_exponent=public_exponent,
            mr_bases=rsa_benchmark.benchmark.DEFAULT_MR_BASES,
            namespace=f"{namespace}:{rsa_bits}",
        )
        results.append(result)
    return results


def build_markdown_report(
    schedule: Sequence[tuple[int, int]],
    sweep_results: Sequence[Dict],
    public_exponent: int,
) -> str:
    """Build a concise markdown report for the RSA sweep."""
    lines = [
        "# RSA Sweep Benchmark Report",
        "",
        "This report benchmarks the deterministic RSA key-generation pipeline across",
        "the fixed sweep schedule up to the requested RSA ceiling.",
        "",
        "## Configuration",
        "",
        f"- `public_exponent`: {public_exponent}",
        f"- `rsa_sizes`: {[rsa_bits for rsa_bits, _ in schedule]}",
        f"- `keypair_counts`: {[keypair_count for _, keypair_count in schedule]}",
        "",
        "## Sweep Summary",
        "",
        "| RSA bits | Keypairs | Baseline total (ms) | Accelerated total (ms) | Speedup | Proxy rejection rate | Saved MR call rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for result in sweep_results:
        baseline = result["baseline"]
        accelerated = result["accelerated"]
        lines.append(
            f"| {result['rsa_bits']} | {result['keypair_count']} | "
            f"{baseline['total_wall_time_ms']:.6f} | "
            f"{accelerated['total_wall_time_ms']:.6f} | "
            f"{result['speedup']:.6f}x | "
            f"{accelerated['proxy_rejection_rate']:.6%} | "
            f"{result['saved_miller_rabin_call_rate']:.6%} |"
        )

    for result in sweep_results:
        baseline = result["baseline"]
        accelerated = result["accelerated"]
        fixed_points = result["prime_fixed_points"]
        lines.extend(
            [
                "",
                f"## RSA {result['rsa_bits']}",
                "",
                f"- Baseline generated `{result['keypair_count']}` deterministic keypairs in `{baseline['total_wall_time_ms']:.6f}` ms total.",
                f"- The accelerated path generated the same keypairs in `{accelerated['total_wall_time_ms']:.6f}` ms for a measured `{result['speedup']:.2f}x` speedup.",
                f"- The proxy removed `{result['saved_miller_rabin_calls']}` Miller-Rabin calls (`{result['saved_miller_rabin_call_rate']:.2%}` of baseline MR work).",
                f"- Proxy rejection rate was `{accelerated['proxy_rejection_rate']:.2%}` across the full candidate stream.",
                f"- All `{fixed_points['fixed_point_count']}` confirmed primes remained on the Divisor Normalization Identity (DNI) `Z(n) = n^(1 - d(n)/2)` band `Z = 1.0` after final `sympy.isprime` confirmation.",
            ]
        )

    return "\n".join(lines) + "\n"


def run_rsa_sweep_benchmark(
    output_dir: Path,
    max_rsa_bits: int,
    public_exponent: int,
    namespace: str,
) -> Dict:
    """Run the full deterministic RSA sweep and write JSON/Markdown artifacts."""
    schedule = build_rsa_sweep_schedule(max_rsa_bits)
    sweep_results = run_rsa_sweep(
        schedule=schedule,
        public_exponent=public_exponent,
        namespace=namespace,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schedule": [
            {"rsa_bits": rsa_bits, "keypair_count": keypair_count}
            for rsa_bits, keypair_count in schedule
        ],
        "public_exponent": public_exponent,
        "results": sweep_results,
    }
    json_path = output_dir / "rsa_sweep_results.json"
    markdown_path = output_dir / "RSA_SWEEP_REPORT.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(
        build_markdown_report(schedule, sweep_results, public_exponent),
        encoding="utf-8",
    )
    return payload


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Deterministic RSA key-generation benchmark sweep."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "benchmarks" / "output" / "python" / "prefilter" / "rsa_sweep",
        help="Directory for JSON and Markdown artifacts.",
    )
    parser.add_argument(
        "--max-rsa-bits",
        type=int,
        default=DEFAULT_MAX_RSA_BITS,
        help=f"Maximum RSA modulus size to include in the sweep (default: {DEFAULT_MAX_RSA_BITS}).",
    )
    parser.add_argument(
        "--public-exponent",
        type=int,
        default=rsa_benchmark.DEFAULT_PUBLIC_EXPONENT,
        help=(
            "RSA public exponent used for every benchmark cell "
            f"(default: {rsa_benchmark.DEFAULT_PUBLIC_EXPONENT})."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    """Run the RSA sweep benchmark and print a compact summary."""
    args = parse_args(argv)
    payload = run_rsa_sweep_benchmark(
        output_dir=args.output_dir,
        max_rsa_bits=args.max_rsa_bits,
        public_exponent=args.public_exponent,
        namespace=DEFAULT_NAMESPACE,
    )
    sizes = [entry["rsa_bits"] for entry in payload["schedule"]]
    print("rsa sweep benchmark complete")
    print("rsa sizes:", sizes)
    for result in payload["results"]:
        print(
            f"rsa {result['rsa_bits']}:",
            f"{result['keypair_count']} keypairs,",
            f"{result['speedup']:.2f}x speedup,",
            f"{result['accelerated']['proxy_rejection_rate']:.2%} proxy rejection,",
            f"{result['saved_miller_rabin_call_rate']:.2%} saved MR calls",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
