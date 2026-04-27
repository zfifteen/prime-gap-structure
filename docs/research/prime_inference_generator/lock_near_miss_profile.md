# Higher-Divisor Pressure Lock Near-Miss Profile

The higher-divisor pressure lock abstains mostly because the required
higher-divisor pressure component is absent. The strongest substitute signal in
the abstention set is previous-search-interval memory.

This note profiles abstentions from Next-Prime Law 005 Candidate. It does not
approve a new lock family and does not approve pure generator output.

## Status

Current status:

- Next-Prime Law 005: preserved as a candidate law.
- Pure generator output: forbidden.
- Milestone 1: blocked for generator output.
- Probe role: offline near-miss profiling only.

The profile targets rows where:

```text
true next prime is resolved
later unresolved alternatives remain
higher_divisor_pressure_lock does not activate
```

The run used:

```text
surfaces:
  11..1_000_000
  100_000..200_000
  1_000_000..1_100_000
candidate_bound: 64
witness_bound: 97
single_hole_positive_witness_closure: enabled
carrier_locked_pressure_ceiling: enabled
carrier_lock_predicate: unresolved_alternatives_before_threat
```

## Headline Result

The profile found `58696` near-miss rows.

The dominant reason is exact and uniform:

```text
missing_higher_divisor_pressure: 58696 / 58696
```

The strongest substitute signal is:

```text
previous_chamber_signal: 43219
```

The best next lock-family candidate by raw support is:

```text
previous_chamber_reset_lock
```

This is a profiling result only. It does not mean the previous-search-interval signal
is selective or safe.

## Surface Summary

| Surface | Rows | Near misses |
|---|---:|---:|
| `11..1_000_000` | `78494` | `48988` |
| `100_000..200_000` | `8392` | `5540` |
| `1_000_000..1_100_000` | `7216` | `4168` |

The shifted windows contribute substantial near-miss rows even though the
higher-divisor pressure lock itself did not activate there.

## Near-Miss Reason Counts

| Reason tag | Count |
|---|---:|
| `missing_higher_divisor_pressure` | `58696` |
| `carrier_not_in_eligible_family` | `58506` |
| `no_resolved_false_survivor_pair` | `48319` |
| `previous_chamber_signal_present` | `43219` |
| `no_carrier_lock_signature` | `15403` |
| `semiprime_pressure_instead_of_higher_divisor_pressure` | `129` |
| `square_pressure_instead_of_higher_divisor_pressure` | `10` |
| `wrong_pressure_location` | `5` |
| `pressure_appears_after_unresolved_alternative` | `3` |

The selected-integer-family result is important. Most near-misses do not have the same
integer regime as the activating Next-Prime Law 005 cases. Many are resolved at
small offsets before a legal integer exists in the search interval.

## Pressure Substitute Counts

| Substitute signal | Count |
|---|---:|
| `previous_chamber_signal` | `43219` |
| `no_pressure_substitute` | `15403` |
| `carrier_extension_change` | `620` |
| `reset_evidence` | `130` |
| `semiprime_pressure` | `129` |
| `square_pressure` | `10` |
| `higher_divisor_wrong_location` | `5` |

The near-miss set is not dominated by square pressure or semiprime pressure.
Those appear, but their support is narrow.

## Candidate Adjacent Lock Families

The profiler ranks adjacent lock families by observed substitute support:

| Candidate family | Supporting signal | Support count |
|---|---|---:|
| `previous_chamber_reset_lock` | `previous_chamber_signal` | `43219` |
| `carrier_extension_absorption_lock` | `carrier_extension_change` | `620` |
| `reset_evidence_lock` | `reset_evidence` | `130` |
| `semiprime_wheel_lock` | `semiprime_pressure` | `129` |
| `square_pressure_lock` | `square_pressure` | `10` |
| `higher_divisor_location_lock` | `higher_divisor_wrong_location` | `5` |

The support order does not establish safety. It only identifies which signal
should be tested first under the zero-wrong separator standard.

## Interpretation

The near-miss profile supports four facts:

1. The higher-divisor lock abstains because the required pressure component is
   absent, not because the true next prime is usually unresolved.
2. Previous-search-interval memory is present in most abstaining true-next-prime rows.
3. Most abstentions are outside the activating selected-integer-family regime.
4. Square and semiprime pressure are real but sparse in this near-miss set.

The next candidate should not be a broad version of Next-Prime Law 005. The next
test should isolate previous-search-interval memory as a lock separator and ask whether
it selects true resolved endpoints without selecting false resolved candidates.

## Next Gate

The next offline probe should test:

```text
previous_chamber_reset_lock
```

against the same zero-wrong gate:

```text
false_locked_count == 0
true_locked_count > 0
```

If previous-search-interval memory selects false resolved candidates, it is rejected as
nonselective. If it passes, it becomes an adjacent candidate lock family. Until
then, it is only the best next family by near-miss support.

The pure generator remains fail-closed.
