# GWR Glossary

This glossary is for readers who want to understand the `GWR` finding notes
and essays without already knowing the project vocabulary.

The goal is plain language first.

For each term, this glossary answers two questions:

- what the term means in ordinary language,
- what it means specifically in this repository.

This is not a formal theorem note.
It is a reading aid.

## How To Use This Glossary

If a term sounds grand or unfamiliar, do not assume it is standard number
theory language.

Many terms in this repo are:

- exact technical names for repo-specific objects,
- shorthand labels for quantities measured by a particular scan,
- or plain-language names for a structural reading of the current evidence.

So the right question is usually not “is this a standard textbook term?”

The right question is:

- what object is the repo pointing at,
- and how much of the claim is exact, measured, or interpretive?

This glossary will say that directly.

## Core Gap Terms

### Prime Gap

**Plain language:** The stretch of integers between one prime and the next.

**In this repo:** A prime gap is written as `(p, q)` where `p < q` are
consecutive primes.

Example:

- `(11, 17)` is a prime gap because the integers `12, 13, 14, 15, 16` lie
  between `11` and `17`, and there is no prime strictly between `11` and `17`.

### Gap Interior

**Plain language:** The integers that sit between the two bounding primes.

**In this repo:** For a gap `(p, q)`, the interior is all integers `n` with
`p < n < q`.

### Consecutive Primes

**Plain language:** Two primes with no other prime in between.

**In this repo:** The project almost always studies primes in this local pair
form, because `GWR` is about what happens inside the interval bounded by one
prime and the next.

### Winner

**Plain language:** The interior composite that “wins” under the repo’s score.

**In this repo:** The winner is the interior integer that maximizes the
implemented log-score
`L(n) = (1 - d(n)/2) ln(n)`.

Under `GWR`, that winner is exactly the leftmost interior integer with the
smallest divisor count present in the gap.

### Carrier

**Plain language:** An integer that carries some divisor class or structural
role.

**In this repo:** “Carrier” usually means the actual integer where a particular
divisor class shows up.

Examples:

- “first `d=4` carrier” means the first interior integer with `d(n)=4`,
- “winner carrier” means the actual integer that wins the score.

### Divisor Count

**Plain language:** How many positive divisors a number has.

**In this repo:** Written as `d(n)`.

Examples:

- `d(7) = 2` because `7` has divisors `1, 7`,
- `d(9) = 3` because `9` has divisors `1, 3, 9`,
- `d(10) = 4` because `10` has divisors `1, 2, 5, 10`.

### Divisor Class

**Plain language:** The group of integers that share the same divisor count.

**In this repo:** Saying “the divisor class `4`” means the set of integers
with `d(n)=4`.

So:

- a `d=3` integer is in divisor class `3`,
- a `d=4` integer is in divisor class `4`.

This is one of the most important terms in the repo.

### Minimal Divisor Class

**Plain language:** The smallest divisor count that actually appears inside a
given gap.

**In this repo:** Often written as `d_min` or `δ_min`.

If a gap interior contains divisor classes `4`, `6`, and `8`, then the minimal
divisor class for that gap is `4`.

### Dominant `d=4` Regime

**Plain language:** The most common winner regime on the tested surface.

**In this repo:** Many tested gaps have winners with divisor count `4`, so the
repo often studies that case separately.

This matters because:

- `d=4` is the common winner class,
- the next strictly smaller composite class is then `d=3`,
- and `d=3` corresponds exactly to prime squares.

That makes the dominant regime much more concrete.

## GWR Terms

### GWR

**Plain language:** Short for `Gap Winner Rule`.

**In this repo:** The central prime-gap law being studied.

It says:

- find the smallest divisor count present in the gap interior,
- then take the leftmost interior integer with that divisor count,
- and that integer is exactly the score winner.

### Leftmost Tie-Break

**Plain language:** If two candidates are equally simple, the earlier one wins.

**In this repo:** This is built into the `GWR` rule.

If two interior integers have the same minimal divisor count, the one closer to
the left prime wins.

### Left Flank

**Plain language:** The part of the gap before the winner.

**In this repo:** Usually means all interior integers `n < w`, where `w` is
the winner.

### Right Flank

**Plain language:** The part of the gap after the winner.

**In this repo:** Usually means all interior integers `n > w` and still
strictly less than the right prime.

### Left-Prefix Exclusion

**Plain language:** Before the winner appears, the gap is not allowed to
contain anything equally simple or simpler.

**In this repo:** If `GWR` holds and the winner has divisor count `δ`, then
every earlier interior integer must satisfy `d(n) > δ`.

### Right-Suffix Exclusion

**Plain language:** After the winner appears, the gap is not allowed to
contain anything strictly simpler.

**In this repo:** If `GWR` holds and the winner has divisor count `δ`, then
every later interior integer must satisfy `d(n) >= δ`.

### Divisor-Profile Admission Condition

**Plain language:** The required shape of the divisor counts across a gap if
`GWR` holds.

**In this repo:** This is the profile

`>δ, >δ, ..., >δ, δ, >=δ, >=δ, ..., >=δ`

where `δ` is the winner’s divisor count.

It means the boundary primes are only allowed to bound interiors with that
general structure.

## Spoiler Terms

### Spoiler

**Plain language:** A candidate that could beat the intended winner.

**In this repo:** A spoiler is usually an earlier interior integer that might
have a larger score than the actual `GWR` carrier.

If such a candidate really beat the winner, `GWR` would fail on that gap.

### Earlier Spoiler

**Plain language:** A spoiler that appears before the winner inside the gap.

**In this repo:** This is the main unresolved direction in the proof program.

The right side is easier because later simpler candidates are ruled out by the
winner law and the dominance theorem. The difficult side is the earlier
higher-divisor candidates.

### Spoiler Candidate

**Plain language:** A candidate checked for whether it could be a spoiler.

**In this repo:** Not every spoiler candidate is a real spoiler. It is just an
interior integer that has to be checked.

### Spoiler Template

**Plain language:** A pattern of values or divisor classes that could act like
a spoiler if it were realized in an actual gap.

**In this repo:** This is an interpretive term, not a formal theorem term.

It usually means an abstract pattern that looks dangerous on paper, before
checking whether actual prime gaps ever realize it.

### Spoiler Family

**Plain language:** A whole infinite collection of spoiler-like patterns built
from one formula.

**In this repo:** The class-only obstruction families are examples. They show
that the current abstract inequality does not automatically eliminate every
possible dangerous class pattern.

### Divisor-Class Spoiler

**Plain language:** A spoiler discussed at the level of divisor counts rather
than at the level of one specific gap.

**In this repo:** This usually means talking about a pair like
“winner class `30`, earlier class `32`” rather than one single pair of
integers.

### Spoiler Threshold

**Plain language:** The boundary between safe and unsafe cases.

**In this repo:** For bridge load, the spoiler threshold is `B(k, w) = 1`.
Below `1` is safe. At or above `1` would be dangerous.

## Bridge Terms

### Bridge

**Plain language:** The missing argument that would connect the current exact
evidence to a full theorem.

**In this repo:** “Bridge” often means the remaining no-early-spoiler argument
needed to turn the current finite and asymptotic evidence into a universal
proof.

### Bridge Load

**Plain language:** A normalized measure of how close an earlier candidate is
to becoming a true spoiler.

**In this repo:** Written as `B(k, w)`.

You can read it as:

- `B` near `0` means very safe,
- `B` near `1` means close to dangerous,
- `B >= 1` would mean the spoiler condition is no longer safely satisfied.

### Spoiler Budget

**Plain language:** How much room there is before a candidate becomes a true
spoiler.

**In this repo:** This is informal language for the same idea measured by
bridge load.

If bridge load is `0.0566`, the case is using only about `5.66%` of the
available budget before reaching the threshold `1`.

### Normalized

**Plain language:** Rescaled so values from different settings can be compared
on one common scale.

**In this repo:** Bridge load is normalized because it divides the realized
danger by the critical amount that would be needed for failure.

## Surface And Frontier Terms

### Surface

**Plain language:** The collection of cases measured by a particular scan or
artifact.

**In this repo:** A “surface” is often the whole output of one deterministic
run.

Examples:

- exact through-`2 × 10^7` surface,
- deterministic even-band surface through `10^18`,
- ratio-frontier surface.

### Exact Surface

**Plain language:** A range where every relevant case was checked, not a
sample.

**In this repo:** “Exact through `2 × 10^7`” means the scan checked the whole
range, not selected windows.

### Sampled Surface

**Plain language:** A deterministic selection of windows rather than the whole
number line up to that scale.

**In this repo:** The high-scale ladders often use deterministic sampled
windows rather than exhaustive enumeration.

### Danger Surface

**Plain language:** The part of the measured surface where cases come closest
to violating the target rule.

**In this repo:** This is informal language, not a formal theorem term.

When a note says “danger surface,” it means the region of the scan where the
cases look closest to becoming spoilers or failures.

### Frontier

**Plain language:** The edge of the measured surface where the hardest cases
live.

**In this repo:** “Frontier” means the nearest observed cases to failure or to
some target bound.

### Frontier Leaders

**Plain language:** The specific cases at the front of that hard edge.

**In this repo:** These are the currently hardest observed cases in a scan.

Example:

- a pair like `(30, 32)` may lead the ratio frontier because it comes closest
  to the spoiler threshold among the measured class pairs.

### Motif

**Plain language:** A small repeating local pattern.

**In this repo:** “Tiny motifs” usually means small gap structures such as
gap-`4` or gap-`6` cases that keep reappearing at the frontier.

### Gap-4 Motif

**Plain language:** A hard case living in a prime gap of length `4`.

**In this repo:** Several frontier notes report that the hardest observed exact
cases live in tiny gap-`4` configurations rather than in the largest gaps.

### Hard Regime

**Plain language:** The part of the problem where the cases are hardest.

**In this repo:** Often used for the scale, divisor classes, or local motifs
that come closest to failure.

## Closure Terms

### Closure

**Plain language:** The way the gap ends when the next prime arrives.

**In this repo:** “Closure” usually means whether the right endpoint prime
arrives before a later strictly simpler composite can appear.

### Closure Violation

**Plain language:** A case where the gap closes too late.

**In this repo:** A closure violation means the next prime did **not** arrive
before the relevant later simpler threat. That would contradict the closure
condition being tested.

### No-Later-Simpler-Composite

**Plain language:** Once the winner appears, no later interior integer should
be strictly simpler before the next prime arrives.

**In this repo:** This is both a conditional corollary of `GWR` and a theorem
candidate in its own right.

### Threat Horizon

**Plain language:** The first later point where a more dangerous simpler
candidate could appear.

**In this repo:** Written as `T_<(w)` in general. In the dominant `d=4`
regime, it becomes the next prime square after the winner.

### Prime-Arrival Margin

**Plain language:** How much room is left between the next prime and the
dangerous later threat.

**In this repo:** In the `d=4` case this is `S_+(w) - q`.
Positive means the prime arrived in time.

### Square-Phase Clock

**Plain language:** The countdown from a `d=4` winner to the next prime square.

**In this repo:** This is the repo’s way of making the dominant `d=4` closure
law concrete.

Since the next simpler composite class after `d=4` is `d=3`, and `d=3`
corresponds exactly to prime squares, the next prime square acts like the next
possible “tick” of a simpler threat.

### Square-Phase Utilization

**Plain language:** How much of the available prime-square clock gets used
before the next prime arrives.

**In this repo:** Written as
`U_square(w, q) = (q - w)/(S_+(w) - w)`.

Small utilization means the next prime arrives very early relative to the
available threat horizon.

## Admissibility Terms

### Admissibility

**Plain language:** Whether a pattern is actually allowed to occur.

**In this repo:** “Admissibility” usually means whether a divisor-arrival
pattern can really appear inside an actual gap between consecutive primes.

### Realizable

**Plain language:** Capable of actually occurring.

**In this repo:** A realizable pattern is one that can show up in an actual
prime gap, not just on paper in class-only algebra.

### Realized

**Plain language:** Actually observed in the measured scans.

**In this repo:** “Realized frontier” means the hardest cases that actually
occurred in the artifact surface.

### Class-Only

**Plain language:** Talking only about divisor-count classes, not about actual
prime-gap geometry.

**In this repo:** A class-only argument may show an abstract obstruction family
without proving that the corresponding pattern ever occurs inside a real gap.

### Admissibility Law

**Plain language:** A rule saying which interior patterns are allowed and which
are not.

**In this repo:** This is currently an interpretive target, not an established
theorem. It is the idea that prime gaps may obey stricter realizability rules
than the present comparison inequalities alone reveal.

### Admissibility Censorship

**Plain language:** Most dangerous-looking abstract patterns seem to be filtered
out before they ever appear in real gaps.

**In this repo:** This is the central interpretive finding of
`prime_gap_admissibility_censorship_finding.md`.

It does **not** mean the repo has proved a censorship theorem.

It means the current evidence suggests:

- many spoiler-like patterns are available in abstract class algebra,
- but only a thin subset seems to survive as actual gap interiors.

### Prime-Gap Admissibility Censorship

**Plain language:** The specific version of admissibility censorship for prime
gaps.

**In this repo:** Same idea as above, stated at the level of interiors bounded
by consecutive primes.

## Boundary Terms

### Boundary Placement

**Plain language:** Where the bounding primes are allowed to sit.

**In this repo:** A key newer reading is that the interior winner law does not
only rank composites. It also constrains where the right endpoint prime can
appear.

### Boundary-Placement Law

**Plain language:** A rule about allowed prime endpoints, not just interior
ranking.

**In this repo:** This is the main point of
`prime_boundary_placement_finding.md`.

### Admissible Stopping Region

**Plain language:** The interval inside which the next prime has to arrive for
the gap to stay valid.

**In this repo:** Informal language for the interval between the winner and the
later threat horizon.

### Winner As A Clock

**Plain language:** The winner determines a later time or position at which a
more dangerous simpler candidate could appear.

**In this repo:** This is especially concrete in the dominant `d=4` regime,
where the next prime square is the clock tick.

## Reading-Level Terms

### Exact

**Plain language:** Proven exactly or checked exhaustively on the stated finite
surface.

**In this repo:** Often means a full deterministic scan over the whole range.

### Empirical

**Plain language:** Measured by computation, not yet proved universally.

**In this repo:** Much of the `GWR` surface is empirical in this sense.

### Theorem Candidate

**Plain language:** A formal claim the repo takes seriously but has not yet
proved.

**In this repo:** Terms like `No-Later-Simpler-Composite Theorem` are currently
theorem candidates unless explicitly marked as exact corollaries.

### Finding

**Plain language:** A strong reading or measured result supported by the
current artifact surface.

**In this repo:** A finding may be very important, but it is not automatically
claimed as a universal theorem.

### Exact Corollary

**Plain language:** Something that follows immediately if the parent statement
is true.

**In this repo:** Several “prime placement” and “prefix/suffix exclusion”
statements are exact corollaries of `GWR`.

## Short Reading Tips

When a note feels unreadable, try this translation rule:

- “surface” means “the cases we measured,”
- “frontier” means “the hardest measured cases,”
- “spoiler” means “a candidate that could beat the winner,”
- “bridge load” means “how close that candidate comes,”
- “closure” means “whether the next prime arrives in time,”
- “admissibility” means “whether a pattern can actually happen in a real gap.”

If you want only one sentence to keep in your head, use this one:

`GWR` is trying to say that prime gaps do not allow arbitrary composite
interiors. They seem to allow only very specific low-divisor arrival patterns,
and those patterns may also constrain where the next prime can appear.
