# Gemini baselines package — RA smoke QA

**Package:** `gemini/pgs_cih1_baselines_gemini_v1/`  
**Author mode:** honest `NO_EXECUTION_PERFORMED` (empty MANIFEST at delivery)  
**RA date:** 2026-08-08

## Command

```bash
cd research/06-cryptology-rsa/experiments/cih1-panel-deliverables/gemini/pgs_cih1_baselines_gemini_v1
export PYTHONPATH=.
bash scripts/smoke_run.sh
bash scripts/generate_manifest.sh
```

## Result: **PASS**

| Check | Outcome |
|-------|---------|
| Unit tests | 7/7 OK |
| Official 40-bit | near_square=true, fermat_steps=0, isqrt=1048573 |
| Official 50-bit | near_square=false, fermat_steps=28534, isqrt=32053641 |
| Official 64-bit | near_square=true, fermat_steps=0, isqrt=3221250486 |
| Tiny corpus integrity | audit_integrity_failures=0 |
| Integrity posture | No fabricated hashes from author; RA computed MANIFEST |

## RA edits (portable only)

- `scripts/generate_manifest.sh`: macOS `shasum`, exclude `__pycache__` / `out_smoke`
- `.gitignore` for smoke artifacts
- `self_check_report.txt` overwritten with RA execution evidence (author NO_EXECUTION flag was the honest starting state)

## Scope note

Smoke uses package `examples/tiny_*.jsonl` only. Full Meta hold-out corpus baseline sweep is a separate RA step before CIH-1 primary scoring.
