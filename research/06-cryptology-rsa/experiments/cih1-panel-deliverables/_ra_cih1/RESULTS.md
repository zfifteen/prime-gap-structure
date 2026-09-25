# CIH-1 RA Execution Results (single blind pass)

**Status labels:** measured on Meta hold-out corpus (60 cases, 48/50/52-bit) · hypothesis support framing only · **no verified/validated language** · **no factorization claim**

**Date:** 2026-08-08  
**Seed:** `20260808`  
**Artifacts:** `out/`

## Inputs used

| Lane | Path |
|------|------|
| Corpus | `meta_ai/pgs_holdout_corpus_meta_ai_v1` (60 public + audit) |
| Freeze science | Gemini `pgs_cih1_prereg_gemini_v1` + RA machine freeze `inputs/freeze_execution.json` |
| Baselines | Gemini `pgs_cih1_baselines_gemini_v1` |
| Analysis | ChatGPT `pgs_cih1_analysis_chatgpt_v1` (RA fix: `io_jsonl.write_jsonl` real newlines) |
| Carriers | RA extract: immediate lower chamber before `isqrt(N)` via live `rsa-v2` PGS cert backend |

## Carrier extraction (public N only)

| Metric | Value |
|--------|-------|
| n_public | 60 |
| n_carrier_ok | 60 |
| n_unresolved | 0 |
| elapsed | ~3.9 s |
| Definition | `previous_endpoint_at(isqrt(N))` → chamber-reset cert → `carrier_w`, band=`[anchor, reset_endpoint]` |

## Baselines (full Meta corpus)

| Metric | Value |
|--------|-------|
| n_cases | 60 |
| near_square_rate | **0.0** (all pass contamination gate) |
| audit_integrity_failures | 0 |
| fermat_steps_median_non_near_square | 64518 (limit-capped path in package) |
| floor_pass_rate_median (window 1000) | 1.0 |

Interpretation card: near-square exclusion not binding on this corpus; floor density high as expected; integrity clean.

## Analysis (ChatGPT tooling)

| Metric | Value |
|--------|-------|
| n_included / n_excluded | **60 / 0** |
| median_R | 0.99999785 |
| mean_R | 0.99999566 |
| f_beat | 0.9167 (55/60) |
| sign-test one-sided p (delta) | 5.19e-12 |
| **ChatGPT decision** | **`no_difference`** |

Reason: median_R is not ≤ 0.90 (threshold for `carrier_better` under tooling rule). Carriers win often on tiny absolute deltas, but relative distance ratio stays ~1.

## Gemini primary metric (from same case scores)

| Metric | Value |
|--------|-------|
| median_delta_distance = median(median(D_u) − D_c) | **9.5** |
| mean_delta_distance | 10.65 |
| n_positive / n_negative delta | 55 / 5 |
| sign-test one-sided p | 5.19e-12 |
| Gemini text rule (p&lt;0.05 and median_delta&gt;0) | would say `carrier_better` |
| Note | Freeze named Wilcoxon; RA used exact sign test (stdlib). Same direction. |

## Shape finding (critical)

Search bands are **prime-gap chambers near √N**, median width **~28**.

Factor distances are **millions** (median D_c ≈ 4.15e6 on this non-near-square corpus).

So:

- Carrier and every uniform control live in a ~30-wide window near √N.
- Absolute “wins” of order **~10** are real as *within-band geometry*, not as factorization proximity in any operational sense.
- **R ≈ 1** correctly reports “same distance scale as the control.”
- ChatGPT `no_difference` under R-threshold is the **honest primary tooling decision** for “is the carrier substantially closer?”
- Gemini median_delta > 0 with tiny p is a **micro-effect** (order band width, not order D_c). Do not inflate to factor information or RSA claim.

## Allowed claim sentence (locked)

> Measured on hold-out corpus C with N=60 non-near-square balanced semiprimes (48–52 bit): under the frozen uniform-band control inside the immediate lower chamber, GWR `carrier_w` shows a small positive median delta (~9.5) versus the control median with high win rate, but median relative ratio R ≈ 1 and the frozen R-decision is `no_difference`. Hypothesis context only. No factorization claim. No verified/validated language.

## Reproduce

```bash
bash research/06-cryptology-rsa/experiments/cih1-panel-deliverables/_ra_cih1/scripts/run_cih1.sh
```
