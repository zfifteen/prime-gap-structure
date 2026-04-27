# Chamber-Reset Decade Ladder: 10^8 Through 10^18

## Executive Summary

Rule X with chamber reset produced full coverage on the decade-window ladder.

```text
decades: 10^8 through 10^18
input primes per decade: 256
candidate bound: 1024
input primes tested: 2816
exact matches: 2816
coverage: 100.000000%
unresolved: 0
false emissions: 0
candidate-bound misses: 0
total runtime: 36.951566 seconds
```

The previous Rule X emission rule resolved `513 / 2816` input primes. The
chamber-reset rule converted the remaining `2303` tail cases by classifying
later unresolved candidates as post-endpoint chamber material.

## Tested Rule

For an input prime `p`, let `r` be the first resolved survivor under the
existing Rule X stack.

The chamber-reset rule is:

```text
r closes the current p-chamber.
Any later unresolved candidate belongs to a later chamber.
Emit r as q_hat.
```

The rule does not create the first survivor. It classifies the unresolved tail
after a survivor has already been resolved.

## Results By Decade

| Decade | Input primes | Exact matches | Unresolved | False emits | Bound misses | Tail cases | Seconds |
|---:|---:|---:|---:|---:|---:|---:|---:|
| `10^8` | `256` | `256` | `0` | `0` | `0` | `195` | `0.334307` |
| `10^9` | `256` | `256` | `0` | `0` | `0` | `208` | `0.473113` |
| `10^10` | `256` | `256` | `0` | `0` | `0` | `212` | `0.793633` |
| `10^11` | `256` | `256` | `0` | `0` | `0` | `213` | `1.015652` |
| `10^12` | `256` | `256` | `0` | `0` | `0` | `205` | `1.447370` |
| `10^13` | `256` | `256` | `0` | `0` | `0` | `206` | `1.757172` |
| `10^14` | `256` | `256` | `0` | `0` | `0` | `209` | `2.501488` |
| `10^15` | `256` | `256` | `0` | `0` | `0` | `211` | `3.741421` |
| `10^16` | `256` | `256` | `0` | `0` | `0` | `218` | `4.854186` |
| `10^17` | `256` | `256` | `0` | `0` | `0` | `207` | `7.288972` |
| `10^18` | `256` | `256` | `0` | `0` | `0` | `219` | `12.744251` |

## Aggregate Totals

| Metric | Value |
|---|---:|
| Input primes tested | `2816` |
| Exact matches | `2816` |
| Coverage | `100.000000%` |
| Unresolved | `0` |
| False emissions | `0` |
| Candidate-bound misses | `0` |
| Tail cases converted | `2303` |
| Tail candidates excluded | `77457` |
| Total runtime | `36.951566` seconds |

## Interpretation

The unresolved input primes were not missing the endpoint. They already contained
the endpoint as the first resolved survivor.

The chamber-reset rule resolves the remaining ambiguity:

```text
p ... first_resolved_survivor ... later_unresolved_tail
      ^ current endpoint         ^ later chamber material
```

Within this decade-window regime, Rule X plus chamber reset reaches complete
audited coverage.

## Scope

This is a decade-window experiment, not exhaustive coverage of every prime
through `10^18`. Classical labels are used for input prime selection and downstream
audit in the experiment harness. The next engineering step is promotion into
the minimal generator path while preserving the two-field emission contract.

## Artifacts

- Runner:
  [../run_chamber_reset_probe.py](../run_chamber_reset_probe.py)
- Aggregate summary:
  [summary.json](summary.json)
- Per-decade directories:
  [10e8](10e8/summary.json),
  [10e9](10e9/summary.json),
  [10e10](10e10/summary.json),
  [10e11](10e11/summary.json),
  [10e12](10e12/summary.json),
  [10e13](10e13/summary.json),
  [10e14](10e14/summary.json),
  [10e15](10e15/summary.json),
  [10e16](10e16/summary.json),
  [10e17](10e17/summary.json),
  [10e18](10e18/summary.json)
