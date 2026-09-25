#!/usr/bin/env bash
# RA-side: compute SHA-256 hashes into MANIFEST.json.
# Portable: sha256sum (Linux) or shasum -a 256 (macOS).
set -euo pipefail

cd "$(dirname "$0")/.."

if command -v sha256sum >/dev/null 2>&1; then
  _hash() { sha256sum "$1" | awk '{print $1}'; }
else
  _hash() { shasum -a 256 "$1" | awk '{print $1}'; }
fi

{
  echo "{"
  echo "  \"package\": \"pgs_cih1_baselines_gemini_v1\","
  echo "  \"author_model\": \"Gemini\","
  echo "  \"integrity_mode\": \"RA_COMPUTED_HASHES\","
  echo "  \"files\": {"
  first=1
  find . -type f \
    ! -name "MANIFEST.json" \
    ! -name ".DS_Store" \
    ! -path "./out_smoke/*" \
    ! -path "./.git/*" \
    ! -path "*/__pycache__/*" \
    ! -name "*.pyc" \
    | sort | while read -r file; do
      hash=$(_hash "$file")
      if [ "$first" -eq 1 ]; then
        printf '    "%s": "%s"' "$file" "$hash"
        first=0
      else
        printf ',\n    "%s": "%s"' "$file" "$hash"
      fi
    done
  echo ""
  echo "  },"
  echo "  \"repro_command\": \"bash scripts/generate_manifest.sh\""
  echo "}"
} > MANIFEST.json

echo "Manifest generated successfully ($(python3 -c 'import json; print(len(json.load(open("MANIFEST.json"))["files"]))') files)."
