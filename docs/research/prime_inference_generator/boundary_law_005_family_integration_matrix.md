# Next-Prime Law 005 Family Integration Matrix

## Status

Next-Prime Law 005A remains candidate-grade. Next-Prime Law 005B is not integration-approved.

The flagged offline integration matrix found that 005A remains zero-wrong on the tested surfaces, but direct 005B absorption fails the hard gate on the origin surface. The combined modes inherit the same failure.

Pure generator output remains forbidden.

## Configuration

The integration matrix used the strongest safe eliminator configuration before absorption:

- input primes: 11..100000, 11..1000000, 100000..200000, 1000000..1100000
- candidate bound: 64
- witness bound: 97
- single-hole positive witness closure: enabled
- selected-integer-locked pressure ceiling: enabled
- selected-integer-lock predicate: unresolved_alternatives_before_threat

The four tested modes were:

- 005A only
- 005B only
- 005A OR 005B
- 005A THEN 005B

## Results

| mode | surface | unique resolved candidates | true next prime rejected | correct absorptions | wrong absorptions | false remaining candidate absorptions | 005A applied | 005B applied | hard gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 005A only | 11..100000 | 25 | 0 | 31 | 0 | 0 | 31 | 0 | pass |
| 005A only | 11..1000000 | 25 | 0 | 31 | 0 | 0 | 31 | 0 | pass |
| 005A only | 100000..200000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | pass |
| 005A only | 1000000..1100000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | pass |
| 005B only | 11..100000 | 33 | 1 | 42 | 1 | 1 | 0 | 43 | fail |
| 005B only | 11..1000000 | 33 | 1 | 42 | 1 | 1 | 0 | 43 | fail |
| 005B only | 100000..200000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | pass |
| 005B only | 1000000..1100000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | pass |
| 005A OR 005B | 11..100000 | 47 | 1 | 59 | 1 | 1 | 31 | 43 | fail |
| 005A OR 005B | 11..1000000 | 47 | 1 | 59 | 1 | 1 | 31 | 43 | fail |
| 005A OR 005B | 100000..200000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | pass |
| 005A OR 005B | 1000000..1100000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | pass |
| 005A THEN 005B | 11..100000 | 47 | 1 | 59 | 1 | 1 | 31 | 29 | fail |
| 005A THEN 005B | 11..1000000 | 47 | 1 | 59 | 1 | 1 | 31 | 29 | fail |
| 005A THEN 005B | 100000..200000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | pass |
| 005A THEN 005B | 1000000..1100000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | pass |

## First Failed Row

The first hard-gate failure is:

- mode: 005B only
- surface: 11..100000
- input prime: 3137
- actual next prime offset: 26
- false absorber offset: 12
- absorbed offsets: 26, 30, 32, 44, 50, 54

The false resolved candidate at offset 12 absorbs the true next prime candidate at offset 26. That violates both required gates:

- true_boundary_rejected_count must remain 0
- absorption_wrong_count must remain 0

## Interpretation

The previous-to-current selected-integer shift lock hardened as a zero-wrong selection rule inside a narrower theorem-discovery population. Direct integration applies it operationally to every row where the local predicate fires.

Those are not the same regime.

The hardening population required the true next prime to already be a resolved candidate with later unresolved alternatives and no active higher-divisor pressure lock. The direct integration path cannot use the true next prime label, so it can fire earlier on false resolved candidates. Input Prime 3137 shows that failure mode explicitly.

## Decision

005A remains preserved as a narrow, zero-wrong candidate:

- higher-divisor pressure lock
- offline integration pass on tested surfaces
- shifted windows abstain safely

005B direct integration is quarantined:

- previous-to-current selected-integer shift lock
- hardening lead remains informative
- direct absorption flag is not safe
- combined 005A/005B modes are not safe

## Next Gate

005B can only return as an integration candidate if a label-free activation guard reproduces the hardening population without using:

- actual next prime labels
- prime markers
- future gap width
- scan-to-first-prime logic
- old recursive walker state

Until such a guard exists, 005B remains a forensic lead rather than an absorption rule.
