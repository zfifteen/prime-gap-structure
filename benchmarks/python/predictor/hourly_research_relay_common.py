#!/usr/bin/env python3
"""Small shared helpers for the hourly research relay tasks."""

from __future__ import annotations

import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def utc_timestamp_compact() -> str:
    """Return one stable compact UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_timestamp_iso() -> str:
    """Return one stable ISO UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_git(*args: str, capture_output: bool = True) -> str:
    """Run one git command and return its stdout."""
    completed = subprocess.run(
        ["git", *args],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=capture_output,
    )
    return completed.stdout.strip()


def remote_branch_exists(remote_branch: str) -> bool:
    """Return whether one remote branch is visible after fetch."""
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", remote_branch],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return completed.returncode == 0


def ensure_clean_worktree() -> None:
    """Abort when the worktree is dirty before branch-moving task runs."""
    status = run_git("status", "--porcelain")
    if status:
        raise RuntimeError("hourly relay task requires a clean git worktree")


def prepare_task_branch(
    branch_name: str,
    first_launch_base_branch: str,
) -> tuple[str | None, str]:
    """Fetch origin and move onto the requested task branch."""
    ensure_clean_worktree()
    run_git("fetch", "origin")
    remote_branch = f"origin/{branch_name}"
    if remote_branch_exists(remote_branch):
        local_exists = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
            cwd=ROOT,
        ).returncode == 0
        if local_exists:
            run_git("checkout", branch_name)
        else:
            run_git("checkout", "-b", branch_name, remote_branch)
        starting_head = run_git("rev-parse", "HEAD")
        run_git("merge", "--ff-only", remote_branch)
        return starting_head, run_git("rev-parse", "HEAD")

    run_git("checkout", "-b", branch_name, first_launch_base_branch)
    return None, run_git("rev-parse", "HEAD")


def stage_commit_push(
    branch_name: str,
    artifact_paths: list[Path],
    commit_message: str,
) -> str:
    """Stage the requested artifacts, commit them, and push the branch."""
    run_git("add", *[str(path.relative_to(ROOT)) for path in artifact_paths])
    run_git("commit", "-m", commit_message)
    run_git("push", "-u", "origin", branch_name)
    return run_git("rev-parse", "HEAD")


def remote_text(remote_branch: str, path: str) -> str:
    """Read one text artifact directly from a remote branch ref."""
    return run_git("show", f"{remote_branch}:{path}")


def remote_json(remote_branch: str, path: str) -> dict[str, object]:
    """Read one JSON artifact directly from a remote branch ref."""
    return json.loads(remote_text(remote_branch, path))


def read_last_jsonl_row(path: Path) -> dict[str, object] | None:
    """Return the final JSONL row when the file exists and is non-empty."""
    if not path.exists():
        return None
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        return None
    return json.loads(rows[-1])


def append_jsonl_row(path: Path, row: dict[str, object]) -> None:
    """Append one JSON row using LF endings."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_json(path: Path, payload: dict[str, object]) -> None:
    """Write one JSON file with LF endings."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def sigmoid_log_loss(positive_count: int, total_count: int) -> tuple[float, float]:
    """Return the Laplace-smoothed Bernoulli probability and its mean log loss."""
    probability = (positive_count + 1.0) / (total_count + 2.0)
    positive_share = positive_count / total_count if total_count else 0.0
    loss = 0.0
    if total_count:
        loss = -(
            positive_share * math.log(probability)
            + (1.0 - positive_share) * math.log(1.0 - probability)
        )
    return probability, loss
