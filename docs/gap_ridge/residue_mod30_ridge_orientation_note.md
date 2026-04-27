# Residue-Modulated Ridge Orientation

This note records one arithmetic refinement of the raw composite near-endpoint peak
result.

The global ridge summary is true:

- the gap-local raw-`Z` maximum is usually near an edge,
- the left edge wins most often,
- the right edge wins in a smaller minority of gaps.

But that global summary averages over distinct arithmetic subfamilies.

## Finding

The orientation of the near-edge ridge depends materially on the residue class
of the left endpoint prime modulo `30`.

That left-endpoint label does not mention the gap interior, exact divisor
counts, or raw-`Z` values. Even so, it changes how often the right edge carries
the within-gap maximum.

In the tested regimes:

- some residue classes materially boost right-edge wins,
- some residue classes strongly suppress them,
- the pattern persists from exact `10^7` through sampled `10^18`,
- no tested residue class flips the global bias far enough to exceed twice the
  global right-edge share.

That is the current committed execution surface for this note.

So the correct reading is modulation, not inversion.

## Visual Evidence

The figure below groups prime gaps by the residue of the left prime modulo
`30`. The top row shows the right-edge win share for each residue class. The
dashed line is the global right-edge baseline at the same scale. The bottom row
shows the lift relative to that global baseline.

![Residue-modulated right-edge share](../../benchmarks/output/python/gap_ridge/insight_probes/residue_mod30_right_edge_share.svg)

The underlying probe artifacts are:

- [residue_mod30_right_edge_share.svg](../../benchmarks/output/python/gap_ridge/insight_probes/residue_mod30_right_edge_share.svg)
- [residue_mod30_right_edge_share.json](../../benchmarks/output/python/gap_ridge/insight_probes/residue_mod30_right_edge_share.json)

## Measured Surface

At exact `10^7`:

- global right-edge share: `16.02%`
- `p ≡ 13 (mod 30)`: right-edge share `24.08%`, lift `1.50x`
- `p ≡ 23 (mod 30)`: right-edge share `19.96%`, lift `1.25x`
- `p ≡ 11 (mod 30)`: right-edge share `9.95%`, lift `0.62x`
- `p ≡ 17 (mod 30)`: right-edge share `9.45%`, lift `0.59x`

At sampled `10^18`:

- global right-edge share: `15.93%`
- `p ≡ 13 (mod 30)`: right-edge share `21.82%`, lift `1.37x`
- `p ≡ 23 (mod 30)`: right-edge share `19.43%`, lift `1.22x`
- `p ≡ 11 (mod 30)`: right-edge share `11.09%`, lift `0.70x`
- `p ≡ 17 (mod 30)`: right-edge share `11.19%`, lift `0.70x`

The same residue classes that boost right-edge wins also show weaker
edge-distance-`2` concentration than the strongly left-dominant classes.

## Interpretation

The near-edge ridge is not one universal shape.

It is better described as a family of arithmetic subregimes indexed, at least
coarsely, by the left prime modulo `30`.

This does not mean the ridge flips into a right-dominant law for some tested
class. It means:

- the left-prime residue class shifts the orientation balance,
- the right-edge minority is not distributed uniformly across gaps,
- and a global ridge summary hides real arithmetic structure.

## Project Implications

For this repository, the immediate implication is conceptual and diagnostic.

The near-endpoint raw-Z peak concern should not be documented only through global aggregate
shares. Future notes and figures should separate:

- global ridge orientation,
- residue-conditioned ridge orientation.

This also introduces one very cheap predictor for future research probes:
`p mod 30`.

That predictor is not part of the normative prefilter contract and should not
be inserted into the deterministic production path without an explicit new
experiment. But it is a real organizing variable for the raw composite gap
ridge and therefore belongs in the research surface of the project.
