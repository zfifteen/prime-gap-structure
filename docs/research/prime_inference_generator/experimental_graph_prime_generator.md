# Experimental Graph Prime Generator

## Status

The experimental graph prime generator is a generator-facing CLI for PGS graph
inference records. It is not production pure emission. It does not approve
cryptographic use. Classical validation is available only as a downstream
audit over already emitted records.

The default solver mode is `v6`, the safe repaired graph line. The quarantined
high-coverage line is exposed as `risky-v5` so its output and failures can be
measured explicitly. The filtered research line is exposed as `filtered-v5`.

## Command

```text
python3 benchmarks/python/prime_inference_generator/experimental_graph_prime_generator.py \
  --solver-version v6 \
  --start-anchor 11 \
  --max-anchor 100000 \
  --candidate-bound 128 \
  --witness-bound 127 \
  --audit \
  --print-dashboard \
  --output-dir output/prime_inference_generator
```

Supported solver versions:

```text
v3
v6
risky-v5
filtered-v5
```

`v6` is the default.

## Solver Modes

`v3` uses the accepted graph relations through the empty-source legal-carrier
extension relation. It is the broad safe baseline before the repaired v4 guard.

`v6` uses v3 plus:

```text
unresolved_later_domination_target_no_carrier_with_positive_nonboundary_guard
```

This is the safe repaired relation. It requires positive target non-boundary
evidence and does not run the old v4 or v5 absence-based propagation.

`risky-v5` runs the quarantined v5 line. It is exposed only for research
comparison. It includes the old v4 no-carrier/no-active-reset relation that
failed at anchor `10193` on the `11..100_000` surface.

`filtered-v5` runs the same internal risky-v5 solve, then applies a
label-free positive disqualification filter before emitting a record. It does
not emit when `inferred_prime_q_hat` has any of these positive nonboundary
certificates:

- bounded composite witness;
- power witness;
- certified divisor-class nonboundary certificate;
- wheel-closed status.

Filtered candidates are not written as inferred-prime records. They are
counted in the summary with:

```text
filter_status: FILTERED_POSITIVE_NONBOUNDARY_CANDIDATE
```

## Output Records

Each emitted JSONL record uses:

```text
record_type: PGS_INFERRED_PRIME_EXPERIMENTAL_GRAPH
production_approved: false
cryptographic_use_approved: false
audit_required: true
classical_audit_required: true
classical_audit_status: NOT_RUN
```

The inferred value is an experimental graph inference. It is not a production
prime-generation result.

## Summary Fields

The generator summary reports:

```text
solver_version
anchors_scanned
emitted_count
abstained_count
coverage_rate
audit_required
audit_confirmed
audit_failed
first_failure
filter_reason_counts
production_approved: false
cryptographic_use_approved: false
```

When `--audit` is supplied, the CLI also writes:

```text
experimental_graph_prime_generator_audit_summary.json
```

The audit checks first-boundary semantics: `inferred_prime_q_hat` must be the
first classical prime after `anchor_p`.

When `--print-dashboard` is supplied, the CLI prints the same generator-facing
run metrics to stdout:

```text
solver_version
anchors_scanned
emitted_count
abstained_count
coverage_rate
audit_confirmed
audit_failed
first_failure
```

## Generator Runs

Configuration:

```text
start_anchor: 11
max_anchor: 100000
candidate_bound: 128
witness_bound: 127
audit: enabled
```

Results:

```text
mode: v3
anchors_scanned: 9588
emitted_count: 216
confirmed_count: 216
failed_count: 0
coverage_rate: 0.02252816020025031
first_failure: null

mode: v6
anchors_scanned: 9588
emitted_count: 217
confirmed_count: 217
failed_count: 0
coverage_rate: 0.022632457238214436
first_failure: null

mode: risky-v5
anchors_scanned: 9588
emitted_count: 7391
confirmed_count: 6039
failed_count: 1352
coverage_rate: 0.7708594075928243
first_failure:
  anchor_p: 10193
  inferred_prime_q_hat: 10201
  first_prime_after_anchor: null

mode: filtered-v5
anchors_scanned: 9588
risky_input_count: 7391
filtered_count: 482
emitted_count: 6909
confirmed_count: 6039
failed_count: 870
coverage_rate: 0.7205882352941176
filter_reason_counts:
  bounded_composite_witness: 463
  power_witness: 25
first_failure:
  anchor_p: 17939
  inferred_prime_q_hat: 17947
  first_prime_after_anchor: null
```

The generator state is now explicit: v6 is safe and low-coverage on this
surface, while risky-v5 is high-coverage but fails downstream audit. The
filtered-v5 positive nonboundary filter blocks the known `10193 -> 10201`
square failure and the `10399 -> 10403` bounded semiprime failure. It still
fails audit and remains research-only.
