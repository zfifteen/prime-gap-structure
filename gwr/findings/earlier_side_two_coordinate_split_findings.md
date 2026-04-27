# Earlier-Side Two-Coordinate Split Findings

This note records a refinement of the current earlier-side reading on the
repository's live `GWR` proof surface.

The main point is not that the old bridge quantity was merely too weak.

The stronger point is this:

the earlier side is governed by two different coordinates of difficulty that do
not collapse cleanly into one normalized scalar.

Those coordinates are:

- direct-score vulnerability, where the absolute margin $L(w) - L(k)$ can
  become small;
- normalized ratio-form tightness, where the counterexample ratio can approach its
  threshold even though the absolute score margin remains comfortably positive.

The current repository already records both extremal cases separately. This note
states the split explicitly, records the direct exact examples that rule out an
over-strong uniform high-class margin claim, and gives a cleaner next
decomposition for the earlier side.

## Strongest Supported Claim

The strongest supported reading is:

all genuine earlier-side score danger is concentrated in a low-class local
search interval, while the current high-class extremal case is only ratio-tight, not
score-tight.

In ordinary language:

- the absolute margin can get small only in tiny local low-divisor cases;
- the normalized ratio can get tight in higher adjacent divisor classes;
- those are different populations;
- so one scalar bridge quantity should not be asked to explain both at once.

This is stronger than saying only that the old bridge does not give the best
proof path.

It says the earlier side itself appears to have a two-coordinate structure.

## The Two Coordinates

### 1. Direct-Score Vulnerability

The direct score is

$$L(n) = \left(1 - \frac{d(n)}{2}\right)\ln n.$$

On the earlier side, the dangerous quantity is the absolute margin

$$L(w) - L(k).$$

The current exact margin scan already shows that the smallest direct-score
margins come from tiny local low-class cases, not from the high-divisor tail.

The current exact leader recorded in
[`no_early_spoiler_margin_findings.md`](./no_early_spoiler_margin_findings.md)
is:

- gap `(7, 11)`,
- selected integer `w = 9` with `d(w) = 3`,
- earlier candidate `k = 8` with `d(k) = 4`,
- direct margin
  $L(w) - L(k) \approx 0.9808292530$.

So the smallest direct slack currently observed is controlled by the smallest
selected divisor-count classes together with tiny offsets and the minimal divisor jump
`delta = 1`.

That is exactly the kind of regime already handled by the live local
admissibility closure.

### 2. Ratio-Form Tightness

The normalized counterexample ratio can be written as

$$\frac{d(k) - 2}{d_{\min} - 2} - \frac{\ln w}{\ln k},$$

or, equivalently, through the bridge load

$$B(k,w) = \frac{\frac{\ln w}{\ln k} - 1}{\frac{\delta}{d_{\min} - 2}}.$$

The current ratio extremum recorded in
[`no_early_spoiler_ratio_frontier_findings.md`](./no_early_spoiler_ratio_frontier_findings.md)
is led instead by adjacent higher divisor classes such as:

- `(30, 32)`,
- `(15, 16)`,
- `(22, 24)`,
- `(18, 20)`,
- `(32, 36)`.

The exact current leader is:

- gap `(2486509, 2486513)`,
- selected integer `w = 2486512` with `d(w) = 30`,
- earlier candidate `k = 2486510` with `d(k) = 32`,
- critical-ratio margin about `0.0714285168`,
- direct margin about `14.7263794181`.

So the ratio extremum is not led by the same population that controls the
direct-score minimum.

The current evidence therefore already separates:

- score-tight low classes,
- from ratio-tight high classes.

## Exact Counterexamples To An Over-Strong High-Class Margin Claim

One tempting next step would have been:

prove that once `d(w)` exceeds a fixed threshold `D0`, the earlier side has a
uniform direct-score margin

$$L(w) - L(k) \ge \eta(D_0) > 0$$

with one explicit constant `eta(D0)` independent of `p`.

That strong form is not supported by the current evidence.

Two direct exact examples on the current code path already rule out the
specific claim `D0 = 8`, `eta = 6`:

### Example 1

- gap `(439, 443)`,
- selected integer `w = 442` with `d(w) = 8`,
- earlier candidate `k = 441` with `d(k) = 9`.

Then

$$L(442) = -3 \ln 442, \qquad L(441) = -3.5 \ln 441,$$

so

$$L(w) - L(k) \approx 3.037727417830869.$$

This is positive, but it is already well below `6`.

### Example 2

- gap `(149767, 149771)`,
- selected integer `w = 149769` with `d(w) = 15`,
- earlier candidate `k = 149768` with `d(k) = 16`.

Then

$$L(w) - L(k) \approx 5.958377954229576.$$

Again the margin is positive, but still below `6`.

So the current exact surface already excludes the stronger claim that one can
take a uniform high-class constant as large as `6` starting at `d(w) >= 8` or
even at `d(w) >= 12`.

## The Mathematical Obstruction In The Naive Lower-Bound Sketch

Write

$$c(w) = 1 - \frac{d(w)}{2} < 0, \qquad \delta = d(k) - d(w) \ge 1.$$

Then

$$L(w) - L(k) = \frac{\delta}{2}\ln k + c(w)\bigl(\ln w - \ln k\bigr).$$

With

$$\Delta \ln = \ln\left(\frac{w}{k}\right) > 0,$$

this gives

$$L(w) - L(k) \ge \frac{1}{2}\ln k - |c(w)| \, \Delta \ln.$$

The problem is the sign.

Lower-bounding `d(w)` only lower-bounds `|c(w)|`, and that makes the
subtracted term larger, not smaller.

So a statement of the form

- `d(w) >= D0`,

by itself does not move the inequality in the right direction for a uniform
positive lower bound.

To prove a universal high-class margin theorem of this type, one would also
need an effective upper control on `d(w)` in the selected integer population.

The current explicit tools do not supply that to infinity without reintroducing
the same bounded-regime obstruction that already limited the old bridge.

In particular:

- Dusart's explicit gap bound gives only a bounded unconditional window;
- universal divisor majoration still lets the selected divisor-count class grow;
- so the naive analytic route does not yield one infinite-range constant
  `eta(D0)` from a lower bound on `d(w)` alone.

## What The Current Proof Surface Already Does Instead

The live proof surface does not depend on that stronger uniform high-class
lemma.

It already closes the earlier side through a different architecture:

1. the low-class local admissibility search interval closes the genuine score-danger
   regime;
2. the residual low-class closure artifacts discharge the remaining requested
   low-class surface;
3. the proof surface is then backed by the exact no-counterexample audits recorded in
   the live theorem-facing documents.

See:

- [`prime_gap_admissibility_theorem.md`](./prime_gap_admissibility_theorem.md),
- [`no_early_spoiler_margin_findings.md`](./no_early_spoiler_margin_findings.md),
- [`../../GWR_PROOF.md`](../../GWR_PROOF.md).

So this note is not reopening the theorem.

It is refining the conceptual reading of why the live closure has the shape it
does.

## Cleaner Three-Part Decomposition

The current evidence suggests a cleaner proof-facing decomposition of the
earlier side:

### 1. Low-Class Search Interval

Use the existing local admissibility theorem and the residual low-class closure
artifacts for the only regime where absolute score danger is real.

This is already the live exact closure mechanism for the small selected divisor-count classes.

### 2. Capped-Class Margin Lemma

Instead of one infinite-range high-class theorem, isolate a bounded divisor
band

$$D_0 \le d(w) \le D_1$$

and prove an explicit positive direct-score margin on that finite class range.

That would still be a real theorem, but it would no longer overstate what the
current analytic tools can support.

### 3. Very-High-Class Reducer

Route the remaining unbounded divisor tail through the existing large-prime and
minimal-integer reduction surface, or through a future censorship theorem if a
cleaner local occurrence law is found.

The current reducer status is recorded in
[`large_prime_reducer_findings.md`](./large_prime_reducer_findings.md).

## Why This Is Cleaner Than The Old Single-Load Bridge

The old bridge quantity tried to normalize the whole earlier side into one
scalar.

That compressed together two different questions:

- when can the absolute score margin get small?
- when can the normalized ratio get tight?

The current evidence says those questions are answered by different families.

So the cleaner architecture is:

- local exact closure for genuine danger,
- bounded-band margin control for moderate selected divisor-count classes,
- reducer logic for the unbounded tail.

That is a better scientific shape than forcing one bridge load to carry all
three jobs at once.

## Open Questions

The immediate next probes suggested by this split are:

1. What is the smallest practical capped-class ceiling `D1` for which a fully
   explicit margin lemma can be proved once and for all?
2. How low can the direct-margin floor fall on the exact current surface when
   conditioned on `d(w) >= 8`, `12`, `16`, and larger thresholds?
3. Can the observed ratio-tight high-class population be explained by a local
   censorship law about which adjacent divisor-class patterns can actually
   occur in prime-gap interiors?
4. Is there a sharper reducer that uses actual selected integer occurrence constraints,
   not only minimal integers with a given divisor count?

## Safe Summary

The earlier side is not well described by one normalized bridge load alone.

The live repository now supports a sharper reading:

- low-class cases control direct score danger,
- higher adjacent classes control ratio-form tightness,
- and those are different extremal cases.

That does not weaken the current `GWR` proof surface.

It explains why the current proof closes through a local search interval and exact
audit route rather than through one global analytic inequality.
