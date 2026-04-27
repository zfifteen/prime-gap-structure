# Semiprime-Shadow Landmark Guard Findings

## Executive Summary

The semiprime-shadow landmark guard fixes the unsafe label-free selected-integer-lock
rule on the tested `11..100000` surface.

The corrected rule is:

```text
If a candidate has no positive witness <= B but is large enough to hide a
two-factor composite with both factors above B, do not treat it as a resolved
endpoint survivor. Hold it open as a semiprime-shadow landmark.
```

This is not a rejection of the semiprime. The semiprime is a landmark. The
error was treating a semiprime-shadow landmark as if it were already a resolved
prime endpoint.

With the guard enabled:

| witness bound | exact unique matches | true next prime rejected |
|---:|---:|---:|
| `97` | `311 / 9588` | `0` |
| `127` | `488 / 9588` | `0` |

The same surfaces before the guard had true-next-prime rejections:

| witness bound | true next prime rejected before guard |
|---:|---:|
| `97` | `507` |
| `127` | `331` |

## Domain

```text
prime anchors: 11..100000
candidate bound: 128
witness bounds tested: 97, 127
anchors tested: 9588
candidate hypotheses: 324809
```

## Guard Definition

Let `B` be the positive-witness bound. Let `s` be the first prime greater than
`B`.

A candidate `n` with no witness `<= B` is held unresolved when:

$$n \geq s^2$$

because a two-factor composite with both prime factors above `B` can first
appear at `s^2`.

This is a deterministic hold-open rule. It does not factor `n` beyond the
witness horizon.

## Results

### Witness Bound 97

```text
label_lock_rejection_count = 189148
label_lock_unique_resolved_anchor_count = 311
label_lock_unique_resolved_match_count = 311
label_lock_true_boundary_rejected_count = 0
```

### Witness Bound 127

```text
label_lock_rejection_count = 201033
label_lock_unique_resolved_anchor_count = 488
label_lock_unique_resolved_match_count = 488
label_lock_true_boundary_rejected_count = 0
```

## Interpretation

The complete small-scale rule stack is now:

```text
1. Build candidate next-prime hypotheses.
2. Reject candidate composites by positive witness.
3. Hold unresolved interiors open.
4. Hold semiprime-shadow landmarks open instead of treating them as resolved q.
5. Lock the selected integer only after a resolved survivor exists.
6. Reject later candidates beyond the first certified lower-divisor threat.
7. Emit only when exactly one resolved survivor remains and no unresolved
   alternatives remain.
```

This produces exact next-prime inference for a nontrivial subset of anchors with
zero true-next-prime rejections on the tested surface.

The result is program-advancing because the guard directly explains the earlier
failure family: the rows were not random defects. They were semiprime-shadow
landmarks being promoted too early to endpoint survivors.
