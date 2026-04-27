# PGS Backward Semiprime Progress Report

## Scope

This report summarizes the semiprime-branch progress that has been made so far
and records the current state of the new backward-walker line of work.

The sequence matters. The current backward work did not begin in isolation. It
was built on top of earlier exact `PGS` recovery milestones in the same
repository, then narrowed into a local number-line orientation probe, then
rebuilt into a pure-`PGS` lane search after the first direct-hit walker family
failed.

## Strongest Supported Results

The strongest results now in hand are:

- the semiprime branch already clears one full official `127`-bit gate on a
  committed known-factor audit, with rung `2` the first passing rung, exact
  recovery recall `0.75`, top-1 routed-window recall `1.0`, top-4
  routed-window recall `1.0`, and the archived exact `127`-bit case recovered;
- the new modulus-orientation runner now documents the exact three-gap `PGS`
  neighborhood around a modulus without starting from `sqrt(N)`;
- the first backward direct-hit family was falsified on the toy odd distinct
  semiprime surface;
- the rebuilt pure-`PGS` backward lane harness is not dead: on the full toy
  surface `<= 5000`, the best law reaches `32 / 980` lane successes while the
  prime-endpoint control remains `0 / 980`.

Those four facts define the present state of the branch.

## Earlier Semiprime Branch Breakthrough

Before the backward walker work began, the branch had already crossed an
important threshold: it produced one deterministic, official, full-stage
`127`-bit recovery result from local prime-gap `PGS` structure.

That result is documented in
[pgs_127_official_gate_breakthrough.md](./pgs_127_official_gate_breakthrough.md)
and measured in
[../../../output/semiprime_branch/pgs_127_official_audit_summary.json](../../../output/semiprime_branch/pgs_127_official_audit_summary.json).

The committed gate result is:

- official rung: `2`
- stage passed: `true`
- exact recovery recall: `0.75`
- top-1 routed-window recall: `1.0`
- top-4 routed-window recall: `1.0`
- archived exact case recovered: `true`

This matters because the backward walker is not being explored as a substitute
for a branch with no measured wins. It is being explored as the next
orientation of a branch that already has one audited recovery regime.

## Modulus Gap Orientation Milestone

The first backward-specific milestone was not a factor walker. It was a local
orientation instrument.

That runner lives in
[../../../benchmarks/python/predictor/pgs_modulus_gap_orientation.py](../../../benchmarks/python/predictor/pgs_modulus_gap_orientation.py).
Its job is narrow and exact:

- take one odd composite modulus `N`;
- place `N` on the number line without using `sqrt(N)`;
- identify the previous gap, the containing gap, and the following gap;
- write the full interior divisor structure of each gap;
- record the exact `GWR` selected integer and local `d=3` / `d=4` structure for each gap.

The focused regression surface is
[../../../tests/python/predictor/test_pgs_modulus_gap_orientation.py](../../../tests/python/predictor/test_pgs_modulus_gap_orientation.py).
The sentinel modulus is `121`.

This milestone established the exact local object that the later backward
walker would operate on:

- `N` as an anchor on the number line;
- the prime gap immediately before `N`;
- the prime gap containing `N`;
- the prime gap immediately after `N`;
- the exact interior divisor field and `GWR` selected integer in each of those gaps.

That orientation artifact closed the first conceptual gap in the program. The
branch no longer had to speak abstractly about “working backward from the
modulus.” It now had an exact, reproducible local neighborhood around the
modulus from repo `PGS` math alone.

## First Backward Walker Failure

The first backward walker family asked the wrong question.

It treated the walker state as a composite anchor and scored success as a
direct factor hit. On the toy surface of all odd distinct semiprimes
`15 <= N <= 5000`, that family failed completely.

The initial harness was then rebuilt rather than abandoned. The main lesson
from the failure was structural:

- for odd distinct semiprimes, the hidden factors are prime;
- a composite-only direct-hit walker cannot land on `p` or `q`;
- pure local one-step rules collapse into generic attractors instead of
  preserving modulus-specific information.

So the failure was informative. It showed that the missing object was not “a
better composite landmark.” The missing object was a hidden-factor lane that
could be preserved across steps.

## Rebuilt Pure-PGS Backward Lane Harness

The current backward harness lives in
[../../../benchmarks/python/predictor/pgs_semiprime_backward_law_search.py](../../../benchmarks/python/predictor/pgs_semiprime_backward_law_search.py),
with focused tests in
[../../../tests/python/predictor/test_pgs_semiprime_backward_law_search.py](../../../tests/python/predictor/test_pgs_semiprime_backward_law_search.py).

The rebuilt harness changes the experiment in three exact ways.

### 1. Success is now lane preservation

The harness no longer scores success as “did a composite anchor directly equal
one factor.”

It now scores whether a trace preserves one hidden factor through a descending
odd-semiprime lane.

The mental model is:

$$N = p q \rightarrow p q_1 \rightarrow p q_2 \rightarrow \cdots$$

or the analogous `q`-side lane.

### 2. The candidate pool is now narrow and structural

At each step the harness allows only:

- local prime endpoints from the previous and containing neighborhoods;
- lower odd-semiprime interior carriers from those same two gaps.

It does not use residue scores. It does not use `sqrt(N)`. It does not use a
non-`PGS` side channel.

### 3. Prime endpoints are terminal nominees

The walker state remains composite. Prime endpoints are treated as terminal
nominees rather than recursive anchor states.

That keeps the experiment narrow:

- odd semiprimes carry the lane;
- prime endpoints terminate the current local descent;
- the trace is judged by whether it stayed on one hidden-factor lane until
  termination.

## Current Backward Lane Surface

The current measured artifacts are:

- [../../../output/semiprime_branch/pgs_semiprime_backward_law_search_summary.json](../../../output/semiprime_branch/pgs_semiprime_backward_law_search_summary.json)
- [../../../output/semiprime_branch/pgs_semiprime_backward_law_search_trace.jsonl](../../../output/semiprime_branch/pgs_semiprime_backward_law_search_trace.jsonl)

The full default surface is:

- all odd distinct semiprimes `15 <= N <= 5000`
- `980` total cases
- `24` maximum backward steps per trace
- one fixed pure-`PGS` law family

The law family now includes:

- `prime_left_boundary_control`
- `odd_prev_winner_large_offset`
- `odd_prev_d4_large_offset`
- `odd_prev_dmin_large_offset`
- `odd_prev_small_gap_d4_large_offset`

The headline result is:

- best law: `odd_prev_d4_large_offset`
- lane success count: `32 / 980`
- lane success recall: `0.0326530612244898`
- factor reach count: `0 / 980`
- prime-endpoint control lane success count: `0 / 980`

That is the first positive surface for the backward line.

The success is still narrow, but it is real:

- the old direct-hit framing was dead;
- the rebuilt lane framing is not dead;
- the signal appears only after the state space is changed to odd-semiprime
  lane carriers plus terminal prime nominees;
- the best law is `PGS`-only and does not use a residue term.

## What The Best Law Is Actually Doing

The current best law is `odd_prev_d4_large_offset`.

Its sort key is:

1. odd semiprime before prime endpoint,
2. previous gap before containing gap,
3. first `d=4` before later `d=4`,
4. larger offset before smaller offset,
5. smaller `n` as the terminal tie break.

That means the strongest current pure-`PGS` signal is not “go to the exact gap
selected integer” in the abstract.

It is more specific:

- prefer lower odd-semiprime carriers;
- prefer the previous gap;
- prefer the first `d=4` entrance into that local odd-semiprime corridor;
- then move deeper into that corridor rather than hugging the endpoint.

The control law that simply nominates the left prime endpoint does nothing on
the same surface. That matters. It means the lane signal is not coming from a
trivial “always pick the nearest prime” rule.

## What Has Not Happened Yet

The backward line has not yet reached a factor on this rebuilt toy surface.

The current harness records:

- positive lane successes;
- zero exact factor reaches.

So the current backward result is:

- not a factorizer yet;
- not a blind semiprime break;
- not a replacement for the already-working `127`-bit centered audit path.

It is a narrower but important result:

- the pure local direct-hit family was falsified;
- a pure-`PGS` lane family survives that falsification and produces nonzero
  lane preservation.

## Interpretation

The backward work now has one concrete shape.

The path that looks dead is:

- composite-only anchors,
- success defined as direct factor hit,
- memoryless local selected integer chasing.

The path that looks alive is:

- exact modulus gap orientation first,
- odd semiprimes as hidden-factor lane carriers,
- prime endpoints as terminal nominees,
- pure-`PGS` ranking laws over the local previous and containing gaps.

That is not yet enough to reach `p` or `q`.

But it is enough to say something precise:

- there is now measurable, nonzero pure-`PGS` lane signal in the backward toy
  surface;
- the lane object is a better fit to the arithmetic than the earlier direct-hit
  object;
- the next backward cycle should concentrate on strengthening lane persistence
  and lane-to-prime collapse, not on reviving the dead direct-hit family.

## Present State

The semiprime branch now has three stacked levels of progress:

1. one official audited `127`-bit recovery regime already passed;
2. one exact modulus neighborhood probe now exists for backward work;
3. one rebuilt pure-`PGS` backward lane harness now produces nonzero toy lane
   successes.

That is the current position of the branch.
