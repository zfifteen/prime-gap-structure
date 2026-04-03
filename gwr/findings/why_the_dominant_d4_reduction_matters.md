# Why The Dominant $d=4$ Reduction Matters

This note records the project-level and number-theoretic significance of the
dominant $d=4$ arrival reduction now documented in this repository.

The underlying empirical finding is recorded in
[`dominant_d4_arrival_reduction_findings.md`](./dominant_d4_arrival_reduction_findings.md).
That finding is already documented on:

- exact full scans to $10^6$ and $2 \times 10^7$,
- deterministic even-band windows at every decade from $10^8$ through
  $10^{18}$.

So the purpose of this note is not to repeat the tables. It is to state
clearly what those tables change.

## The Reduction Itself

The supported dominant-case reading is:

- if a tested prime gap has winner class $d(w)=4$, then the gap contains no
  interior prime square;
- once no interior prime square is present, the winner is the first interior
  $d=4$ carrier.

This is narrower than full GWR, but it covers the dominant winner class on the
current surface.

The stricter semiprime-only slogan is already false. The surviving statement is
class-based:

- first interior $d=4$ carrier,

not factorization-type-based:

- first interior semiprime.

That distinction matters because it tells the project which formulation is
actually true.

## What It Changes Inside The Project

### 1. The dominant regime now has a visible mechanism

Before this reduction, the strongest repo story was:

- a divisor-weighted log-score is computed across each gap interior,
- and its winner matches a simple arithmetic rule on the tested surface.

That was already interesting, but it still left the main effect looking like a
global score optimization.

The dominant $d=4$ reduction changes that.

For most tested winner gaps, the mechanism now reads:

- the gap fails to admit any interior prime square,
- then the first interior $d=4$ carrier wins.

That is a local exclusion-and-arrival law, not a full gap-wide search story.

### 2. The project now has a better decomposition

The current repo structure is now cleaner:

- the divisor-normalized field defines the score surface,
- GWR gives the exact winner law on the tested surface,
- the dominant $d=4$ reduction explains why most of that surface collapses so
  cleanly,
- the No-Later-Simpler-Composite condition gives the closure consequence.

This is a better scientific shape than one isolated empirical identity. The
project now has:

- a field,
- a winner law,
- a dominant mechanism,
- and a closure law.

### 3. The proof program narrows

The dominant proof target is no longer “explain the whole winner rule at once.”

The dominant $d=4$ regime splits into two cleaner questions:

- why do prime gaps with $d=4$ winners avoid interior prime squares?
- once no interior prime square is present, why does the first interior
  $d=4$ carrier always win?

That is a much better proof program.

It does not solve full GWR. But it identifies the main regime and states its
mechanism in a form that can plausibly be attacked directly.

### 4. The project now knows which simplifications are safe

This result also protects the project from drifting into a cleaner but false
story.

It would have been tempting to say:

- the winner is the first semiprime.

The exact $2 \times 10^7$ run already shows that this is not true. A thin
prime-cube exception family survives.

So the project can now state, with precision:

- the right low-complexity winner class is $d=4$,
- not “semiprimes” as a factorization type.

That is an important calibration point for every future theorem candidate and
story artifact.

## What It Suggests For Number Theory

### 1. Prime gaps may have a local interior law, not just a length

Prime gaps are usually described by their length.

This project is now isolating a different kind of structure:

- whether a prime square enters the interior,
- where the first $d=4$ carrier appears,
- and how that local divisor profile determines the winner.

If this continues to hold and eventually gets proved, then prime gaps will not
look only like empty stretches between consecutive primes. They will also have
an internal arithmetic structure whose first low-divisor events matter.

### 2. The dominant winner regime looks more like exclusion than optimization

The reduction changes the conceptual picture.

The winner does not primarily look like:

- the point that survives a complicated continuous competition across the whole
  interior.

It looks much more like:

- the first low-divisor carrier that survives the local exclusions of the gap.

That is a different kind of phenomenon.

If that picture is right, then the relevant mathematics may lie less in the
global geometry of the score and more in the short-interval arithmetic of:

- prime squares,
- $d=4$ carriers,
- and the order in which these classes can enter prime-gap interiors.

### 3. The dominant regime moves closer to classical objects

This reduction makes the problem more legible to classical number theory.

Prime squares, prime cubes, divisor classes, and short intervals are familiar
objects. So the dominant regime is no longer only a novel score phenomenon. It
becomes a question about the arrival order of low-divisor classes in intervals
bounded by consecutive primes.

That is a much more recognizable target.

It does not mean the proof is easy. It does mean the project is no longer
asking number theory to explain an unfamiliar scoring rule all at once. It is
asking for a theorem about a very concrete local ordering.

### 4. The project is isolating a candidate local law of gap termination

Combined with the No-Later-Simpler-Composite condition, the dominant reduction
points toward this picture:

- prime squares govern whether the $d=3$ layer can intrude,
- the first interior $d=4$ carrier governs the dominant winner layer,
- and the next prime closes the gap before a later strictly simpler threat can
  appear.

That is not yet a global prime-distribution theorem.

But it is a real candidate for a local theorem about prime-gap interiors and
gap termination. It says that the right endpoint of the gap may be constrained
by the low-divisor events available inside the gap, not only by the abstract
size of the gap.

That is already significant.

## What The Current Validation Status Means

The through-$10^{18}$ validation work for this reduction is already done in the
current deterministic artifact surface:

- exact full scans at $10^6$ and $2 \times 10^7$,
- deterministic even-band windows at every decade from $10^8$ through
  $10^{18}$.

On that current surface:

- every tested $d=4$ winner gap contained no interior prime square,
- every such gap had the first interior $d=4$ carrier as its true winner,
- the semiprime-only version failed, but only through a very thin prime-cube
  exception family.

So the next step is not “start the $10^{18}$ test.” The $10^{18}$ test is now
part of the documented record.

The next step is to decide which formal target comes next:

- a theorem candidate for the dominant $d=4$ reduction itself,
- a tighter exclusion theorem for prime-square absence in $d=4$ winner gaps,
- or a proof path connecting the dominant reduction to the full GWR surface.

## Safe Summary

The dominant $d=4$ reduction matters because it turns the main winner surface
from a mysterious global score identity into a local arithmetic mechanism that
already holds on the current documented exact-and-band ladder through
$10^{18}$.

That does not prove full GWR. But it does identify the dominant regime, the
right winner class, the main exception family, and a much sharper proof target
than the project had before.
