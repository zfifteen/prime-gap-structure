#!/usr/bin/env bash
set -e

echo "Running Unit Tests..."
python3 -m unittest discover tests/

echo "Running Integration (Official Replay)..."
python3 -m cih1_baselines official-replay --out-dir out_smoke

echo "Running Integration (Corpus Baselines)..."
python3 -m cih1_baselines corpus-baselines --public examples/tiny_public.jsonl --audit examples/tiny_audit.jsonl --out-dir out_smoke

echo "ALL SMOKE TESTS PASSED."
