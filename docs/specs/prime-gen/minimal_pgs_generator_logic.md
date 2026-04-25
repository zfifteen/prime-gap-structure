# Minimal PGS Generator Logic

The generator has one job: start from an accepted anchor prime `p` and emit the
next prime `q`.

The generator never withholds an answer. If the PGS boundary rule determines
the next boundary, the generator emits it. If the PGS boundary rule is not
complete enough yet, the generator uses explicit trial-division or factorization
fallback arithmetic to finish the selection and emits the correct `q`.

With fallback arithmetic allowed, 100% completeness and 100% accuracy are
minimum requirements.

Each emitted line has exactly two fields:

```json
{"p": 11, "q": 13}
```

`q` is the generator's next-prime output. A separate downstream audit still
checks every emitted record, but audit is verification after emission, not the
mechanism that chooses `q`.

## Stage 1: Anchor

The anchor `p` is the current known prime.

The generator accepts `p` as input. It does not prove `p` during generation. The
input side is responsible for supplying accepted anchors.

For every accepted anchor, the generator emits exactly one record.

## Stage 2: Chamber

The initial chamber is the finite interval to the right of `p` that the
generator inspects while choosing `q`.

Inside the chamber, the generator may use PGS structure:

- offsets from the anchor;
- wheel-open positions;
- divisor-class relations;
- no-later-simpler-composite ceilings;
- the smallest boundary selector state needed by the current rule.

The chamber is not a place to ask a primality oracle which number is prime. It
is the local arithmetic region where the PGS rule decides the next boundary. If
the PGS rule does not decide, fallback arithmetic completes the answer.

If the initial chamber does not contain a fallback-accepted `q`, the generator
expands the chamber by a fixed deterministic rule and continues. Chamber
expansion is part of fallback completion, not a primality oracle.

The default expansion rule is:

- start with `chamber_width = candidate_bound`;
- inspect candidates from `p + 1` through `p + chamber_width`;
- if no `q` is found, double `chamber_width`;
- repeat until exactly one `q` is emitted.

## Stage 3: Carrier

GWR identifies the simplest leftmost carrier `w` inside the chamber.

The carrier is not the boundary. It is a landmark that helps orient the local
PGS state.

The rule `q = w + 1` is false as a general rule and is forbidden.

The carrier may contribute its location and divisor class to the boundary rule,
but it does not by itself authorize the final value of `q`.

## Stage 4: Boundary Rule

The complete generator needs a boundary rule:

$$q = B(p, S, w, d(w))$$

In plain language:

- `p` is the current anchor;
- `S` is the smallest local state needed to make the boundary choice
  single-valued;
- `w` is the GWR carrier;
- `d(w)` is the divisor class of the carrier;
- `B` chooses the proposed next boundary `q`.

The main PGS object still to derive is the complete form of `B`.

If the available state `S` is sufficient, the generator emits the selected `q`.

If `S` is insufficient, deterministic fallback arithmetic selects the correct
`q`, and the generator emits that value.

## Stage 5: Emission

Emission is unconditional for accepted anchors.

Correctness is also unconditional. Every emitted `q` must be the actual next
prime after `p`, whether it came from the PGS boundary rule or from the
last-resort arithmetic fallback.

For each anchor `p`, the generator emits exactly one line:

```json
{"p": 11, "q": 13}
```

The line contains no extra fields. It contains no carrier data, relation
history, proof object, approval flags, counters, status categories, or hidden
diagnostics.

Implementations may write sidecar diagnostics keyed by `p`. A sidecar record
may report whether `q` came from the PGS boundary rule or from fallback
arithmetic. Sidecar diagnostics are not part of the emitted generator stream.

## Allowed Arithmetic

The preferred path is PGS-derived arithmetic:

- anchor arithmetic;
- chamber offsets;
- wheel-open positions;
- GWR carrier selection;
- divisor-class relations;
- no-later-simpler-composite ceilings;
- boundary selector state.

Trial division or factorization may appear only when no derived PGS rule is
available to make the generator work. If used, it must be explicit, minimal, and
documented as temporary last-resort arithmetic. It must not be hidden inside the
boundary rule or presented as the final PGS solution.

The fallback path is deterministic:

- inspect candidates to the right of `p` in increasing order;
- reject a candidate when a concrete divisor is found;
- for candidate `n`, the fallback divisor check is exhausted only when every
  integer divisor `d` with `2 <= d <= floor(sqrt(n))` has been tested, or when
  an explicit deterministic factorization routine has returned no nontrivial
  factor;
- if any divisor is found, reject `n`;
- if no divisor exists after the complete check, accept `n` as `q`;
- emit that accepted candidate as `q`.

This fallback exists to guarantee completeness and accuracy while the PGS
boundary rule is still incomplete.

Generation must never call these tools:

- `isPrime`;
- Miller-Rabin;
- `nextprime`;
- probabilistic primality tests;
- ECPP;
- PARI primality checks;
- sieve-based prime generation.

After emission, a separate downstream audit may use classical validation tools.
Audit results may confirm or reject emitted records, but they never choose `q`
inside generation.

## Completion Standard

A complete minimal PGS generator satisfies these conditions:

- every accepted anchor emits exactly one record;
- every emitted `q` is the actual next prime after `p`;
- every record has exactly `p` and `q`;
- no forbidden tool is used inside generation;
- fallback arithmetic selects the correct `q` whenever the PGS boundary rule is
  incomplete;
- chamber expansion is deterministic and continues until one `q` is found;
- downstream audit checks the emitted records after generation.

The long-term target is a derived PGS boundary rule that makes `B` complete and
minimizes or removes temporary last-resort trial division and factorization.
