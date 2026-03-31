#!/usr/bin/env python3
"""Exact raw composite Z study on prime-gap interior maxima up to 10^6."""

from __future__ import annotations

import math


LIMIT = 1_000_000


def main() -> None:
    divisor_count = [0] * (LIMIT + 1)
    for d in range(1, LIMIT + 1):
        for multiple in range(d, LIMIT + 1, d):
            divisor_count[multiple] += 1

    primes = [n for n in range(2, LIMIT + 1) if divisor_count[n] == 2]

    def log_raw_z(n: int) -> float:
        # This preserves exact raw-Z ordering while avoiding underflow.
        return (1.0 - divisor_count[n] / 2.0) * math.log(n)

    gap_count = 0
    observed_mean_edge_sum = 0.0
    observed_edge2 = 0
    observed_edge_le2 = 0
    observed_d4 = 0
    observed_left = 0
    observed_right = 0
    observed_center = 0

    baseline_mean_edge_sum = 0.0
    baseline_edge2 = 0.0
    baseline_edge_le2 = 0.0
    baseline_d4 = 0.0

    gap_bin_counts = {"4-10": 0, "12-20": 0, "22+": 0}
    gap_bin_edge2 = {"4-10": 0, "12-20": 0, "22+": 0}
    gap_bin_d4 = {"4-10": 0, "12-20": 0, "22+": 0}

    for left_prime, right_prime in zip(primes, primes[1:]):
        gap = right_prime - left_prime
        if gap < 4:
            continue

        position_count = gap - 1
        edge_distance_sum = 0
        edge2_count = 0
        edge_le2_count = 0
        d4_count = 0
        best_n = left_prime + 1
        best_log_z = log_raw_z(best_n)

        for n in range(left_prime + 1, right_prime):
            offset = n - left_prime
            edge_distance = min(offset, gap - offset)
            edge_distance_sum += edge_distance
            edge2_count += int(edge_distance == 2)
            edge_le2_count += int(edge_distance <= 2)
            d4_count += int(divisor_count[n] == 4)

            candidate_log_z = log_raw_z(n)
            if candidate_log_z > best_log_z:
                best_n = n
                best_log_z = candidate_log_z

        peak_offset = best_n - left_prime
        peak_edge_distance = min(peak_offset, gap - peak_offset)

        gap_count += 1
        observed_mean_edge_sum += peak_edge_distance
        observed_edge2 += int(peak_edge_distance == 2)
        observed_edge_le2 += int(peak_edge_distance <= 2)
        observed_d4 += int(divisor_count[best_n] == 4)

        if peak_offset < gap / 2:
            observed_left += 1
        elif peak_offset > gap / 2:
            observed_right += 1
        else:
            observed_center += 1

        baseline_mean_edge_sum += edge_distance_sum / position_count
        baseline_edge2 += edge2_count / position_count
        baseline_edge_le2 += edge_le2_count / position_count
        baseline_d4 += d4_count / position_count

        if gap <= 10:
            gap_bin = "4-10"
        elif gap <= 20:
            gap_bin = "12-20"
        else:
            gap_bin = "22+"

        gap_bin_counts[gap_bin] += 1
        gap_bin_edge2[gap_bin] += int(peak_edge_distance == 2)
        gap_bin_d4[gap_bin] += int(divisor_count[best_n] == 4)

    baseline_mean_edge = baseline_mean_edge_sum / gap_count
    baseline_edge2_share = baseline_edge2 / gap_count
    baseline_edge_le2_share = baseline_edge_le2 / gap_count
    baseline_d4_share = baseline_d4 / gap_count

    observed_mean_edge = observed_mean_edge_sum / gap_count
    observed_edge2_share = observed_edge2 / gap_count
    observed_edge_le2_share = observed_edge_le2 / gap_count
    observed_d4_share = observed_d4 / gap_count

    print(f"limit={LIMIT}")
    print(f"gap_count={gap_count}")
    print(f"observed_mean_edge={observed_mean_edge:.12f}")
    print(f"baseline_mean_edge={baseline_mean_edge:.12f}")
    print(f"mean_edge_enrichment={baseline_mean_edge / observed_mean_edge:.12f}")
    print(f"observed_edge2_share={observed_edge2_share:.12f}")
    print(f"baseline_edge2_share={baseline_edge2_share:.12f}")
    print(f"edge2_enrichment={observed_edge2_share / baseline_edge2_share:.12f}")
    print(f"observed_edge_le2_share={observed_edge_le2_share:.12f}")
    print(f"baseline_edge_le2_share={baseline_edge_le2_share:.12f}")
    print(
        f"edge_le2_enrichment="
        f"{observed_edge_le2_share / baseline_edge_le2_share:.12f}"
    )
    print(f"observed_d4_share={observed_d4_share:.12f}")
    print(f"baseline_d4_share={baseline_d4_share:.12f}")
    print(f"d4_enrichment={observed_d4_share / baseline_d4_share:.12f}")
    print(f"left_share={observed_left / gap_count:.12f}")
    print(f"right_share={observed_right / gap_count:.12f}")
    print(f"center_share={observed_center / gap_count:.12f}")

    for gap_bin in ("4-10", "12-20", "22+"):
        count = gap_bin_counts[gap_bin]
        print(f"bin={gap_bin}")
        print(f"bin_gap_count={count}")
        print(f"bin_edge2_share={gap_bin_edge2[gap_bin] / count:.12f}")
        print(f"bin_d4_share={gap_bin_d4[gap_bin] / count:.12f}")


if __name__ == "__main__":
    main()
