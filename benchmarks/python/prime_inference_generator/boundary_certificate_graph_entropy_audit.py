"""
PGS Entropy/Collision Audit Instrumentation
============================================
Measures boundary information contribution per PGS graph stage.
No isprime, nextprime, d(n)==2, or classical boundary label enters
the entropy rows or stall rows. Classical audit is downstream only.

Output artifacts:
  boundary_certificate_graph_entropy_rows.jsonl
  boundary_certificate_graph_entropy_stalls.jsonl
  boundary_certificate_graph_entropy_summary.json
"""

import json
import math
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Stage ordering (matches solver pipeline)
# ---------------------------------------------------------------------------

STAGES = [
    "initial",
    "after_positive_composite_rejection",
    "after_single_hole_positive_witness_closure",
    "after_carrier_locked_pressure_ceiling",
    "after_005A_R_locked_absorption",
    "after_v1_unresolved_later_domination",
    "after_v2_active_graph_reset_refinement",
    "after_v3_empty_source_extension",
    "after_repaired_v4_positive_nonboundary_guard",
    "final",
]

STAGE_KEY = {s: i for i, s in enumerate(STAGES)}


# ---------------------------------------------------------------------------
# Entropy helpers
# ---------------------------------------------------------------------------

def uniform_entropy(candidate_count: int) -> Optional[float]:
    """
    H = log2(|C|). Returns None for empty set (solver error guard).
    Does not claim the boundary distribution is uniform; this is the
    clean structural uncertainty measure over remaining candidate identities.
    """
    if candidate_count == 0:
        return None
    if candidate_count == 1:
        return 0.0
    return math.log2(candidate_count)


def bits_removed(h_prev: Optional[float], h_curr: Optional[float]) -> Optional[float]:
    if h_prev is None or h_curr is None:
        return None
    return h_prev - h_curr


# ---------------------------------------------------------------------------
# Per-stage record
# ---------------------------------------------------------------------------

@dataclass
class StageRecord:
    stage: str
    active_offsets: list[int]
    rejected_offsets: list[int] = field(default_factory=list)
    absorbed_offsets: list[int] = field(default_factory=list)
    resolved_offsets: list[int] = field(default_factory=list)
    unresolved_offsets: list[int] = field(default_factory=list)

    def to_dict(
        self,
        h_initial: Optional[float],
        h_prev: Optional[float],
    ) -> dict:
        n = len(self.active_offsets)
        h = uniform_entropy(n)
        return {
            "stage": self.stage,
            "active_candidate_count": n,
            "active_offsets": sorted(self.active_offsets),
            "resolved_offsets": sorted(self.resolved_offsets),
            "unresolved_offsets": sorted(self.unresolved_offsets),
            "rejected_offsets": sorted(self.rejected_offsets),
            "absorbed_offsets": sorted(self.absorbed_offsets),
            "entropy_uniform_bits": h,
            "bits_removed_from_previous_stage": bits_removed(h_prev, h),
            "bits_removed_from_initial": bits_removed(h_initial, h),
            "solver_error": "EMPTY_CANDIDATE_SET" if n == 0 else None,
        }


# ---------------------------------------------------------------------------
# Anchor entropy row builder
# ---------------------------------------------------------------------------

def build_entropy_row(
    anchor_p: int,
    candidate_bound: int,
    witness_bound: int,
    stage_records: list[StageRecord],
    true_boundary_offset: Optional[int] = None,
) -> dict:
    """
    Build the full per-anchor entropy row from an ordered list of StageRecords.
    true_boundary_offset is annotated AFTER solving; never used inside the row
    to influence candidate selection.
    """
    assert stage_records[0].stage == "initial", "First stage must be initial"

    h_initial = uniform_entropy(len(stage_records[0].active_offsets))
    h_prev = h_initial

    stage_dicts = []
    first_stall_stage = None
    first_stall_bits = None
    stages_after_first_stall = []

    for sr in stage_records:
        d = sr.to_dict(h_initial, h_prev)
        stage_dicts.append(d)

        h_curr = d["entropy_uniform_bits"]

        # Track first stall: stage where count > 1 and no further reduction
        # from previous stage (i.e., bits_removed == 0 and count > 1)
        if (
            first_stall_stage is None
            and d["active_candidate_count"] > 1
            and d["bits_removed_from_previous_stage"] is not None
            and d["bits_removed_from_previous_stage"] == 0.0
            and sr.stage != "initial"
        ):
            first_stall_stage = sr.stage
            first_stall_bits = h_curr

        if first_stall_stage is not None and sr.stage != first_stall_stage:
            stages_after_first_stall.append(sr.stage)

        h_prev = h_curr

    final = stage_dicts[-1]
    final_count = final["active_candidate_count"]
    final_offsets = final["active_offsets"]
    final_entropy = final["entropy_uniform_bits"]

    solved = final_count == 1
    abstain = final_count > 1
    solver_error = final_count == 0

    row = {
        "record_type": "PGS_GRAPH_ENTROPY_ROW",
        "anchor_p": anchor_p,
        "candidate_bound": candidate_bound,
        "witness_bound": witness_bound,
        "solved": solved,
        "abstain": abstain,
        "solver_error": solver_error,
        "initial_candidate_count": len(stage_records[0].active_offsets),
        "final_candidate_count": final_count,
        "initial_entropy_bits": h_initial,
        "final_entropy_bits": final_entropy,
        "total_bits_removed": bits_removed(h_initial, final_entropy),
        "stages": stage_dicts,
        # Downstream annotation slot; never populated during solving.
        "classical_audit": {
            "true_boundary_offset": true_boundary_offset,
            "audit_status": (
                "NOT_RUN" if true_boundary_offset is None else "ANNOTATED"
            ),
        },
    }

    if abstain:
        pairwise_deltas = sorted(
            set(
                abs(final_offsets[j] - final_offsets[i])
                for i in range(len(final_offsets))
                for j in range(i + 1, len(final_offsets))
            )
        )
        row["stall_profile"] = {
            "record_type": "PGS_GRAPH_ENTROPY_STALL",
            "final_active_offsets": final_offsets,
            "final_entropy_uniform_bits": final_entropy,
            "pairwise_offset_deltas": pairwise_deltas,
            "adjacent_survivor_pairs": [
                [final_offsets[i], final_offsets[i + 1]]
                for i in range(len(final_offsets) - 1)
            ],
            "stage_at_first_stall": first_stall_stage,
            "bits_remaining_at_first_stall": first_stall_bits,
            "stages_active_after_first_stall": stages_after_first_stall,
        }
    else:
        row["stall_profile"] = None

    return row


# ---------------------------------------------------------------------------
# Summary aggregator
# ---------------------------------------------------------------------------

class EntropySummaryAggregator:
    def __init__(self):
        self.anchor_count = 0
        self.solved_count = 0
        self.abstain_count = 0
        self.error_count = 0

        self._initial_entropy_sum = 0.0
        self._final_entropy_sum = 0.0
        self._bits_removed_sum = 0.0

        # per-stage bit yield accumulator
        self._stage_bits: dict[str, float] = {s: 0.0 for s in STAGES}
        self._stage_counts: dict[str, int] = {s: 0 for s in STAGES}

        # stall histograms
        self.stall_candidate_histogram: dict[str, int] = {}
        self.stall_delta_histogram: dict[str, int] = {}
        self.stall_first_stage_histogram: dict[str, int] = {}

    def ingest(self, row: dict):
        self.anchor_count += 1
        if row["solver_error"]:
            self.error_count += 1
            return
        if row["solved"]:
            self.solved_count += 1
        if row["abstain"]:
            self.abstain_count += 1

        if row["initial_entropy_bits"] is not None:
            self._initial_entropy_sum += row["initial_entropy_bits"]
        if row["final_entropy_bits"] is not None:
            self._final_entropy_sum += row["final_entropy_bits"]
        if row["total_bits_removed"] is not None:
            self._bits_removed_sum += row["total_bits_removed"]

        for stage_dict in row["stages"]:
            s = stage_dict["stage"]
            br = stage_dict["bits_removed_from_previous_stage"]
            if br is not None and br > 0:
                self._stage_bits[s] = self._stage_bits.get(s, 0.0) + br
                self._stage_counts[s] = self._stage_counts.get(s, 0) + 1

        if row["abstain"] and row["stall_profile"]:
            sp = row["stall_profile"]
            k = str(sp["final_active_offsets"].__len__())
            k_key = k if int(k) < 5 else "5+"
            self.stall_candidate_histogram[k_key] = (
                self.stall_candidate_histogram.get(k_key, 0) + 1
            )

            for delta in sp["pairwise_offset_deltas"]:
                dk = str(delta)
                self.stall_delta_histogram[dk] = (
                    self.stall_delta_histogram.get(dk, 0) + 1
                )

            fs = sp.get("stage_at_first_stall")
            if fs:
                self.stall_first_stage_histogram[fs] = (
                    self.stall_first_stage_histogram.get(fs, 0) + 1
                )

    def to_dict(self) -> dict:
        n = self.anchor_count - self.error_count
        stage_mean_yield = {}
        for s in STAGES:
            total = self._stage_bits.get(s, 0.0)
            stage_mean_yield[s] = round(total / n, 6) if n > 0 else 0.0

        return {
            "anchor_count": self.anchor_count,
            "solved_count": self.solved_count,
            "abstain_count": self.abstain_count,
            "error_count": self.error_count,
            "solved_rate": (
                round(self.solved_count / self.anchor_count, 6)
                if self.anchor_count
                else 0
            ),
            "mean_initial_entropy_bits": (
                round(self._initial_entropy_sum / n, 6) if n else 0
            ),
            "mean_final_entropy_bits": (
                round(self._final_entropy_sum / n, 6) if n else 0
            ),
            "mean_bits_removed": (
                round(self._bits_removed_sum / n, 6) if n else 0
            ),
            "stage_mean_bit_yields": stage_mean_yield,
            "stall_candidate_count_histogram": dict(
                sorted(self.stall_candidate_histogram.items())
            ),
            "stall_pairwise_delta_histogram": dict(
                sorted(self.stall_delta_histogram.items(), key=lambda x: int(x[0]))
            ),
            "stall_first_stage_histogram": dict(
                sorted(self.stall_first_stage_histogram.items())
            ),
        }


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------

class EntropyAuditWriter:
    def __init__(self, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        self._rows_path = output_dir / "boundary_certificate_graph_entropy_rows.jsonl"
        self._stalls_path = (
            output_dir / "boundary_certificate_graph_entropy_stalls.jsonl"
        )
        self._summary_path = (
            output_dir / "boundary_certificate_graph_entropy_summary.json"
        )

        self._rows_fh = open(
            self._rows_path,
            "w",
            encoding="utf-8",
            newline="\n",
        )
        self._stalls_fh = open(
            self._stalls_path,
            "w",
            encoding="utf-8",
            newline="\n",
        )
        self._aggregator = EntropySummaryAggregator()

    def write_row(self, row: dict):
        self._rows_fh.write(json.dumps(row, sort_keys=True) + "\n")
        if row.get("abstain") and row.get("stall_profile"):
            stall = {
                "anchor_p": row["anchor_p"],
                "candidate_bound": row["candidate_bound"],
                "witness_bound": row["witness_bound"],
                **row["stall_profile"],
            }
            self._stalls_fh.write(json.dumps(stall, sort_keys=True) + "\n")
        self._aggregator.ingest(row)

    def close(self):
        self._rows_fh.close()
        self._stalls_fh.close()
        summary = self._aggregator.to_dict()
        with open(self._summary_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, indent=2, sort_keys=True)
            f.write("\n")
        return summary

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


# ---------------------------------------------------------------------------
# Integration shim: wrap an existing solver stage pipeline
# ---------------------------------------------------------------------------

def instrument_solver(
    anchor_p: int,
    candidate_bound: int,
    witness_bound: int,
    solver_fn,  # callable(anchor_p, candidate_bound, witness_bound) -> list[StageRecord]
    writer: EntropyAuditWriter,
    true_boundary_offset: Optional[int] = None,
):
    """
    Call solver_fn to get ordered StageRecords, build the entropy row,
    and write it. true_boundary_offset is a downstream annotation only.
    """
    stage_records = solver_fn(anchor_p, candidate_bound, witness_bound)
    row = build_entropy_row(
        anchor_p=anchor_p,
        candidate_bound=candidate_bound,
        witness_bound=witness_bound,
        stage_records=stage_records,
        true_boundary_offset=true_boundary_offset,
    )
    writer.write_row(row)
    return row


# ---------------------------------------------------------------------------
# Smoke test / demo (no classical primality used)
# ---------------------------------------------------------------------------

def _demo():
    """
    Demonstrates the instrumentation with two synthetic anchor examples:
    one that resolves, one that stalls. No primality oracle used.
    """
    # Synthetic: anchor resolves cleanly
    resolved_stages = [
        StageRecord("initial", active_offsets=[2, 4, 6, 8, 10, 12, 14, 16]),
        StageRecord("after_positive_composite_rejection",
                    active_offsets=[2, 4, 6, 8, 12, 14],
                    rejected_offsets=[10, 16]),
        StageRecord("after_single_hole_positive_witness_closure",
                    active_offsets=[2, 4, 6, 8, 12, 14],
                    rejected_offsets=[]),
        StageRecord("after_carrier_locked_pressure_ceiling",
                    active_offsets=[2, 6, 12],
                    absorbed_offsets=[4, 8, 14]),
        StageRecord("after_005A_R_locked_absorption",
                    active_offsets=[2, 12],
                    absorbed_offsets=[6]),
        StageRecord("after_v1_unresolved_later_domination",
                    active_offsets=[2],
                    resolved_offsets=[2],
                    unresolved_offsets=[12]),
        StageRecord("after_v2_active_graph_reset_refinement", active_offsets=[2]),
        StageRecord("after_v3_empty_source_extension", active_offsets=[2]),
        StageRecord("after_repaired_v4_positive_nonboundary_guard", active_offsets=[2]),
        StageRecord("final", active_offsets=[2], resolved_offsets=[2]),
    ]

    # Synthetic: anchor stalls at 2 candidates
    stalled_stages = [
        StageRecord("initial", active_offsets=[2, 4, 6, 8, 10, 12]),
        StageRecord("after_positive_composite_rejection",
                    active_offsets=[2, 4, 8, 10, 12],
                    rejected_offsets=[6]),
        StageRecord("after_single_hole_positive_witness_closure",
                    active_offsets=[2, 4, 8, 10, 12]),
        StageRecord("after_carrier_locked_pressure_ceiling",
                    active_offsets=[2, 8, 12],
                    absorbed_offsets=[4, 10]),
        StageRecord("after_005A_R_locked_absorption",
                    active_offsets=[8, 12],
                    absorbed_offsets=[2]),
        StageRecord("after_v1_unresolved_later_domination", active_offsets=[8, 12]),
        StageRecord("after_v2_active_graph_reset_refinement", active_offsets=[8, 12]),
        StageRecord("after_v3_empty_source_extension", active_offsets=[8, 12]),
        StageRecord("after_repaired_v4_positive_nonboundary_guard", active_offsets=[8, 12]),
        StageRecord("final", active_offsets=[8, 12], unresolved_offsets=[8, 12]),
    ]

    output_dir = Path("output/entropy_audit_demo")
    with EntropyAuditWriter(output_dir) as writer:
        for anchor_p, stages in [(101, resolved_stages), (10193, stalled_stages)]:
            row = build_entropy_row(
                anchor_p=anchor_p,
                candidate_bound=128,
                witness_bound=127,
                stage_records=stages,
            )
            writer.write_row(row)
        summary = writer.close()

    print(json.dumps(summary, indent=2))
    print(f"\nArtifacts written to: {output_dir.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PGS Entropy/Collision Audit")
    parser.add_argument("--demo", action="store_true", help="Run synthetic demo")
    args = parser.parse_args()

    if args.demo:
        _demo()
    else:
        print("Import EntropyAuditWriter, StageRecord, build_entropy_row, instrument_solver")
        print("and wire into boundary_certificate_graph_solver.py stage pipeline.")
