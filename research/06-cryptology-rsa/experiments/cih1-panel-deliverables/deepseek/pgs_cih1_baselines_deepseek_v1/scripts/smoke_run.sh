#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Running unittests ==="
python -m pytest tests -q

echo "=== official-replay ==="
python -m cih1_baselines official-replay --out-dir OUT_smoke
echo ">>> official_fixture_replay.json:"
cat OUT_smoke/official_fixture_replay.json

echo "=== corpus-baselines on examples ==="
python -m cih1_baselines corpus-baselines \
  --public examples/tiny_public.jsonl \
  --audit examples/tiny_audit.jsonl \
  --out-dir OUT_smoke \
  --seed 42 \
  --floor-window 5000 \
  --floor-stride 1 \
  --decoy-samples 5

echo "=== baseline_summary.json ==="
cat OUT_smoke/baseline_summary.json

echo "=== PASS baselines package ==="
