# Rule X Algorithm Findings

## Executive Summary

The tiny algorithm collapses every tested input prime to the true next prime
when exact search-interval closure is allowed, but GWR/NLSC structural consistency
alone eliminates zero candidate next primes.

This is the key result:

```text
GWR/NLSC consistency annotates proposed intervals.
It does not, by itself, reject false candidate next primes.
```

Exact search-interval closure produced one remaining candidate for every input prime:

```text
exact_unique_match_count = 164 / 164
```

Structural GWR/NLSC consistency produced no rejections:

```text
structural_rejection_count = 0 / 5562
```

## Domain

```text
input primes: 11..1000
candidate bound: 128
```

The algorithm tested `164` input primes and `5562` wheel-open candidate next prime
hypotheses.

## Rule Sets

The algorithm records two layers.

### Structural Layer

For each hypothetical interval `(p, candidate_q)`, the algorithm:

1. finds the GWR-selected integer inside the proposed interior;
2. checks whether any later interior composite has lower divisor count than
   that integer;
3. rejects the candidate only on direct GWR/NLSC inconsistency.

This layer rejected no candidates.

### Exact Search Interval Layer

For each hypothetical interval, the algorithm also applies exact small-scale
closure facts:

1. reject the candidate if `candidate_q` is composite;
2. reject the candidate if a prime appears inside `(p, candidate_q)`;
3. keep the candidate only if the proposed interval is exactly closed.

This layer left exactly one remaining candidate for every input prime, and every remaining candidate was
the audited next prime.

## Summary Metrics

| Metric | Value |
|---|---:|
| Input primes tested | `164` |
| Candidate hypotheses | `5562` |
| Structural rejections | `0` |
| Structural unique input primes | `0` |
| Exact rejections | `5398` |
| Exact unique input primes | `164` |
| Exact unique matches | `164` |
| Verdict | `exact_consistency_collapse` |

## Example: Input Prime 89

For input prime `p = 89`, the true next prime is:

```text
q = 97
offset = 8
```

The structural layer keeps every wheel-open candidate because each proposed
search interval can choose its own internally consistent GWR-selected integer.

The exact layer keeps only offset `8`.

Later candidate `101` at offset `12` is rejected because `97` appears inside
the proposed interval. Later candidate `119` at offset `30` is rejected because
the candidate itself is composite and because earlier primes appear inside the
proposed interval.

## Interpretation

The experiment supports the user's framing that the right object is a logic
model. It also identifies the missing rule precisely.

The existing GWR/NLSC rules do not create contradiction unless the integer is
already fixed across candidate extensions. If every proposed interval is free
to choose a new integer, all proposed intervals remain structurally coherent.

The next experimental rule should therefore be a selected-integer-lock rule:

```text
Once a proposed interval establishes a selected integer, later candidate extensions
must either preserve that selected integer or provide a legal reset record.
```

The next probe should test whether that lock/reset rule eliminates false later
candidates without rejecting the true next prime.
