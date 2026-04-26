# Rule X Consistency-Collapse Logic Engine

## Executive Summary

The Rule X logic engine is a finite candidate-elimination engine for next-prime
boundary inference from an accepted anchor prime `p`.

It does not score candidate primes. It does not search until the next prime. It
builds candidate boundary hypotheses and eliminates the hypotheses whose
proposed chambers contradict available PGS evidence.

On the current high-scale chamber-reset surface:

```text
decade windows: 10^8 through 10^18
anchors per decade: 256
candidate bound: 1024
anchors tested: 2816
```

the current rule stack produced:

```text
exact boundary matches: 2816 / 2816
coverage: 100.000000%
unresolved anchors: 0
false emissions: 0
candidate-bound misses: 0
```

The result is significant because the engine now distinguishes current-chamber
boundary evidence from later-chamber tail evidence. Once the first resolved
survivor appears, later unresolved candidates are assigned to later chambers
and no longer block emission for the original anchor.

The earlier semiprime-shadow landmark hold remains necessary. It prevents
two-factor witness-horizon landmarks from being promoted into false boundaries.
The chamber-reset rule then closes the remaining coverage gap by classifying
later unresolved tails as post-boundary chamber material.

## Core Object

For an accepted anchor prime `p`, define a finite set of candidate right
boundaries:

$$C(p, H) = \{p + h : 1 \leq h \leq H,\ p + h \in W_{30}\}.$$

Here `W_30` is the set of integers whose residue modulo `30` is wheel-open.
The experiment uses `H = 128` and wheel-open residues modulo `30`:

```text
1, 7, 11, 13, 17, 19, 23, 29
```

Each candidate `c = p + h` defines a proposed chamber:

$$I(p, c) = \{p+1, p+2, \dots, c-1\}.$$

The engine asks one question:

```text
If c were the next prime boundary, can the proposed chamber remain consistent
with the current PGS evidence?
```

The boundary is inferred by consistency collapse followed by chamber reset:

```text
all impossible candidate chambers are removed;
the first resolved survivor appears;
that survivor closes the current chamber;
later unresolved candidates are assigned to later chambers;
the first resolved survivor is emitted as q_hat.
```

## Rule Vocabulary

### Candidate Boundary Hypothesis

A candidate boundary hypothesis is one proposed statement:

```text
q_hat = p + h
```

It is not assumed prime. It is a node in the logic engine.

### Positive Composite Witness

A positive composite witness is a deterministic factor `r <= B` such that:

$$r \mid n.$$

If a candidate boundary has a positive composite witness, that candidate is
rejected.

If an interior wheel-open position has no positive witness, that interior
position remains unresolved. Absence of a witness is not primality evidence.

### Resolved Survivor

A candidate is a resolved survivor when:

1. the candidate itself has no positive composite witness;
2. all wheel-open interior positions in its proposed chamber are closed by
   positive composite evidence;
3. the proposed chamber contains a carrier available to the rule stack;
4. no active rule rejects the candidate.

Resolved survivor does not mean "proved prime" in the mathematical sense. It
means "not eliminated by the label-free finite rule stack."

### Unresolved Hold

An unresolved hold is an abstention state before chamber reset. A candidate
with unresolved interior positions remains active until a resolved survivor
closes the current chamber.

Before chamber reset, unresolved alternatives block emission. After the first
resolved survivor, later unresolved alternatives belong to a later chamber and
do not compete with the current anchor's boundary.

### Semiprime-Shadow Landmark

A semiprime-shadow landmark is a wheel-open candidate or interior position that
has no positive witness within the current witness horizon but is large enough
to hide a two-factor composite whose factors both exceed that horizon.

Let `B` be the witness bound and let `s` be the first prime greater than `B`.
The first possible two-factor composite with both factors beyond `B` is:

$$s^2.$$

Therefore, a no-witness candidate `n` satisfying

$$n \geq s^2$$

is held open as a semiprime-shadow landmark.

This is not a rejection. The semiprime-shadow landmark is load-bearing PGS
evidence. The engine does not promote it to a resolved boundary survivor until
it is cleared by additional evidence.

### Carrier Lock

Each proposed chamber has a GWR-style carrier: the leftmost known composite in
the proposed interior with minimum divisor count among known composites.

The carrier is not locked merely because it appears. The engine locks a carrier
only after a resolved survivor exists.

In logic-puzzle language:

```text
the chamber story cannot become binding until the proposed boundary has earned
resolved-survivor status.
```

### Lower-Divisor Threat

After a carrier `w` is locked, the first later known composite `t` with lower
divisor count is a lower-divisor threat:

$$t > w,\ d(t) < d(w).$$

Under GWR/NLSC, a locked carrier cannot be followed inside the same prime gap
by a strictly simpler composite. Therefore, once the carrier is legitimately
locked, the first certified lower-divisor threat becomes a right-boundary
ceiling.

The engine rejects later candidate boundaries that extend beyond this threat.

### Chamber Reset

A chamber reset occurs at the first resolved survivor `r` after anchor `p`.

The observable state is:

```text
p ... r ... u
```

where `r` is the first resolved survivor and `u` is a later unresolved
candidate.

The reset rule is:

```text
once r is resolved, r closes the p-chamber;
later unresolved candidates u are post-reset chamber material;
u is not a competing boundary for anchor p.
```

This rule does not promote arbitrary candidates. It activates only after the
existing Rule X stack has produced a resolved survivor. The reset classifies
the later tail. It does not create the first survivor.

## Rule Stack

The current Rule X chamber-reset stack is:

```text
1. Build wheel-open candidate boundary hypotheses.
2. Reject candidate composites with positive composite witnesses.
3. Hold candidate chambers with unresolved wheel-open interiors.
4. Hold semiprime-shadow landmarks open instead of treating them as resolved q.
5. Lock the carrier only after a resolved survivor exists.
6. Find the first certified lower-divisor threat after the locked carrier.
7. Reject candidate boundaries beyond that threat.
8. Identify the first resolved survivor r.
9. Reset the chamber at r.
10. Exclude later unresolved candidates as post-reset chamber material.
11. Emit r as q_hat.
12. Audit classically after emission.
```

The decisive safety rule is step `4`. Before this rule, semiprime-shadow
landmarks were incorrectly promoted to resolved boundary survivors. That caused
premature carrier locks and true-boundary rejection. After the hold-open rule,
the tested `11..100000` surface has zero true-boundary rejections for witness
bounds `97` and `127`.

The decisive coverage rule is step `9`. Before this rule, the engine found the
true boundary as the first resolved survivor but refused to emit when later
unresolved tail candidates remained. After chamber reset, those tail candidates
are assigned to later chambers and no longer block the current boundary.

## Why GWR/NLSC Alone Did Not Collapse Candidates

GWR and NLSC are interior consistency laws. If each candidate chamber is allowed
to choose its own carrier from scratch, every proposed chamber can often remain
internally coherent.

The initial structural-only run showed:

```text
structural_rejection_count = 0
structural_unique_anchor_count = 0
```

This does not weaken GWR/NLSC. It identifies the missing operational condition:

```text
candidate extensions must not be allowed to freely rewrite the carrier story
after a carrier has legitimately locked.
```

The logic engine supplies that missing operational condition.

## Why The Naive Carrier Lock Failed

The naive rule was:

```text
lock the first carrier immediately
```

On `11..100000`, `candidate_bound = 128`, this was unsafe:

```text
rule_x_rejection_count = 297753
rule_x_unique_anchor_count = 4162
rule_x_true_boundary_rejected_count = 7297
```

The rule locked too early. Many anchors begin with a small composite near
`p + 1`, but the true gap later introduces the actual carrier before the prime
boundary. Locking the first carrier converts real reset structure into a false
contradiction.

## Why The Semiprime-Shadow Landmark Hold Is Necessary

The failed label-free runs revealed a single obstruction family. At
`witness_bound = 97`, the true-boundary rejections were caused by candidates
with no witness at or below `97` that were actually:

```text
492 distinct semiprimes
15 prime squares
```

Examples:

```text
10609 = 103^2
11413 = 101 * 113
11449 = 107^2
11639 = 103 * 113
13231 = 101 * 131
```

These are semiprime-shadow landmarks. They mark the two-factor layer just
beyond the current witness horizon. The error was not their existence. The
error was treating them as resolved prime-boundary survivors.

The hold-open rule fixes this by preserving the landmark state:

```text
no witness <= B and n >= next_prime(B)^2
=> SEMIPRIME_SHADOW_LANDMARK_HOLD
```

The candidate remains active but unresolved. It cannot lock the carrier and it
cannot be emitted.

## Measured Surface

### Chamber-Reset Decade Ladder

The chamber-reset rule was rerun on the same high-scale decade ladder used for
the previous Rule X and classical comparisons:

```text
decades: 10^8 through 10^18
anchors per decade: 256
candidate bound: 1024
anchors tested: 2816
```

The aggregate result:

```text
exact matches: 2816
coverage: 100.000000%
unresolved anchors: 0
false emissions: 0
candidate-bound misses: 0
tail cases converted by reset: 2303
tail candidates excluded by reset: 77457
total runtime: 36.951566 seconds
```

Per-decade result:

| Decade | Anchors | Exact matches | Unresolved | False emits | Bound misses |
|---:|---:|---:|---:|---:|---:|
| `10^8` | `256` | `256` | `0` | `0` | `0` |
| `10^9` | `256` | `256` | `0` | `0` | `0` |
| `10^10` | `256` | `256` | `0` | `0` | `0` |
| `10^11` | `256` | `256` | `0` | `0` | `0` |
| `10^12` | `256` | `256` | `0` | `0` | `0` |
| `10^13` | `256` | `256` | `0` | `0` | `0` |
| `10^14` | `256` | `256` | `0` | `0` | `0` |
| `10^15` | `256` | `256` | `0` | `0` | `0` |
| `10^16` | `256` | `256` | `0` | `0` | `0` |
| `10^17` | `256` | `256` | `0` | `0` | `0` |
| `10^18` | `256` | `256` | `0` | `0` | `0` |

This is a decade-window result, not exhaustive coverage of every prime through
`10^18`.

### Tested Runs

| Run | Anchors | Candidate bound | Witness bound | Unique matches | True rejected |
|---|---:|---:|---:|---:|---:|
| label-free lock before landmark hold | `11..100000` | `128` | `97` | `2107` | `507` |
| label-free lock before landmark hold | `11..100000` | `128` | `127` | `2144` | `331` |
| label-free lock before landmark hold | `11..100000` | `128` | `317` | `2231` | `0` |
| Rule X with semiprime-shadow landmark hold | `11..100000` | `128` | `97` | `311` | `0` |
| Rule X with semiprime-shadow landmark hold | `11..100000` | `128` | `127` | `488` | `0` |

The `317` run is a finite full-witness control for this surface because
`317 > sqrt(100128)`. It shows the carrier-lock pressure rule is safe when
false boundary promotion is removed by complete small-scale witness coverage.

The semiprime-shadow landmark hold gives the same zero true-rejection safety
without full witness coverage, at the cost of holding more candidate chambers
unresolved.

### Current Best Guarded Runs

At `witness_bound = 97`:

```text
label_lock_rejection_count = 189148
label_lock_unique_resolved_anchor_count = 311
label_lock_unique_resolved_match_count = 311
label_lock_true_boundary_rejected_count = 0
```

At `witness_bound = 127`:

```text
label_lock_rejection_count = 201033
label_lock_unique_resolved_anchor_count = 488
label_lock_unique_resolved_match_count = 488
label_lock_true_boundary_rejected_count = 0
```

## Emission Contract

The chamber-reset logic engine may emit when all of these hold:

```text
first_resolved_survivor exists
semiprime-shadow landmarks before that survivor are not promoted
positive composite witnesses reject closed candidate boundaries
carrier lock and lower-divisor threat rules do not reject the survivor
true-boundary labels have not been consulted
```

Later unresolved candidates do not block emission after chamber reset:

```text
p ... first_resolved_survivor ... later_unresolved_tail
      ^ emit this boundary       ^ classify as later chamber material
```

The emitted experimental record should remain minimal if promoted into a
generator-style path:

```json
{"p": 11, "q": 13}
```

All rule status, carrier lock, landmark, threat, and audit fields belong in
sidecar records.

## Audit Boundary

Classical labels are downstream audit only. The rule engine must not use:

- `nextprime`;
- `isprime`;
- Miller-Rabin;
- prime-marker masking;
- actual gap width;
- scan-to-first-prime behavior.

The current experiment script includes exact labels for measurement and
development comparison, but the Rule X decision layer is the label-free
candidate-elimination path described above.

## Relation To Existing Artifacts

This artifact supersedes the loose "Rule X" brainstorming label with a precise
candidate-elimination and chamber-reset rule stack.

It is related to these earlier lines of work:

- `positive_composite_witness_rejection`;
- carrier-locked pressure ceilings;
- boundary certificate graph solving;
- semiprime-shadow recovery;
- unresolved candidate holds.

The first new contribution is the semiprime-shadow landmark hold before carrier
lock. It prevents unresolved two-factor landmarks from being promoted to
boundary survivors.

The second new contribution is chamber reset at the first resolved survivor.
It converts the later unresolved tail from apparent boundary competition into
post-boundary chamber structure.

## Current Status

Rule X with semiprime-shadow landmark hold is a safe finite inference engine on
the documented `11..100000`, `candidate_bound = 128` surface for
`witness_bound = 97` and `127`:

```text
true_boundary_rejected_count = 0
```

Before chamber reset, it did not resolve every anchor:

```text
witness_bound = 97:  311 / 9588 exact unique matches
witness_bound = 127: 488 / 9588 exact unique matches
```

Rule X with chamber reset resolved the full decade-window ladder:

```text
10^8 through 10^18
2816 / 2816 exact matches
0 unresolved
0 false emissions
0 candidate-bound misses
```

The chamber-reset rule has been promoted into the minimal generator path as
`pgs_chamber_reset_v1` while preserving the emitted record contract and keeping
classical labels downstream.

Promoted generator check:

```text
surface: 11..100000
candidate_bound: 128
anchors tested: 9588
PGS emissions: 9588
rule_id: pgs_chamber_reset_v1
failed emissions: 0
```

## Artifact Links

- Experiment script:
  [../../../experiments/rule_x_logic_engine/run_logic_engine.py](../../../experiments/rule_x_logic_engine/run_logic_engine.py)
- Guarded `witness_bound = 97` summary:
  [../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w97_shadow_guard/summary.json](../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w97_shadow_guard/summary.json)
- Guarded `witness_bound = 127` summary:
  [../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w127_shadow_guard/summary.json](../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w127_shadow_guard/summary.json)
- Guarded findings:
  [../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w127_shadow_guard/findings.md](../../../experiments/rule_x_logic_engine/results_11_100000_b128_label_w127_shadow_guard/findings.md)
- Chamber-reset probe script:
  [../../../experiments/rule_x_logic_engine/run_chamber_reset_probe.py](../../../experiments/rule_x_logic_engine/run_chamber_reset_probe.py)
- Chamber-reset decade ladder summary:
  [../../../experiments/rule_x_logic_engine/chamber_reset_decade_ladder_1e8_1e18_a256_b1024/summary.json](../../../experiments/rule_x_logic_engine/chamber_reset_decade_ladder_1e8_1e18_a256_b1024/summary.json)
- Chamber-reset probe report:
  [../../../experiments/rule_x_logic_engine/chamber_reset_probe_1e8_1e18_a256_b1024/report.md](../../../experiments/rule_x_logic_engine/chamber_reset_probe_1e8_1e18_a256_b1024/report.md)
