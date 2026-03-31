#!/usr/bin/env python3
"""Deterministic end-to-end RSA key generation benchmark."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Sequence

from sympy import isprime


ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import candidate_benchmark as benchmark


DEFAULT_RSA_BITS = 2048
DEFAULT_RSA_KEYPAIR_COUNT = 300
DEFAULT_BONUS_RSA_BITS = 4096
DEFAULT_BONUS_RSA_KEYPAIR_COUNT = 50
DEFAULT_PUBLIC_EXPONENT = 65537
DEFAULT_NAMESPACE = "cdl-rsa-keygen"
RSA_VALIDATION_MESSAGE = 42


def validate_rsa_inputs(rsa_bits: int, public_exponent: int) -> None:
    """Require an even RSA modulus size and a usable odd public exponent."""
    if rsa_bits < 4 or rsa_bits % 2 != 0:
        raise ValueError("rsa_bits must be an even integer greater than or equal to 4")
    if public_exponent <= 1 or public_exponent % 2 == 0:
        raise ValueError("public_exponent must be an odd integer greater than 1")


def deterministic_candidate_stream(bit_length: int, namespace: str) -> Iterator[int]:
    """Yield a deterministic, duplicate-free odd candidate stream."""
    seen = set()
    index = 0
    while True:
        candidate = benchmark.deterministic_odd_candidate(
            bit_length,
            index,
            namespace=namespace,
        )
        index += 1
        if candidate in seen:
            continue
        seen.add(candidate)
        yield candidate


def build_proxy_tables(
    prime_bits: int,
) -> tuple[
    benchmark.WheelPrimeTable,
    benchmark.WheelPrimeTable,
    benchmark.WheelPrimeTable | None,
]:
    """Build the deterministic prime tables used by the accelerated path."""
    primary = benchmark.WheelPrimeTable(
        benchmark.DEFAULT_PROXY_TRIAL_PRIME_LIMIT,
        benchmark.DEFAULT_PROXY_CHUNK_SIZE,
    )
    tail = benchmark.WheelPrimeTable(
        benchmark.DEFAULT_PROXY_TAIL_PRIME_LIMIT,
        benchmark.DEFAULT_PROXY_TAIL_CHUNK_SIZE,
        start_exclusive=benchmark.DEFAULT_PROXY_TRIAL_PRIME_LIMIT,
    )
    deep_tail = None
    if prime_bits >= benchmark.DEFAULT_PROXY_DEEP_TAIL_MIN_BITS:
        deep_tail = benchmark.WheelPrimeTable(
            benchmark.DEFAULT_PROXY_DEEP_TAIL_PRIME_LIMIT,
            benchmark.DEFAULT_PROXY_DEEP_TAIL_CHUNK_SIZE,
            start_exclusive=benchmark.DEFAULT_PROXY_TAIL_PRIME_LIMIT,
        )
    return primary, tail, deep_tail


def find_rsa_prime(
    prime_bits: int,
    namespace: str,
    public_exponent: int,
    mr_bases: Sequence[int],
    use_proxy: bool,
    prime_table: benchmark.WheelPrimeTable | None = None,
    tail_prime_table: benchmark.WheelPrimeTable | None = None,
    deep_tail_prime_table: benchmark.WheelPrimeTable | None = None,
    deep_tail_min_bits: int | None = None,
    excluded_values: set[int] | None = None,
) -> tuple[int, Dict[str, int]]:
    """Find one RSA prime on a deterministic candidate stream."""
    stats = {
        "candidates_tested": 0,
        "proxy_rejections": 0,
        "miller_rabin_calls": 0,
        "proxy_time_ns": 0,
        "miller_rabin_time_ns": 0,
    }
    excluded = excluded_values or set()

    for candidate in deterministic_candidate_stream(prime_bits, namespace):
        stats["candidates_tested"] += 1

        if use_proxy:
            if prime_table is None:
                raise ValueError("prime_table is required when use_proxy is True")
            start_ns = time.perf_counter_ns()
            proxy = benchmark.cheap_cdl_proxy(
                candidate,
                prime_table,
                tail_prime_table=tail_prime_table,
                deep_tail_prime_table=deep_tail_prime_table,
                deep_tail_min_bits=deep_tail_min_bits,
            )
            stats["proxy_time_ns"] += time.perf_counter_ns() - start_ns
            if bool(proxy["rejected"]):
                stats["proxy_rejections"] += 1
                continue

        stats["miller_rabin_calls"] += 1
        start_ns = time.perf_counter_ns()
        mr_passed = benchmark.miller_rabin_fixed_bases(candidate, mr_bases)
        stats["miller_rabin_time_ns"] += time.perf_counter_ns() - start_ns
        if not mr_passed:
            continue
        if math.gcd(candidate - 1, public_exponent) != 1:
            continue
        if candidate in excluded:
            continue

        return candidate, stats

    raise RuntimeError("deterministic candidate stream exhausted unexpectedly")


def generate_rsa_keypair(
    rsa_bits: int,
    keypair_index: int,
    public_exponent: int,
    mr_bases: Sequence[int],
    namespace: str,
    use_proxy: bool,
    prime_table: benchmark.WheelPrimeTable | None = None,
    tail_prime_table: benchmark.WheelPrimeTable | None = None,
    deep_tail_prime_table: benchmark.WheelPrimeTable | None = None,
    deep_tail_min_bits: int | None = None,
) -> Dict[str, int]:
    """Generate one deterministic RSA keypair and its search statistics."""
    validate_rsa_inputs(rsa_bits, public_exponent)
    total_start_ns = time.perf_counter_ns()
    prime_bits = rsa_bits // 2
    p_namespace = f"{namespace}:{rsa_bits}:{keypair_index}:p"
    q_namespace = f"{namespace}:{rsa_bits}:{keypair_index}:q"

    p, p_stats = find_rsa_prime(
        prime_bits,
        p_namespace,
        public_exponent,
        mr_bases,
        use_proxy,
        prime_table=prime_table,
        tail_prime_table=tail_prime_table,
        deep_tail_prime_table=deep_tail_prime_table,
        deep_tail_min_bits=deep_tail_min_bits,
    )
    q, q_stats = find_rsa_prime(
        prime_bits,
        q_namespace,
        public_exponent,
        mr_bases,
        use_proxy,
        prime_table=prime_table,
        tail_prime_table=tail_prime_table,
        deep_tail_prime_table=deep_tail_prime_table,
        deep_tail_min_bits=deep_tail_min_bits,
        excluded_values={p},
    )

    assembly_start_ns = time.perf_counter_ns()
    phi = (p - 1) * (q - 1)
    d = pow(public_exponent, -1, phi)
    n = p * q
    if pow(pow(RSA_VALIDATION_MESSAGE, public_exponent, n), d, n) != RSA_VALIDATION_MESSAGE:
        raise ValueError("RSA round-trip validation failed")
    assembly_time_ns = time.perf_counter_ns() - assembly_start_ns

    return {
        "p": p,
        "q": q,
        "n": n,
        "d": d,
        "candidates_tested": p_stats["candidates_tested"] + q_stats["candidates_tested"],
        "proxy_rejections": p_stats["proxy_rejections"] + q_stats["proxy_rejections"],
        "miller_rabin_calls": p_stats["miller_rabin_calls"] + q_stats["miller_rabin_calls"],
        "proxy_time_ns": p_stats["proxy_time_ns"] + q_stats["proxy_time_ns"],
        "miller_rabin_time_ns": (
            p_stats["miller_rabin_time_ns"] + q_stats["miller_rabin_time_ns"]
        ),
        "assembly_time_ns": assembly_time_ns,
        "total_time_ns": time.perf_counter_ns() - total_start_ns,
    }


def summarize_keygen_path(
    rsa_bits: int,
    keypair_count: int,
    public_exponent: int,
    mr_bases: Sequence[int],
    namespace: str,
    use_proxy: bool,
    prime_table: benchmark.WheelPrimeTable | None = None,
    tail_prime_table: benchmark.WheelPrimeTable | None = None,
    deep_tail_prime_table: benchmark.WheelPrimeTable | None = None,
    deep_tail_min_bits: int | None = None,
) -> tuple[Dict, List[Dict[str, int]]]:
    """Run one deterministic RSA key generation path and summarize it."""
    keypairs: List[Dict[str, int]] = []
    candidates_per_keypair: List[int] = []
    mr_calls_per_keypair: List[int] = []
    proxy_rejections_per_keypair: List[int] = []
    proxy_time_per_keypair_ns: List[int] = []
    mr_time_per_keypair_ns: List[int] = []
    assembly_time_per_keypair_ns: List[int] = []

    start_ns = time.perf_counter_ns()
    for keypair_index in range(keypair_count):
        keypair = generate_rsa_keypair(
            rsa_bits,
            keypair_index,
            public_exponent,
            mr_bases,
            namespace=namespace,
            use_proxy=use_proxy,
            prime_table=prime_table,
            tail_prime_table=tail_prime_table,
            deep_tail_prime_table=deep_tail_prime_table,
            deep_tail_min_bits=deep_tail_min_bits,
        )
        keypairs.append(keypair)
        candidates_per_keypair.append(keypair["candidates_tested"])
        mr_calls_per_keypair.append(keypair["miller_rabin_calls"])
        proxy_rejections_per_keypair.append(keypair["proxy_rejections"])
        proxy_time_per_keypair_ns.append(keypair["proxy_time_ns"])
        mr_time_per_keypair_ns.append(keypair["miller_rabin_time_ns"])
        assembly_time_per_keypair_ns.append(keypair["assembly_time_ns"])
    total_wall_time_ns = time.perf_counter_ns() - start_ns

    total_candidates_tested = sum(candidates_per_keypair)
    total_miller_rabin_calls = sum(mr_calls_per_keypair)
    total_proxy_rejections = sum(proxy_rejections_per_keypair)
    total_proxy_time_ns = sum(proxy_time_per_keypair_ns)
    total_miller_rabin_time_ns = sum(mr_time_per_keypair_ns)
    total_assembly_time_ns = sum(assembly_time_per_keypair_ns)
    residual_time_ns = (
        total_wall_time_ns
        - total_proxy_time_ns
        - total_miller_rabin_time_ns
        - total_assembly_time_ns
    )
    total_seconds = total_wall_time_ns / 1_000_000_000.0

    if residual_time_ns < 0:
        raise ValueError("timing bucket residual fell below zero")

    return (
        {
            "rsa_bits": rsa_bits,
            "prime_bits": rsa_bits // 2,
            "keypair_count": keypair_count,
            "public_exponent": public_exponent,
            "path": (
                "gated_proxy_then_miller_rabin"
                if use_proxy
                else "miller_rabin_only"
            ),
            "total_wall_time_ms": total_wall_time_ns / 1_000_000.0,
            "keypairs_per_second": keypair_count / total_seconds if total_seconds else 0.0,
            "mean_time_per_keypair_ms": (total_wall_time_ns / keypair_count) / 1_000_000.0,
            "total_candidates_tested": total_candidates_tested,
            "total_miller_rabin_calls": total_miller_rabin_calls,
            "total_proxy_rejections": total_proxy_rejections,
            "proxy_rejection_rate": (
                total_proxy_rejections / total_candidates_tested
                if total_candidates_tested
                else 0.0
            ),
            "mean_candidates_per_prime": total_candidates_tested / (2.0 * keypair_count),
            "mean_miller_rabin_calls_per_prime": total_miller_rabin_calls / (2.0 * keypair_count),
            "total_proxy_time_ms": total_proxy_time_ns / 1_000_000.0,
            "total_miller_rabin_time_ms": total_miller_rabin_time_ns / 1_000_000.0,
            "total_assembly_time_ms": total_assembly_time_ns / 1_000_000.0,
            "total_residual_time_ms": residual_time_ns / 1_000_000.0,
            "proxy_time_share": total_proxy_time_ns / total_wall_time_ns if total_wall_time_ns else 0.0,
            "miller_rabin_time_share": (
                total_miller_rabin_time_ns / total_wall_time_ns if total_wall_time_ns else 0.0
            ),
            "assembly_time_share": (
                total_assembly_time_ns / total_wall_time_ns if total_wall_time_ns else 0.0
            ),
            "residual_time_share": residual_time_ns / total_wall_time_ns if total_wall_time_ns else 0.0,
            "mean_proxy_time_per_keypair_ms": (total_proxy_time_ns / keypair_count) / 1_000_000.0,
            "mean_miller_rabin_time_per_keypair_ms": (
                total_miller_rabin_time_ns / keypair_count
            ) / 1_000_000.0,
            "mean_assembly_time_per_keypair_ms": (
                total_assembly_time_ns / keypair_count
            ) / 1_000_000.0,
            "mean_residual_time_per_keypair_ms": (residual_time_ns / keypair_count) / 1_000_000.0,
            "candidate_preview": [benchmark.compact_hex(pair["n"]) for pair in keypairs[:3]],
            "mean_candidates_per_keypair": total_candidates_tested / keypair_count,
            "median_candidates_per_keypair": statistics.median(candidates_per_keypair),
            "max_candidates_per_keypair": max(candidates_per_keypair),
            "median_miller_rabin_calls_per_keypair": statistics.median(mr_calls_per_keypair),
            "max_miller_rabin_calls_per_keypair": max(mr_calls_per_keypair),
        },
        keypairs,
    )


def compare_keypair_sets(
    baseline_keypairs: Sequence[Dict[str, int]],
    accelerated_keypairs: Sequence[Dict[str, int]],
) -> None:
    """Require the baseline and accelerated paths to produce the same keypairs."""
    if len(baseline_keypairs) != len(accelerated_keypairs):
        raise ValueError("baseline and accelerated keypair counts do not match")

    for index, (baseline_pair, accelerated_pair) in enumerate(
        zip(baseline_keypairs, accelerated_keypairs)
    ):
        for field in ("p", "q", "n", "d"):
            if baseline_pair[field] != accelerated_pair[field]:
                raise ValueError(
                    f"keypair mismatch at index {index} for field {field}"
                )


def confirm_prime_fixed_points(keypairs: Sequence[Dict[str, int]]) -> Dict[str, object]:
    """
    Confirm the prime DCI band on final RSA primes via primality.

    Once a final keypair factor is confirmed prime, the Divisor Curvature Identity
    (DCI) `Z(n) = n^(1 - d(n)/2)` locks the invariant exactly at Z = 1.0.
    """
    confirmed_primes = 0
    for keypair in keypairs:
        for prime in (keypair["p"], keypair["q"]):
            if not isprime(prime):
                raise ValueError("final RSA factor failed sympy.isprime confirmation")
            confirmed_primes += 1

    return {
        "verification_mode": "sympy_isprime_then_closed_form_fixed_point",
        "confirmed_prime_count": confirmed_primes,
        "fixed_point_count": confirmed_primes,
        "fixed_point_value": 1.0,
    }


def run_rsa_keygen_benchmark(
    rsa_bits: int,
    keypair_count: int,
    public_exponent: int,
    mr_bases: Sequence[int],
    namespace: str,
) -> Dict:
    """Run baseline and accelerated RSA key generation on the same deterministic streams."""
    validate_rsa_inputs(rsa_bits, public_exponent)
    primary_table, tail_table, deep_tail_table = build_proxy_tables(rsa_bits // 2)
    baseline_summary, baseline_keypairs = summarize_keygen_path(
        rsa_bits,
        keypair_count,
        public_exponent,
        mr_bases,
        namespace=namespace,
        use_proxy=False,
    )
    accelerated_summary, accelerated_keypairs = summarize_keygen_path(
        rsa_bits,
        keypair_count,
        public_exponent,
        mr_bases,
        namespace=namespace,
        use_proxy=True,
        prime_table=primary_table,
        tail_prime_table=tail_table,
        deep_tail_prime_table=deep_tail_table,
        deep_tail_min_bits=benchmark.DEFAULT_PROXY_DEEP_TAIL_MIN_BITS,
    )
    compare_keypair_sets(baseline_keypairs, accelerated_keypairs)
    fixed_points = confirm_prime_fixed_points(accelerated_keypairs)

    baseline_mr_calls = baseline_summary["total_miller_rabin_calls"]
    accelerated_mr_calls = accelerated_summary["total_miller_rabin_calls"]
    saved_mr_calls = baseline_mr_calls - accelerated_mr_calls
    speedup = baseline_summary["total_wall_time_ms"] / accelerated_summary["total_wall_time_ms"]

    return {
        "rsa_bits": rsa_bits,
        "keypair_count": keypair_count,
        "public_exponent": public_exponent,
        "baseline": baseline_summary,
        "accelerated": accelerated_summary,
        "speedup": speedup,
        "saved_miller_rabin_calls": saved_mr_calls,
        "saved_miller_rabin_call_rate": saved_mr_calls / baseline_mr_calls if baseline_mr_calls else 0.0,
        "matching_keypairs": keypair_count,
        "prime_fixed_points": fixed_points,
    }


def build_rsa_report_section(title: str, results: Dict) -> List[str]:
    """Build one markdown section for an end-to-end RSA benchmark."""
    baseline = results["baseline"]
    accelerated = results["accelerated"]
    fixed_points = results["prime_fixed_points"]

    return [
        f"## {title}",
        "",
        f"- Baseline generated `{baseline['keypair_count']}` deterministic `{results['rsa_bits']}`-bit keypairs in `{baseline['total_wall_time_ms']:.6f}` ms total (`{baseline['keypairs_per_second']:.6f}` keypairs/s).",
        f"- The accelerated path generated the same `{baseline['keypair_count']}` keypairs in `{accelerated['total_wall_time_ms']:.6f}` ms total (`{accelerated['keypairs_per_second']:.6f}` keypairs/s) for a measured `{results['speedup']:.2f}x` speedup.",
        f"- The proxy removed `{results['saved_miller_rabin_calls']}` Miller-Rabin calls (`{results['saved_miller_rabin_call_rate']:.2%}` of baseline MR work) while preserving identical deterministic keypairs across both paths.",
        f"- Timing buckets in the accelerated path broke down into `{accelerated['total_proxy_time_ms']:.6f}` ms proxy filtering (`{accelerated['proxy_time_share']:.2%}`), `{accelerated['total_miller_rabin_time_ms']:.6f}` ms survivor Miller-Rabin (`{accelerated['miller_rabin_time_share']:.2%}`), `{accelerated['total_assembly_time_ms']:.6f}` ms RSA assembly/validation (`{accelerated['assembly_time_share']:.2%}`), and `{accelerated['total_residual_time_ms']:.6f}` ms residual search overhead (`{accelerated['residual_time_share']:.2%}`).",
        f"- Final keypair primes were confirmed by `sympy.isprime`; under the Divisor Curvature Identity (DCI) `Z(n) = n^(1 - d(n)/2)`, all `{fixed_points['fixed_point_count']}` confirmed factors remain exactly on the `Z = 1.0` fixed-point band.",
        "",
        "| Metric | Baseline | Accelerated |",
        "|---|---:|---:|",
        f"| Keypair count | {baseline['keypair_count']} | {accelerated['keypair_count']} |",
        f"| Total wall time (ms) | {baseline['total_wall_time_ms']:.6f} | {accelerated['total_wall_time_ms']:.6f} |",
        f"| Keypairs per second | {baseline['keypairs_per_second']:.6f} | {accelerated['keypairs_per_second']:.6f} |",
        f"| Mean time per keypair (ms) | {baseline['mean_time_per_keypair_ms']:.6f} | {accelerated['mean_time_per_keypair_ms']:.6f} |",
        f"| Mean candidates per prime | {baseline['mean_candidates_per_prime']:.6f} | {accelerated['mean_candidates_per_prime']:.6f} |",
        f"| Total candidates tested | {baseline['total_candidates_tested']} | {accelerated['total_candidates_tested']} |",
        f"| Total Miller-Rabin calls | {baseline['total_miller_rabin_calls']} | {accelerated['total_miller_rabin_calls']} |",
        f"| Total proxy rejections | 0 | {accelerated['total_proxy_rejections']} |",
        f"| Proxy rejection contribution | 0.000000% | {accelerated['proxy_rejection_rate']:.6%} |",
        f"| Saved Miller-Rabin call rate | 0.000000% | {results['saved_miller_rabin_call_rate']:.6%} |",
        f"| Proxy filtering time (ms) | {baseline['total_proxy_time_ms']:.6f} | {accelerated['total_proxy_time_ms']:.6f} |",
        f"| Survivor Miller-Rabin time (ms) | {baseline['total_miller_rabin_time_ms']:.6f} | {accelerated['total_miller_rabin_time_ms']:.6f} |",
        f"| RSA assembly + validation time (ms) | {baseline['total_assembly_time_ms']:.6f} | {accelerated['total_assembly_time_ms']:.6f} |",
        f"| Residual search overhead (ms) | {baseline['total_residual_time_ms']:.6f} | {accelerated['total_residual_time_ms']:.6f} |",
        f"| Proxy filtering share | {baseline['proxy_time_share']:.6%} | {accelerated['proxy_time_share']:.6%} |",
        f"| Survivor Miller-Rabin share | {baseline['miller_rabin_time_share']:.6%} | {accelerated['miller_rabin_time_share']:.6%} |",
        f"| RSA assembly + validation share | {baseline['assembly_time_share']:.6%} | {accelerated['assembly_time_share']:.6%} |",
        f"| Residual search overhead share | {baseline['residual_time_share']:.6%} | {accelerated['residual_time_share']:.6%} |",
        f"| Matching deterministic keypairs | {results['matching_keypairs']} | {results['matching_keypairs']} |",
        "",
    ]


def build_combined_report(results: Dict) -> str:
    """Build the candidate benchmark report with appended RSA sections."""
    lines = [benchmark.build_report_markdown(results).rstrip(), ""]
    lines.extend(build_rsa_report_section("End-to-End RSA Key Generation", results["rsa_keygen"]))
    lines.extend(
        build_rsa_report_section("4096-bit RSA Spot-Check", results["bonus_rsa_keygen"])
    )
    lines.extend(
        [
            "## RSA Reproduction",
            "",
            "Run the end-to-end RSA benchmark again with:",
            "",
            "```bash",
            results["rsa_reproduction_command"],
            "```",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def run_combined_benchmark(
    output_dir: Path,
    rsa_bits: int,
    rsa_keypair_count: int,
    bonus_rsa_bits: int,
    bonus_rsa_keypair_count: int,
    public_exponent: int,
) -> Dict:
    """Run the candidate benchmark and append end-to-end RSA key generation results."""
    results = benchmark.run_benchmark(
        output_dir=output_dir,
        exact_bits=benchmark.DEFAULT_EXACT_BITS,
        exact_count=benchmark.DEFAULT_EXACT_COUNT,
        crypto_bits=benchmark.DEFAULT_CRYPTO_BITS,
        crypto_count=benchmark.DEFAULT_CRYPTO_COUNT,
        bonus_crypto_bits=benchmark.DEFAULT_BONUS_CRYPTO_BITS,
        bonus_crypto_count=benchmark.DEFAULT_BONUS_CRYPTO_COUNT,
        proxy_trial_prime_limit=benchmark.DEFAULT_PROXY_TRIAL_PRIME_LIMIT,
        proxy_chunk_size=benchmark.DEFAULT_PROXY_CHUNK_SIZE,
        proxy_tail_prime_limit=benchmark.DEFAULT_PROXY_TAIL_PRIME_LIMIT,
        proxy_tail_chunk_size=benchmark.DEFAULT_PROXY_TAIL_CHUNK_SIZE,
        proxy_deep_tail_prime_limit=benchmark.DEFAULT_PROXY_DEEP_TAIL_PRIME_LIMIT,
        proxy_deep_tail_chunk_size=benchmark.DEFAULT_PROXY_DEEP_TAIL_CHUNK_SIZE,
        proxy_deep_tail_min_bits=benchmark.DEFAULT_PROXY_DEEP_TAIL_MIN_BITS,
        mr_bases=benchmark.DEFAULT_MR_BASES,
        truth_check=False,
    )
    results["rsa_keygen"] = run_rsa_keygen_benchmark(
        rsa_bits,
        rsa_keypair_count,
        public_exponent,
        benchmark.DEFAULT_MR_BASES,
        namespace=f"{DEFAULT_NAMESPACE}:main",
    )
    results["bonus_rsa_keygen"] = run_rsa_keygen_benchmark(
        bonus_rsa_bits,
        bonus_rsa_keypair_count,
        public_exponent,
        benchmark.DEFAULT_MR_BASES,
        namespace=f"{DEFAULT_NAMESPACE}:bonus",
    )
    results["rsa_configuration"] = {
        "rsa_bits": rsa_bits,
        "rsa_keypair_count": rsa_keypair_count,
        "bonus_rsa_bits": bonus_rsa_bits,
        "bonus_rsa_keypair_count": bonus_rsa_keypair_count,
        "public_exponent": public_exponent,
    }
    results["rsa_reproduction_command"] = (
        "python3 benchmarks/python/rsa_keygen_benchmark.py "
        f"--rsa-bits {rsa_bits} "
        f"--rsa-keypair-count {rsa_keypair_count} "
        f"--bonus-rsa-bits {bonus_rsa_bits} "
        f"--bonus-rsa-keypair-count {bonus_rsa_keypair_count} "
        f"--public-exponent {public_exponent}"
    )

    json_path = output_dir / "benchmark_results.json"
    markdown_path = output_dir / "BENCHMARK_REPORT.md"
    json_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(build_combined_report(results), encoding="utf-8")
    return results


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Deterministic end-to-end RSA key generation benchmark."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "benchmarks" / "output" / "python",
        help="Directory for JSON and Markdown artifacts.",
    )
    parser.add_argument(
        "--rsa-bits",
        type=int,
        default=DEFAULT_RSA_BITS,
        help=f"RSA modulus size for the main benchmark (default: {DEFAULT_RSA_BITS}).",
    )
    parser.add_argument(
        "--rsa-keypair-count",
        type=int,
        default=DEFAULT_RSA_KEYPAIR_COUNT,
        help=(
            "Number of full RSA keypairs to generate in the main benchmark "
            f"(default: {DEFAULT_RSA_KEYPAIR_COUNT})."
        ),
    )
    parser.add_argument(
        "--bonus-rsa-bits",
        type=int,
        default=DEFAULT_BONUS_RSA_BITS,
        help=f"RSA modulus size for the bonus spot-check (default: {DEFAULT_BONUS_RSA_BITS}).",
    )
    parser.add_argument(
        "--bonus-rsa-keypair-count",
        type=int,
        default=DEFAULT_BONUS_RSA_KEYPAIR_COUNT,
        help=(
            "Number of bonus RSA keypairs to generate in the spot-check "
            f"(default: {DEFAULT_BONUS_RSA_KEYPAIR_COUNT})."
        ),
    )
    parser.add_argument(
        "--public-exponent",
        type=int,
        default=DEFAULT_PUBLIC_EXPONENT,
        help=f"RSA public exponent (default: {DEFAULT_PUBLIC_EXPONENT}).",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    """Run the end-to-end RSA benchmark and print a compact summary."""
    args = parse_args(argv)
    results = run_combined_benchmark(
        output_dir=args.output_dir,
        rsa_bits=args.rsa_bits,
        rsa_keypair_count=args.rsa_keypair_count,
        bonus_rsa_bits=args.bonus_rsa_bits,
        bonus_rsa_keypair_count=args.bonus_rsa_keypair_count,
        public_exponent=args.public_exponent,
    )
    rsa = results["rsa_keygen"]
    bonus = results["bonus_rsa_keygen"]
    print("rsa keygen benchmark complete")
    print(
        "main rsa:",
        f"{rsa['accelerated']['keypair_count']} keypairs,",
        f"{rsa['accelerated']['total_proxy_rejections']} proxy rejections,",
        f"{rsa['accelerated']['mean_time_per_keypair_ms']:.6f} ms/keypair,",
        f"{rsa['speedup']:.2f}x speedup",
    )
    print(
        "bonus rsa:",
        f"{bonus['accelerated']['keypair_count']} keypairs,",
        f"{bonus['accelerated']['total_proxy_rejections']} proxy rejections,",
        f"{bonus['accelerated']['mean_time_per_keypair_ms']:.6f} ms/keypair,",
        f"{bonus['speedup']:.2f}x speedup",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
