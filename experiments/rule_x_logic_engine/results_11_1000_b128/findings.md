# Rule X Logic Engine Findings

## Executive Summary

The tiny logic engine collapses every tested anchor to the true next boundary
when exact chamber closure is allowed, but GWR/NLSC structural consistency
alone eliminates zero candidate boundaries.

This is the key result:

```text
GWR/NLSC consistency annotates candidate chambers.
It does not, by itself, reject false candidate boundaries.
```

Exact chamber closure produced one survivor for every anchor:

```text
exact_unique_match_count = 164 / 164
```

Structural GWR/NLSC consistency produced no rejections:

```text
structural_rejection_count = 0 / 5562
```

## Domain

```text
prime anchors: 11..1000
candidate bound: 128
```

The engine tested `164` prime anchors and `5562` wheel-open candidate boundary
hypotheses.

## Rule Sets

The engine records two layers.

### Structural Layer

For each hypothetical chamber `(p, candidate_q)`, the engine:

1. finds the GWR carrier inside the proposed interior;
2. checks whether any later interior composite has lower divisor count than
   that carrier;
3. rejects the candidate only on direct GWR/NLSC inconsistency.

This layer rejected no candidates.

### Exact Chamber Layer

For each hypothetical chamber, the engine also applies exact small-scale
closure facts:

1. reject the candidate if `candidate_q` is composite;
2. reject the candidate if a prime appears inside `(p, candidate_q)`;
3. keep the candidate only if the proposed chamber is exactly closed.

This layer left exactly one survivor for every anchor, and every survivor was
the audited next prime.

## Summary Metrics

| Metric | Value |
|---|---:|
| Anchors tested | `164` |
| Candidate hypotheses | `5562` |
| Structural rejections | `0` |
| Structural unique anchors | `0` |
| Exact rejections | `5398` |
| Exact unique anchors | `164` |
| Exact unique matches | `164` |
| Verdict | `exact_consistency_collapse` |

## Example: Anchor 89

For anchor `p = 89`, the true next prime is:

```text
q = 97
offset = 8
```

The structural layer keeps every wheel-open candidate because each proposed
chamber can choose its own internally consistent GWR carrier.

The exact layer keeps only offset `8`.

Later candidate `101` at offset `12` is rejected because `97` appears inside
the proposed chamber. Later candidate `119` at offset `30` is rejected because
the candidate itself is composite and because earlier primes appear inside the
proposed chamber.

## Interpretation

The experiment supports the user's framing that the right object is a logic
engine. It also identifies the missing rule precisely.

The existing GWR/NLSC rules do not create contradiction unless the carrier is
already fixed across candidate extensions. If every candidate chamber is free
to choose a new carrier, all candidate chambers remain structurally coherent.

The next experimental rule should therefore be a carrier-lock rule:

```text
Once a candidate chamber establishes a carrier, later candidate extensions
must either preserve that carrier or provide a legal reset certificate.
```

The next probe should test whether that lock/reset rule eliminates false later
candidates without rejecting the true boundary.
