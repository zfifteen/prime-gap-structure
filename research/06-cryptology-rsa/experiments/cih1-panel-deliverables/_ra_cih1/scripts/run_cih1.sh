#!/usr/bin/env bash
# One-shot CIH-1 RA execution: carriers -> baselines -> analysis (single pass).
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
PANEL="$ROOT/research/06-cryptology-rsa/experiments/cih1-panel-deliverables"
RA="$PANEL/_ra_cih1"
META="$PANEL/meta_ai/pgs_holdout_corpus_meta_ai_v1"
BASE="$PANEL/gemini/pgs_cih1_baselines_gemini_v1"
ANAL="$PANEL/chatgpt/pgs_cih1_analysis_chatgpt_v1"
OUT="$RA/out"
SEED=20260808

mkdir -p "$OUT"

echo "=== 1) Extract carriers (public N only) ==="
python3 "$RA/scripts/extract_carriers.py" \
  --public "$META/public/holdout_public.jsonl" \
  --out-carrier "$OUT/carrier_rows.jsonl" \
  --out-detail "$OUT/carrier_detail.jsonl"

echo "=== 2) Convert Meta JSONL ints + full baselines ==="
python3 - <<PY
import json
from pathlib import Path
meta = Path("$META")
out = Path("$OUT")
pub_in = meta / "public/holdout_public.jsonl"
aud_in = meta / "private/holdout_audit.jsonl"
pub_out = out / "public_int.jsonl"
aud_out = out / "audit_int.jsonl"
with pub_out.open("w", encoding="utf-8") as f:
    for line in pub_in.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        r["N"] = int(r["N"])
        f.write(json.dumps(r) + "\n")
with aud_out.open("w", encoding="utf-8") as f:
    for line in aud_in.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        for k in ("N", "p", "q"):
            if k in r:
                r[k] = int(r[k])
        f.write(json.dumps(r) + "\n")
print("converted", pub_out, aud_out)
PY

(
  cd "$BASE"
  export PYTHONPATH=.
  python3 -m cih1_baselines corpus-baselines \
    --public "$OUT/public_int.jsonl" \
    --audit "$OUT/audit_int.jsonl" \
    --out-dir "$OUT/baselines" \
    --seed "$SEED" \
    --floor-window 1000 \
    --floor-stride 1 \
    --decoy-samples 20
)

echo "=== 3) ChatGPT analysis (single pass, seed=$SEED) ==="
(
  cd "$ANAL"
  export PYTHONPATH=.
  python3 -m cih1_analysis run \
    --public "$OUT/public_int.jsonl" \
    --audit "$OUT/audit_int.jsonl" \
    --carrier "$OUT/carrier_rows.jsonl" \
    --freeze "$RA/inputs/freeze_execution.json" \
    --out-dir "$OUT/analysis" \
    --seed "$SEED"
)

echo "=== 4) Gemini primary metric from case scores ==="
python3 "$RA/scripts/gemini_primary_from_scores.py" \
  --case-scores "$OUT/analysis/case_scores.jsonl" \
  --out "$OUT/gemini_primary_summary.json"

echo "=== CIH-1 RA RUN COMPLETE ==="
ls -la "$OUT" "$OUT/analysis" "$OUT/baselines"
