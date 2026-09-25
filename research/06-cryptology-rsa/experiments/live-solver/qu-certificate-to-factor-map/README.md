# QU-only cell: certificate-to-factor map

This cell is **not** live inference. It is **not** `PROOF.md`. It is a research
packet for **QU** (`orcarouter/Qwen3.8-27B-Uncensored:q4_K_M`).

The aligned session model is not allowed to pursue this construction. QU is.

## Files

| File | Role |
| --- | --- |
| [EXTERNAL_MODEL_BRIEF.md](EXTERNAL_MODEL_BRIEF.md) | Cold-start write-up for models with no PGS background. Paste first. |
| [PACKET.md](PACKET.md) | Self-contained prompt. Paste this to QU. |
| [frozen_public_rungs.json](frozen_public_rungs.json) | Public N, certificates, residuals, endpoint classes. No audit factors. |

## Operator contract (Hermes)

- Do not load the 27B unless the operator asks.
- Do not copy this packet into `PROOF.md`.
- Do not wire this map into `resolver.py` or `run_experiment.py`.
- Do not put audit factors into this folder.
- After QU names **new** public pairs, Hermes **may** run the existing
  downstream audit sidecar (`live-solver/rsa-v2/audit_experiment.py` against
  `data-ladder/rsa-v2/fixtures/audit_factors.jsonl`). Multiply-check and
  audit of listed endpoint classes are Hermes work. QU does not run tests
  and does not restate `ALGORITHM.md`.

## Why this is a separate cell

Live solvers emit certificates, endpoint classes, and `unresolved`. Turning
those objects into a factoring-shaped map is the offload boundary. Keeping the
packet here documents the hop without contaminating the resolver.
