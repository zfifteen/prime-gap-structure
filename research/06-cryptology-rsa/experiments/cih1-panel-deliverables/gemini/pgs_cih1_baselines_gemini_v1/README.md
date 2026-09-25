# CIH-1 Baselines Package (Gemini V1)

This package computes the negative-control baselines and near-square contamination checks for the CIH-1 experiment. It contains pure-Python instrumentation for the hold-out corpus.

**Integrity Limitations (No Execution Protocol)**:
The author model (Gemini) generated this package without a local execution environment. Consequently:
1. `MANIFEST.json` does not contain pre-computed SHA-256 hashes. The RA must run `bash scripts/generate_manifest.sh`.
2. `self_check_report.txt` contains a strict `NO_EXECUTION_PERFORMED` flag rather than fabricated test results.
3. The RA must run `bash scripts/smoke_run.sh` to execute the unit tests and verify the official fixture calculations.

**Non-Claims**:
This package consists entirely of baseline/audit tools. It does NOT execute PGS inference, it does NOT "resolve" RSA pins, and it contains NO "verified/validated" oracle language.

**CLI Usage**:
```bash
# Replay the 40/50/64-bit known fixtures
python3 -m cih1_baselines official-replay --out-dir OUT

# Sweep the CIH-1 hold-out corpus
python3 -m cih1_baselines corpus-baselines --public examples/tiny_public.jsonl --audit examples/tiny_audit.jsonl --out-dir OUT --seed 42 --floor-window 1000 --floor-stride 1 --decoy-samples 50
```
