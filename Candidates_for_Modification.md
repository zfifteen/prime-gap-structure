# Candidates for Modification

Use this as a screening rubric for candidate software that may benefit from the
methods documented in this project.

## Core Fit Attributes

- The software spends meaningful time on prime generation, primality testing,
  sieving, factor screening, or candidate rejection.
- It has a clear prefilter stage where composites can be rejected before
  expensive tests like Miller-Rabin or equivalent.
- That stage is performance-relevant, not just a tiny fraction of runtime.
- The software operates on integers large enough that cheaper structural
  rejection could matter.
- The prime-related path is deterministic or can be isolated into a
  deterministic subpath.
- The code has a narrow insertion point where a DCI/GWR-style prefilter can be
  added without rewriting the whole system.

## Correctness Fit Attributes

- A new prefilter can be added as a reject-only step without changing final
  correctness guarantees.
- The software already separates candidate survival from final prime
  confirmation.
- It is acceptable for the new method to reduce work, but not to replace final
  primality confirmation.
- The surrounding codebase has tests or invariants strong enough to catch false
  rejections quickly.
- The prime path is auditable enough that the change can be explained and
  defended precisely.

## Benchmark Fit Attributes

- The software has a repeatable benchmarkable workflow.
- There is an obvious A/B metric:
  - total runtime
  - number of Miller-Rabin calls
  - number of candidates rejected before expensive testing
  - key generation latency
  - throughput
- The benchmark can be run locally without distributed infrastructure.
- The benchmark can be scoped to a smoke-test version inside this repo before
  cloning the full upstream project.
- The prime-related workload is common enough that a win would be meaningful,
  not synthetic.

## Integration Fit Attributes

- The prime-handling code is in one or a few files, not deeply scattered.
- The software can be exercised through a small wrapper, fixture, or extracted
  benchmark harness.
- The language interface is manageable from the current implementation base.
- A Python proof-of-concept is possible even if the eventual target is C, C++,
  Rust, or Java.
- The software does not require invasive architectural changes just to test the
  idea.

## Adoption Fit Attributes

- The project is widely used or strategically important.
- A measurable win in this software would be easy to explain to outsiders.
- The maintainer culture is friendly to performance patches backed by
  benchmarks.
- The license permits modification, benchmarking, and contribution.
- The software is active enough that a successful patch could plausibly be
  merged or gain attention.

## Communication Fit Attributes

- The improvement can be demonstrated first and explained second.
- A successful patch would let you say:
  - this software is now faster or better
  - here is the benchmark
  - here is the mathematical structure that made it possible
- The benefit is legible to non-specialists.
- The win is not so tiny that it disappears into noise or compiler variance.

## Low-Friction Smoke-Test Attributes

- You can test only the prime-related slice without vendoring the entire
  upstream codebase.
- A minimal harness can mimic the candidate generation path faithfully enough
  for an early A/B.
- The required inputs and outputs are simple:
  - integer candidates in
  - reject or survive decision out
  - final runtime and call counts measured
- The candidate software can be represented by a small benchmark fixture in
  this repo before a full fork.

## Strong Positive Signals

- The software already uses trial division, wheel filtering, or small-factor
  screening before expensive tests.
- Prime generation is called often in real workloads.
- RSA, DSA, or cryptographic key generation is on the hot path.
- `nextprime`, `isprime`, or arbitrary-precision primality routines are central
  user-facing features.
- The project already cares about exactness, determinism, and benchmark
  evidence.

## Weak-Fit or Bad-Fit Signals

- Prime handling is rare or not performance-critical.
- The code only touches tiny integers where the prefilter cannot matter.
- The prime-related path is too entangled to isolate.
- The software is dominated by I/O, networking, or unrelated computation, so a
  prime-speed win would be invisible.
- The project has no reliable benchmark surface.
- A patch would require replacing correctness-critical logic instead of adding a
  reject-only prefilter.
- The maintainers are unlikely to accept performance work without deep
  cryptographic or numerical credibility in that ecosystem.

## What Another LLM Should Return For Each Candidate

- Project name
- Why the software is a fit
- Exact prime-related hotspot
- Likely insertion point for a DCI/GWR prefilter
- Best A/B benchmark metric
- Ease of smoke-testing inside this repo
- Expected integration difficulty
- Why a successful result would matter in practice

## Simple Scoring Rule

Have other LLMs score each candidate from `0` to `2` on these six axes:

- Prime-hotspot relevance
- Clear insertion point
- Benchmarkability
- Correctness safety
- Adoption impact
- Smoke-test feasibility

Then prioritize candidates with the highest total.
