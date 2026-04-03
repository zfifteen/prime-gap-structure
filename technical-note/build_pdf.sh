#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p export

pandoc technical_note.md \
  --citeproc \
  --pdf-engine=xelatex \
  --output export/z-band-prime-prefilter-technical-note.pdf
