"""Downstream audit of the twenty stored chambers and omitted boundary gaps.

Run from the repository root with python3 path/to/this/audit.py.
This reads the pinned measurement artifact; it does not generate PGS outputs.
"""
import json
import math
from pathlib import Path
import re
import subprocess

COMMIT = "362d95e688872786aaab2afe5f9c7edf1977fa8f"
CHAPTER = "research/23-witness-offset-classification"
HERE = Path(__file__).resolve().parent


def tau(n):
    return sum(1 + (d * d != n) for d in range(1, math.isqrt(n) + 1) if n % d == 0)


summary = json.loads(subprocess.check_output(
    ["git", "show", f"{COMMIT}:{CHAPTER}/classification_scan_100000000.json"],
    text=True,
))
l4 = next(row for row in summary["decisions"] if row["name"] == "L4")
assert l4["counterexample_count"] == len(l4["counterexamples"]) == 20
chambers = []
for record in l4["counterexamples"]:
    p, q = record["left_prime"], record["right_prime"]
    r = (p + 1) // 30
    counts = [tau(n) for n in range(p, q + 1)]
    seats = [i for i in range(1, q - p) if counts[i] == 16]
    assert p % 30 == 29 and q - p == 8 and tau(r) == 2
    assert counts[0] == counts[-1] == 2
    assert min(counts[1:-1]) == counts[1] == 16
    assert len(seats) == record["minimum_multiplicity"]
    chambers.append(dict(p=p, q=q, r=r, tau_including_endpoints=counts, tie_seats=seats))

note = (HERE.parent / "the-30r-chamber.md").read_text()
listed = [tuple(int(x.replace(",", "")) for x in match) for match in re.findall(
    r"^\| ([\d,]+) \| ([\d,]+) \| (\d+) \|$", note, re.M
)]
assert len(listed) == 20
table_mismatches = []
for supplied, chamber in zip(listed, chambers):
    actual = (chamber["r"], chamber["p"], len(chamber["tie_seats"]))
    if supplied != actual:
        table_mismatches.append(dict(supplied=supplied, actual=actual))

factors = [
    [2, 3, 5, 588877], [13, 31, 59, 743], [2, 2, 2, 569, 3881],
    [3, 7, 7, 47, 2557], [2, 19, 101, 4603], [5, 17, 307, 677],
    [2, 2, 3, 3, 3, 37, 4421],
]
for offset, row in enumerate(factors, 1):
    assert math.prod(row) == 17666309 + offset
    assert all(tau(factor) == 2 for factor in row)

boundaries = []
for limit, p, q in [(10**6, 999983, 1000003), (10**7, 9999991, 10000019),
                    (10**8, 99999989, 100000007)]:
    counts = [tau(n) for n in range(p, q + 1)]
    assert p < limit < q and counts[0] == counts[-1] == 2
    assert min(counts[1:-1]) > 2
    minimum = min(counts[1:-1])
    boundaries.append(dict(limit=limit, p=p, q=q, residue=p % 30,
                           witness=p + counts.index(minimum, 1), minimum=minimum,
                           tau_including_endpoints=counts))

result = dict(
    status="downstream audit corroboration on named chambers below 10^8",
    source_commit=COMMIT, chambers=chambers,
    distinct_tie_patterns=len({tuple(row["tie_seats"]) for row in chambers}),
    maximum_multiplicity=max(len(row["tie_seats"]) for row in chambers),
    table_mismatches=table_mismatches,
    first_chamber_factorizations=factors, omitted_boundary_chambers=boundaries,
    high_scale_surface_executed=False,
)
(HERE / "audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: result[key] for key in ["status", "distinct_tie_patterns",
                 "maximum_multiplicity", "table_mismatches"]}, indent=2))
