# GWR/DNI Semiprime Branch for Large-RSA Early Rejection

## Status

This note opens the semiprime research branch tracked in issue #5.

The branch thesis is narrow and strong:

> The GWR/DNI arithmetic in this repository may provide major compute savings in large-RSA prime-generation pipelines by exposing the dominant `d=4` layer just below the prime fixed point and enabling stronger deterministic early rejection of doomed composite candidates.

This is **not** a claim of general semiprime factor recovery or superior exact semiprime certification versus classical methods.

## Exact Arithmetic Base

The branch starts from the repository's live arithmetic identity

```text
Z(n) = n^(1 - d(n)/2)
L(n) = (1 - d(n)/2) ln(n)
```

Immediate consequences:

- if `n` is prime, `d(n)=2`, so `Z(n)=1`
- if `n=pq` with distinct primes `p != q`, then `d(n)=4`, so `Z(n)=1/n`
- if `n=p^2`, then `d(n)=3`, so `Z(n)=1/sqrt(n)`

So distinct semiprimes occupy an exact arithmetic shell directly below the prime fixed point.

## Why Semiprimes Matter Here

The current GWR surface already says the dominant selected-integer regime is a `d=4` regime.

Live repo finding:

- when the implemented score maximizer has `d(w)=4`, the tested surface shows no interior prime square
- under that square exclusion, the selected integer is exactly the first interior `d=4` integer

This is the main bridge from GWR/DNI to semiprimes.

The stronger slogan

```text
first interior semiprime wins
```

is false on the current surface because a thin prime-cube exception family survives inside the broader `d=4` class.

So the right research object is:

```text
the d=4 layer, dominated by distinct semiprimes, with a thin prime-cube residue
```

not a semiprime-only theorem.

## Why This Could Matter For Large RSA

RSA prime generation is dominated by repeated rejection of composite candidates.

The practical question is not whether this branch beats classical algorithms at exact semiprime recognition or factor recovery.

The practical question is whether the repo's arithmetic structure lets the pipeline reject many doomed composite candidates earlier and more cheaply than a classical probable-prime path alone.

That is already plausible from current repo artifacts because the production path reports:

- about `91%` rejection before Miller-Rabin
- `2.09x` deterministic end-to-end speedup for `2048`-bit RSA key generation
- `2.82x` deterministic end-to-end speedup for `4096`-bit RSA key generation

The branch hypothesis is that explicit modeling of the `d=4` / semiprime-dominant layer may strengthen that advantage.

## Claim Limit

### In scope

- deterministic early rejection in large-RSA candidate loops
- structural analysis of the `d=4` layer
- separation of distinct semiprimes from prime squares and prime cubes
- cost-normalized rejection studies
- exact calibration on small surfaces and benchmark scaling on large surfaces

### Out of scope

- claims of a new general factoring algorithm
- claims of faster exact semiprime certification than classical methods
- claims that GWR alone reveals the factors of RSA semiprimes

## Main Research Questions

### RQ1 — How much of the current rejection power is tied to the d=4 layer?

Measure the share of current candidate-loop savings that can be attributed to structure related to the dominant `d=4` shell rather than to generic shallow-factor filtering.

### RQ2 — Can semiprime-layer-aware deterministic proxies improve the current front end?

Test whether a front end that explicitly models the `d=4` / semiprime-dominant layer can reject more doomed candidates at equal or lower cost than the current proxy path.

### RQ3 — Does the gain survive honest classical baselines?

Test whether any measured gain survives comparison against classical baselines matched for cost, especially bounded trial tables and ordinary shallow composite screens.

## First Falsification Plan

The branch fails if any of the following happens:

1. explicit `d=4` / semiprime-layer modeling adds no measurable rejection benefit beyond current table-depth effects
2. any observed gain disappears under cost-matched classical baselines
3. the semiprime-dominant layer does not materially improve rejection economics at large RSA sizes

The branch succeeds only if at least one semiprime-layer-aware deterministic front end improves cost-normalized rejection or end-to-end key-generation time on committed large-RSA benchmark surfaces.

## Immediate Deliverables

### D1 — Exact d=4 structural note

Build a note with:

- distinct semiprime selected-integer share
- prime-cube residue share
- first-`d=4` arrival offsets
- square-exclusion conditional counts

### D2 — Candidate-loop economics note

Break current savings into:

- stage-by-stage rejection share
- Miller-Rabin calls avoided
- wall-clock contribution by stage
- scaling with bit length and table depth

### D3 — Semiprime-layer proxy ablation

Compare:

- current proxy path
- cost-matched classical baseline
- semiprime-layer-aware proxy variants

with explicit false-remaining candidate and false-reject audits.

## Working Interpretation

The branch is worth pursuing because the current repo already supports all three legs needed for a real systems claim:

1. an exact arithmetic identity that isolates the semiprime-dominant `d=4` layer
2. a live prime-gap result showing that the dominant selected-integer regime is first-`d=4` arrival under square exclusion
3. practical benchmark evidence that deterministic early composite rejection already produces large RSA savings

So the research program is not speculative in the weak sense.

It is a focused attempt to determine whether the repo's strongest arithmetic structure can be converted into a stronger large-RSA rejection front end.

## Next Artifact

The next artifact after this note should be a measured baseline file under:

```text
docs/research/semiprime_branch/d4_layer_baseline.md
```

backed by committed CSV/JSON outputs and one benchmark harness update.
