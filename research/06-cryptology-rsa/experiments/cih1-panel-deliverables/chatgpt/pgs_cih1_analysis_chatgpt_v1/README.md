# pgs_cih1_analysis_chatgpt_v1

Sandbox analysis tooling for CIH-1 (Carrier Information Hold-Out).

## Scope

This package scores **distance information** supplied by Research Assistant
carrier rows against a deterministic uniform-integer search-band control.
It does not build PGSPG certificates and does not perform factor selection.

Primary case metric:

`D_c = min(|carrier_w-p|, |carrier_w-q|)`

For K uniform controls in the inclusive band `[lo, hi]`:

`D_u = min(|U-p|, |U-q|)`

`R = D_c / max(1, median(D_u))`

The primary aggregate is median R. We also report the fraction of cases for
which the carrier beats the control median.

## Install

No installation is required. Python 3.10+ standard library is sufficient.

## Run

```sh
python3 -m cih1_analysis run   --public path/to/holdout_public.jsonl   --audit path/to/holdout_audit.jsonl   --carrier path/to/carrier_rows.jsonl   --freeze path/to/freeze.json   --out-dir path/to/out   --seed 20260808
```

If `--freeze` is omitted, `freeze_fallback_cih1.json` is used. A supplied freeze
must contain every required field; missing fields fail closed. Gemini's freeze
should be preferred when available.

## Inputs

Public rows: `case_id`, `bits`, `N`.

Audit rows: `case_id`, `N`, `p`, `q`, with optional square-root diagnostics.

Carrier rows: `case_id`, `carrier_w`, `search_band_lo`, `search_band_hi`.
Public, audit, and carrier data are joined only by `case_id`.

## Exclusions

Defaults are:
- absolute distance from sqrt(N) >= 100000
- relative distance from sqrt(N) >= 0.01

A case failing either threshold is excluded. The audit factors are used for
scoring and exclusion measurement, not for choosing the carrier.

## Statistics

The fallback uses an exact one-sided sign test over nonzero
`median(control distance) - carrier distance` deltas. The default decision
requires median R <= 0.90, f_beat >= 0.60, p < 0.05, and at least 30 included
cases. Control-better requires median R >= 1.10 and two-sided p < 0.05.

## Important boundaries

Bidirectional floor reciprocity is not a primary success criterion.
There is no historical false-class blacklist. No primality test, gcd-based
factor selector, Pollard/Fermat success criterion, or RSA-v3 certificate
construction is used.

This package makes no factorization breakthrough claim, no RSA/RH oracle claim,
and never reports a result as verified or validated. Reporting language is
limited to measured-on-hold-out-corpus / hypothesis-support framing.

This is sandbox analysis tooling / hypothesis support.
