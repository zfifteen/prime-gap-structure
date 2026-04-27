# Search Interval-Reset Probe: 10^8 Through 10^18

## Executive Summary

The search-interval-reset hypothesis closed the unresolved-tail gap on the decade
ladder.

Across the same `10^8` through `10^18` windows:

```text
input primes tested: 2816
old unique Rule X matches: 513
search-interval-reset exact matches: 2816
search-interval-reset false outputs: 0
candidate-bound misses: 0
tail cases converted: 2303
tail candidates excluded by reset: 77457
```

Every previously unresolved input prime had one resolved candidate followed by a
later unresolved tail. Under the search-interval-reset rule, the first resolved
remaining candidate closes the current search interval, so later unresolved candidates are
assigned to later search intervals and excluded from the current input prime's endpoint
choice.

## Tested Rule

For an input prime `p`, let `r` be the first resolved candidate under the
existing Rule X stack.

The tested search-interval-reset rule is:

```text
If r is resolved before any later unresolved candidate u,
then u is not a candidate next prime for p.

u belongs to a search interval beginning at r or later.
```

This changes the output rule from:

```text
output only if exactly one resolved candidate exists and no unresolved tail remains
```

to:

```text
output the first resolved candidate;
exclude later unresolved candidates as post-reset search-interval material
```

## Results By Decade

| decade | input primes | old matches | reset matches | false outputs | tail cases | tail candidates | seconds |
|---:|---:|---:|---:|---:|---:|---:|---:|
| `10^8` | `256` | `61` | `256` | `0` | `195` | `10416` | `0.335062` |
| `10^9` | `256` | `48` | `256` | `0` | `208` | `9744` | `0.472654` |
| `10^10` | `256` | `44` | `256` | `0` | `212` | `8049` | `0.799641` |
| `10^11` | `256` | `43` | `256` | `0` | `213` | `8225` | `1.012683` |
| `10^12` | `256` | `51` | `256` | `0` | `205` | `6687` | `1.437035` |
| `10^13` | `256` | `50` | `256` | `0` | `206` | `7139` | `1.767475` |
| `10^14` | `256` | `47` | `256` | `0` | `209` | `6065` | `2.489409` |
| `10^15` | `256` | `45` | `256` | `0` | `211` | `5209` | `3.555352` |
| `10^16` | `256` | `38` | `256` | `0` | `218` | `5691` | `4.748999` |
| `10^17` | `256` | `49` | `256` | `0` | `207` | `5291` | `7.148526` |
| `10^18` | `256` | `37` | `256` | `0` | `219` | `4941` | `12.189204` |

## Interpretation

The unresolved input primes were not missing the endpoint. They already contained
the endpoint as the first resolved candidate.

The previous output rule treated later unresolved candidates as competing
endpoints. The search-interval-reset test shows that this was too conservative in the
tested windows. Once the first resolved candidate appears, later unresolved
candidates are outside the current search interval and should not block output.

The measured effect is complete on this decade ladder:

```text
513 / 2816  -> old strict no-tail output
2816 / 2816 -> search-interval-reset output
```

No false outputs were observed.

## Artifacts

- Runner:
  [../run_chamber_reset_probe.py](../run_chamber_reset_probe.py)
- Aggregate summary:
  [summary.json](summary.json)
- Per-decade directories:
  [10e8](10e8/summary.json),
  [10e9](10e9/summary.json),
  [10e10](10e10/summary.json),
  [10e11](10e11/summary.json),
  [10e12](10e12/summary.json),
  [10e13](10e13/summary.json),
  [10e14](10e14/summary.json),
  [10e15](10e15/summary.json),
  [10e16](10e16/summary.json),
  [10e17](10e17/summary.json),
  [10e18](10e18/summary.json)
