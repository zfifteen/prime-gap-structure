# Chamber-Reset Probe: 10^8 Through 10^18

## Executive Summary

The chamber-reset hypothesis closed the unresolved-tail gap on the decade
ladder.

Across the same `10^8` through `10^18` windows:

```text
anchors tested: 2816
old unique Rule X matches: 513
chamber-reset exact matches: 2816
chamber-reset false emissions: 0
candidate-bound misses: 0
tail cases converted: 2303
tail candidates excluded by reset: 77457
```

Every previously unresolved anchor had one resolved survivor followed by a
later unresolved tail. Under the chamber-reset rule, the first resolved
survivor closes the current chamber, so later unresolved candidates are
assigned to later chambers and excluded from the current anchor's boundary
choice.

## Tested Rule

For an accepted anchor `p`, let `r` be the first resolved survivor under the
existing Rule X stack.

The tested chamber-reset rule is:

```text
If r is resolved before any later unresolved candidate u,
then u is not a candidate boundary for p.

u belongs to a chamber beginning at r or later.
```

This changes the emission rule from:

```text
emit only if exactly one resolved survivor exists and no unresolved tail remains
```

to:

```text
emit the first resolved survivor;
exclude later unresolved candidates as post-reset chamber material
```

## Results By Decade

| decade | anchors | old matches | reset matches | false emits | tail cases | tail candidates | seconds |
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

The unresolved anchors were not missing the boundary. They already contained
the boundary as the first resolved survivor.

The previous emission rule treated later unresolved candidates as competing
boundaries. The chamber-reset test shows that this was too conservative in the
tested windows. Once the first resolved survivor appears, later unresolved
candidates are outside the current chamber and should not block emission.

The measured effect is complete on this decade ladder:

```text
513 / 2816  -> old strict no-tail emission
2816 / 2816 -> chamber-reset emission
```

No false emissions were observed.

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
