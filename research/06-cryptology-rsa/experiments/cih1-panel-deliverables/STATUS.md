# CIH-1 Panel Deliverables — Intake Status

| Model | Status | Notes |
|-------|--------|-------|
| Meta AI | **QA PASS** | Hold-out corpus `pgs_holdout_corpus_meta_ai_v1` (60) |
| Gemini | **QA PASS (freeze + baselines)** | Freeze + baselines smoke + full-corpus baselines run |
| ChatGPT | **QA PASS (analysis)** | Engine used; RA fixed `write_jsonl` `\\n` → real newlines |
| DeepSeek | **FIRED / DISQUALIFIED** | Fabricated integrity artifacts; never cite |

## RA experiment execution (2026-08-08)

**Path:** `_ra_cih1/`  
**Run:** `scripts/run_cih1.sh` (carriers → baselines → analysis → gemini primary)

| Gate | Result |
|------|--------|
| Carriers extracted (public only) | 60/60 ok |
| Near-square contamination | 0/60 |
| Analysis included | 60/60 |
| ChatGPT decision (R rule) | **`no_difference`** (median_R ≈ 1) |
| Gemini median_delta | 9.5, p≈5e-12 (micro-effect; sign-test stand-in) |
| Factorization claim | **none** |

Details: `_ra_cih1/RESULTS.md`  
Human decision needed: `_ra_cih1/WHAT_YOU_DO.md` (A/B/C)

## Gates

- DeepSeek evidence: **never cite**
- CIH-1 first pass: **executed**; official call pending principal A/B/C
- Claim language: measured / hypothesis only

Last update: RA full CIH-1 pass complete; awaiting decision rule choice.
