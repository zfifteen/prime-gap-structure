Technical Specification: PGS Prime Inference Generator

1. Purpose

This specification defines a new deterministic prime-generation architecture based on Prime Gap Structure (PGS). The generator does not use Miller-Rabin, probabilistic primality testing, trial division primality testing, or classical sieve-based generation as part of its generation logic.

Instead, it uses deterministic PGS structure to infer prime endpoints from the internal arithmetic structure of prime-gap interiors.

The generator emits PGS-inferred primes. Classical primality methods may be applied afterward as an external validation layer, but they are not part of the generator itself.

2. Core Idea

Traditional prime generation asks:

Is this candidate prime?

The PGS Prime Inference Generator asks:

Given a known prime endpoint and the deterministic structure of the following composite chamber, where is the next prime endpoint inferred to be?

This inverts the usual workflow.

Classical generators repeatedly test candidates. The PGS generator attempts to walk the prime sequence by inferring the next prime from deterministic gap-interior structure.

3. High-Level Architecture

The system consists of four conceptual layers:

1. Anchor Layer
    * Starts from a known prime p.
    * The known prime can be supplied externally or taken from a validated seed list.
2. PGS Inference Layer
    * Uses deterministic repo rules such as DNI, GWR, raw-Z/log-Z scoring, divisor-class arrival, no-later-simpler-composite closure, and recursive gap-walker logic.
    * Infers the next prime endpoint q without classical primality testing.
3. Emission Layer
    * Emits q as a PGS-inferred prime.
    * Records the inference path, gap interior evidence, selected integer, divisor-class logic, and confidence metadata.
4. External Validation Layer
    * Runs after generation.
    * Uses classical methods only to audit the generated output.
    * Validation may include deterministic primality proof, Miller-Rabin, trial division, ECPP, PARI/GP, SymPy, GMP, or other external checkers.
    * Validation results do not feed back into the generation step unless explicitly running a debugging or calibration mode.

4. Non-Goals

The generator is not:

* A Miller-Rabin wrapper.
* A faster sieve.
* A trial-division primality tester.
* A probabilistic prime candidate filter.
* A cryptographic primality certificate by itself.
* A factorization method for RSA moduli.
* A replacement for classical certification in security-critical deployment.

The generator’s claim is narrower and more novel:

It generates primes by deterministic PGS inference, then allows classical validation afterward.

5. Terminology

PGS-Inferred Prime

A number emitted by the generator as the inferred next prime endpoint according to deterministic PGS rules.

Before external validation, this number should not be called a certified prime.

Anchor Prime

A known prime from which the generator begins a recursive inference walk.

Gap Interior

For consecutive primes p < q, the gap interior is:

I = {p + 1, ..., q - 1}

In the generator, the future right endpoint q is not assumed known. The inference layer attempts to infer it.

GWR Integer

The leftmost integer of the minimum divisor-count class present in a gap interior. Under the GWR framing, this integer is the raw-Z/log-Z selected integer inside the gap.

Raw-Z / Log-Z Score

The log-score used by the repo:

L(n) = (1 - d(n)/2) log(n)

where d(n) is the divisor count.

No-Later-Simpler-Composite Closure

The rule that after the GWR-selected integer appears, the next prime endpoint arrives before any later composite with strictly lower divisor count can appear inside the same gap.

Threat Margin

For a proposed selected integer w, define the first later lower-divisor threat:

T_<(w) = min {m > w : d(m) < d(w)}

The threat margin is:

T_<(w) - q

A nonnegative margin means the inferred right prime endpoint arrives before the lower-divisor threat overtakes the selected integer.

6. Design Principle

The central design principle is:

Generate by inference. Validate by audit.

The generation path must remain free of classical primality testing. The validation path may use classical methods, but only after the generator has emitted inferred primes.

This preserves the conceptual distinction between:

* PGS inference: the novel deterministic generator mechanism.
* Classical validation: the external correctness audit.

7. Generator Contract

Given an anchor prime p, the generator attempts to produce an inferred next prime q_hat such that:

1. q_hat > p
2. All integers between p and q_hat are treated as inferred composite interior under the PGS chamber model.
3. The interior contains a GWR-compatible selected integer structure.
4. The inferred integer satisfies the active deterministic rule set.
5. No-later-simpler-composite closure holds under the active inference model.
6. The generator emits q_hat as a PGS-inferred prime.
7. The generator records sufficient metadata to reproduce the inference.

The generator must not call Miller-Rabin, trial division primality testing, or a classical sieve to decide whether q_hat is prime during generation.

8. Proposed Runtime Modes

8.1 Pure Inference Mode

The strict mode.

* No primality validation during generation.
* No candidate testing by Miller-Rabin or classical sieve.
* Emits inferred primes and inference metadata only.
* Classical validation is a separate later command or workflow.

This is the flagship mode.

8.2 Audit Mode

Runs PGS inference first, then validates the emitted list externally.

* Generation is still pure PGS inference.
* Validation is run afterward.
* Produces a confirmation report: confirmed / inferred.

This is the main benchmark mode.

8.3 Debug Mode

Allows optional classical checks during development, but only as diagnostic assertions.

* Not used for headline claims.
* Must be clearly marked as non-production research mode.
* Any classical feedback must not alter the inference rule unless the run is explicitly labeled as calibration or failure analysis.

9. Input

Minimum input:

* anchor_prime: known prime seed.
* count: number of inferred primes to generate.
* rule_set: selected deterministic PGS inference rule set.

Optional input:

* maximum search horizon,
* maximum chamber width,
* divisor-class budget,
* selected-integer-family restrictions,
* threat-margin reporting level,
* metadata verbosity,
* validation backend for post-generation audit.

10. Output

The generator emits a sequence of records.

Each record should include:

* step_index
* anchor_prime_p
* inferred_prime_q_hat
* inferred_gap_width
* winner_carrier_w
* winner_offset
* winner_divisor_count
* winner_family
* first_open_offset
* raw_z_log_score
* closure_status
* threat_margin, when computable
* rule_set_version
* inference_status
* failure_reason, if inference fails

In audit mode, append:

* classical_validation_status
* validation_backend
* validation_time
* validated_prime_bool
* first_failure_index, if any

11. Inference Strategy

The initial design should use the repo’s existing deterministic components in the following conceptual order:

1. Start from known prime p.
2. Build or scan the candidate chamber immediately to the right of p using PGS-compatible structure.
3. Identify admissible composite integers and their divisor classes.
4. Locate the earliest minimum-divisor integer according to GWR logic.
5. Use no-later-simpler-composite closure to infer the right endpoint before any later simpler composite threat.
6. Infer the next prime endpoint q_hat.
7. Emit q_hat and advance the anchor to q_hat.
8. Repeat.

This strategy may be refined into multiple inference engines, but all engines must obey the generation contract.

12. Candidate Engine Variants

12.1 Exact Recursive Walker Engine

Uses the repo’s exact recursive next-prime walk logic where available.

Best for:

* correctness-first development,
* low-to-mid-scale validation,
* proving the inference interface.

12.2 Bounded Walker Engine

Uses a bounded chamber rule such as a cutoff based on log-scale growth.

Best for:

* speed-oriented tests,
* scalability experiments,
* failure-bound discovery.

Must emit explicit failure if the inferred next prime cannot be uniquely resolved within the bound.

12.3 Threat-Margin Engine

Uses lower-divisor threat margins to infer safe closure of the chamber.

Best for:

* formalizing no-later-simpler closure,
* identifying endpoint cases,
* building the next theorem candidate.

12.4 Finite-State Surface Engine

Uses the reduced gap-type grammar and Semiprime Wheel Attractor as a stateful predictive layer.

Best for:

* long-run structure experiments,
* compressed symbolic inference,
* testing whether the reduced engine can support prime-endpoint inference rather than only gap-type modeling.

This should be treated as experimental until it achieves exact recovery benchmarks.

13. Correctness Levels

The project should distinguish these levels carefully:

Level 0: Structural Candidate

The number is generated by PGS structure but has not yet passed internal consistency checks.

Level 1: PGS-Inferred Prime

The number satisfies the active deterministic inference rule set and is emitted by the generator.

Level 2: PGS-Inferred + Internally Consistent

The inference record satisfies all available PGS metadata checks: GWR-selected integer, closure, threat-margin, and chamber consistency.

Level 3: Classically Validated Prime

The emitted inferred prime has been validated after generation by external classical methods.

Level 4: Certified Prime

The emitted inferred prime has a formal primality certificate from an accepted proof system.

Headline claims must clearly state which level is being reported.

14. Benchmark Plan

14.1 Exact Consecutive Walk Benchmark

Goal:

Measure whether the generator can infer consecutive primes from a small anchor without classical testing.

Method:

* Start from a known small prime, such as 11.
* Generate N inferred primes.
* Validate afterward.

Metrics:

* inferred count,
* validated count,
* first failure index,
* average inference time,
* median inference time,
* maximum chamber width,
* average chamber width,
* metadata completeness rate.

Success threshold:

* 100% validation over the committed exact development surface.

Failure signal:

* any inferred q_hat that is not the actual next prime after p.

14.2 Large-Anchor Spot Benchmark

Goal:

Test inference from large known anchors.

Method:

* Select validated anchor primes around 10^12, 10^14, 10^16, and 10^18.
* Infer the next K primes from each anchor.
* Validate afterward.

Metrics:

* validated recall,
* first failure index per anchor,
* inference time per step,
* chamber width,
* threat-margin distribution.

Success threshold:

* 100% validation across the selected committed anchor windows.

Failure signal:

* any missed or skipped prime endpoint.

14.3 Speed Benchmark Against Classical Generation

Goal:

Measure whether PGS inference can outperform classical candidate-test generation.

Method:

* Compare pure PGS inference plus after-the-fact validation against classical generation loops.
* Report generation time separately from validation time.

Metrics:

* pure inference time,
* validation time,
* total time,
* classical baseline time,
* speedup excluding validation,
* speedup including validation.

Important reporting rule:

The most important number is pure inference speed, but the honest deployment number includes validation unless the use case accepts inferred primes as research objects rather than certified primes.

15. Failure Handling

The generator must fail closed.

If the inference engine cannot identify a unique next prime, it must emit a structured failure rather than guessing.

Failure types:

* NO_UNIQUE_BOUNDARY
* CARRIER_NOT_FOUND
* CLOSURE_UNRESOLVED
* THREAT_MARGIN_NEGATIVE
* BOUND_EXCEEDED
* STATE_ENGINE_AMBIGUOUS
* INTERNAL_CONTRADICTION
* VALIDATION_FAILED, audit mode only

A failed inference is useful research data and should be saved as an artifact.

16. Artifact Requirements

Each benchmark run should produce:

* machine-readable JSON summary,
* per-step JSONL trace,
* failure examples, if any,
* validation report, if run,
* environment metadata,
* rule-set version,
* git commit hash,
* command-line invocation.

Recommended artifact paths:

* output/prime_inference_generator/
* docs/research/prime_inference_generator/
* benchmarks/python/prime_inference_generator/
* tests/python/test_prime_inference_generator.py

17. Naming

Possible names:

* PGS Prime Inference Generator
* PGS Recursive Prime Walker
* DNI-GWR Prime Inference Engine
* Structural Prime Inference Generator
* Prime Endpoint Inference Walker

Recommended public name:

PGS Prime Inference Generator

Recommended short internal name:

pgs-pig should be avoided despite being funny.

Better internal names:

* pgs_prime_infer
* prime_inference_walker
* dni_gwr_prime_walker

18. Claim Language

Recommended careful claim:

The PGS Prime Inference Generator emits primes by deterministic structural inference from the PGS rule set. Classical primality methods are used only afterward to validate the emitted sequence.

Avoid saying:

* “This proves primality instantly.”
* “This replaces all primality testing.”
* “This breaks RSA.”
* “This factors composites.”
* “This is cryptographically deployable without validation.”

Strong but defensible phrasing:

This separates prime generation from prime validation. The generator proposes the next prime endpoint from deterministic gap structure; classical methods then audit the generated stream.

19. Security Position

The generator should not be advertised as cryptographically safe until externally validated at the required certification level.

For cryptographic key generation, the safe deployment architecture is:

1. Use PGS inference to propose primes.
2. Validate every proposed prime with an accepted deterministic or probabilistic primality process required by the target standard.
3. Use only validated primes in cryptographic material.

The research breakthrough is in generation logic, not in bypassing security certification.

20. Open Questions

1. Can the exact recursive walker be converted into a generation-only interface with no hidden classical primality dependency?
2. What is the smallest deterministic metadata set needed to infer a unique next prime?
3. Does the bounded walker remain exact beyond the committed 10^7 surface?
4. Can threat-margin closure provide the formal bridge for large-scale inference?
5. Can the Semiprime Wheel Attractor help predict or compress inference steps without sacrificing exactness?
6. What is the first scale where inference becomes faster than classical candidate testing, excluding validation?
7. What is the first scale where inference remains faster including validation?
8. What are the endpoint cases where inference is ambiguous?

21. Smallest Useful MVP

The MVP should be intentionally narrow.

MVP Goal

Generate a consecutive list of PGS-inferred primes from a known anchor using no Miller-Rabin, no trial-division primality test, and no sieve-based generation inside the generator.

MVP Scope

* Start from a known small anchor prime.
* Generate a fixed number of inferred primes.
* Emit per-step inference metadata.
* Run classical validation only after the sequence is emitted.
* Report confirmed / inferred.

MVP Success Condition

100% validation over the selected committed exact surface.

MVP Failure Condition

The first emitted inferred prime that is not the actual next prime after its anchor.

22. Recommended Next Work Item

Create a research note and benchmark stub for:

PGS Prime Inference Generator MVP

The first artifact should not try to be cryptographic. It should prove the architecture:

* generation by PGS inference,
* validation afterward,
* clean separation of inference and certification,
* reproducible trace output,
* exact first-failure reporting.

The first successful milestone should be:

Starting from prime 11, PGS inferred the next N consecutive primes without classical primality testing in the generation loop; afterward, classical validation confirmed N/N outputs.

23. Final Design Summary

The PGS Prime Inference Generator is a new architecture for prime generation.

It does not test candidates for primality during generation.

It uses deterministic PGS rules to infer the next prime endpoint from gap-interior structure.

It emits inferred primes with complete inference traces.

It validates later using classical methods.

The core research claim is not that validation is unnecessary. The core claim is that prime generation itself can be reframed as deterministic structural inference rather than probabilistic candidate testing.
