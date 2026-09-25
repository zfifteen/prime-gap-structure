#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
python3 -m unittest discover -s tests -v
rm -rf /tmp/cih1_smoke_out
python3 -m cih1_analysis run \
  --public examples/tiny_public.jsonl \
  --audit examples/tiny_audit.jsonl \
  --carrier examples/tiny_carrier.jsonl \
  --freeze freeze_fallback_cih1.json \
  --out-dir /tmp/cih1_smoke_out \
  --seed 20260808
test -s /tmp/cih1_smoke_out/case_scores.jsonl
test -s /tmp/cih1_smoke_out/experiment_summary.json
echo "PASS: CIH-1 ChatGPT sandbox package smoke"
