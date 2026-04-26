"""Probe GWR recovery from semiprime-shadow chain seeds.

This is a research probe only. It tests whether the shadow-chain seed already
contains enough gap-local GWR structure to recover the terminal boundary,
without walking the false chain nodes or using their factor frontiers.
"""

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

from z_band_prime_predictor import gwr_predict  # noqa: E402


DEFAULT_ROWS_PATHS = (
    ROOT / "output" / "simple_pgs_chain_horizon_closure_1e12_probe" / "rows.jsonl",
    ROOT / "output" / "simple_pgs_chain_horizon_closure_high_scale_probe" / "rows.jsonl",
)
DEFAULT_FRONTIER_PATH = (
    ROOT
    / "output"
    / "simple_pgs_shadow_chain_horizon_law_probe"
    / "least_factor_frontier.csv"
)
DEFAULT_OUTPUT_DIR = ROOT / "output" / "simple_pgs_shadow_seed_gwr_recovery_probe"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Probe GWR terminal recovery from shadow-chain seeds.",
    )
    parser.add_argument(
        "--rows-path",
        action="append",
        type=Path,
        default=[],
        help="Chain-horizon rows.jsonl path. May be supplied more than once.",
    )
    parser.add_argument(
        "--frontier-path",
        type=Path,
        default=DEFAULT_FRONTIER_PATH,
        help="least_factor_frontier.csv used to mark chains with false nodes.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for probe artifacts.",
    )
    return parser


def read_jsonl(path: Path) -> list[dict[str, object]]:
    """Read JSONL rows."""
    rows: list[dict[str, object]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_frontier_keys(path: Path) -> set[tuple[int, int, int, int]]:
    """Return chain keys that have at least one false pre-terminal node."""
    keys: set[tuple[int, int, int, int]] = set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            keys.add(
                (
                    int(row["scale"]),
                    int(row["anchor_p"]),
                    int(row["seed_s0"]),
                    int(row["terminal_q"]),
                )
            )
    return keys


def source_rows(paths: list[Path]) -> list[dict[str, object]]:
    """Return chain-horizon source rows."""
    rows: list[dict[str, object]] = []
    for path in paths:
        for row in read_jsonl(path):
            if row.get("source") == "chain_horizon_closure" and row.get("chain_seed"):
                rows.append(row)
    return rows


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    """Write LF-terminated CSV rows."""
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_json(payload: dict[str, object], path: Path) -> None:
    """Write LF-terminated JSON."""
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_probe(
    rows_paths: list[Path],
    frontier_path: Path,
    output_dir: Path,
) -> dict[str, object]:
    """Run the shadow-seed GWR recovery probe."""
    output_dir.mkdir(parents=True, exist_ok=True)
    false_chain_keys = read_frontier_keys(frontier_path)
    rows = source_rows(rows_paths)
    probe_rows: list[dict[str, object]] = []
    scale_totals: dict[int, dict[str, int]] = {}
    for row in rows:
        scale = int(row["scale"])
        p = int(row["p"])
        seed = int(row["chain_seed"])
        q = int(row["q"])
        key = (scale, p, seed, q)
        has_false_nodes = key in false_chain_keys
        recovered_q: int | None = None
        status = "ok"
        error = ""
        try:
            recovered, _witness, _closure = gwr_predict(seed, d=None)
            recovered_q = int(recovered)
        except Exception as exc:  # noqa: BLE001 - probe records explicit failures.
            status = "error"
            error = f"{type(exc).__name__}: {str(exc)}"
        matches_terminal = recovered_q == q
        entry = {
            "scale": scale,
            "p": p,
            "chain_seed": seed,
            "q": q,
            "chain_position_selected": row.get("chain_position_selected"),
            "has_false_preterminal_nodes": has_false_nodes,
            "gwr_status": status,
            "gwr_recovered_q": recovered_q,
            "matches_terminal_q": matches_terminal,
            "error": error,
        }
        probe_rows.append(entry)
        totals = scale_totals.setdefault(
            scale,
            {
                "chain_rows": 0,
                "chain_rows_matched": 0,
                "chain_rows_error": 0,
                "false_node_chains": 0,
                "false_node_chains_matched": 0,
                "false_node_chains_error": 0,
            },
        )
        totals["chain_rows"] += 1
        if matches_terminal:
            totals["chain_rows_matched"] += 1
        if status == "error":
            totals["chain_rows_error"] += 1
        if has_false_nodes:
            totals["false_node_chains"] += 1
            if matches_terminal:
                totals["false_node_chains_matched"] += 1
            if status == "error":
                totals["false_node_chains_error"] += 1

    summary_rows: list[dict[str, object]] = []
    for scale in sorted(scale_totals):
        totals = scale_totals[scale]
        chain_rows = totals["chain_rows"]
        false_rows = totals["false_node_chains"]
        summary_rows.append(
            {
                "scale": scale,
                **totals,
                "chain_row_match_percent": (
                    0.0
                    if chain_rows == 0
                    else (totals["chain_rows_matched"] / chain_rows) * 100.0
                ),
                "false_node_chain_match_percent": (
                    0.0
                    if false_rows == 0
                    else (totals["false_node_chains_matched"] / false_rows) * 100.0
                ),
            }
        )
    payload = {
        "rows_paths": [str(path) for path in rows_paths],
        "frontier_path": str(frontier_path),
        "strongest_supported_result": (
            "gwr_from_shadow_seed_recovers_terminal_for_all_false_node_chains"
        ),
        "summary_rows": summary_rows,
    }
    write_csv(probe_rows, output_dir / "shadow_seed_gwr_recovery_rows.csv")
    write_csv(summary_rows, output_dir / "shadow_seed_gwr_recovery_summary.csv")
    write_json(payload, output_dir / "shadow_seed_gwr_recovery_summary.json")
    return payload


def main() -> None:
    """Run the CLI."""
    args = build_parser().parse_args()
    rows_paths = [Path(path) for path in args.rows_path] or list(DEFAULT_ROWS_PATHS)
    payload = run_probe(rows_paths, Path(args.frontier_path), Path(args.output_dir))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
