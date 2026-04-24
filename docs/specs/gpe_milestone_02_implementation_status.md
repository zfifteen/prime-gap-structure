# GPE Milestone 2 Implementation Status

The current implementation exposes the dominant $d(w)=4$ NLSC ceiling as a
branch validation surface, not as a completed selector theorem.

For one exact oracle row, the implemented surface records:

- current prime $q$,
- GWR winner $w$,
- winner divisor class $d(w)$,
- exact right boundary $q^+$ from the existing oracle,
- the branch horizon $S_{+}(w)$ when $d(w)=4$,
- the square-ceiling margin $S_{+}(w)-q^+$,
- and square-phase utilization $(q^+-w)/(S_{+}(w)-w)$ as a measured ratio.

The implementation lives in
[`../../src/python/z_band_prime_predictor/gpe_nlsc_selector.py`](../../src/python/z_band_prime_predictor/gpe_nlsc_selector.py).

## Current Deterministic Path

For $d(w)=4$, the row builder computes the validation horizon
$S_{+}(w)$ using the existing arithmetic definition of the next prime-square
threat. The branch selector then checks one straight-line contract:

$$q^+=S_{+}(w)-M_{\square},$$

where $M_{\square}=S_{+}(w)-q^+$ is the explicit selector-state
square-ceiling margin. The selector also verifies:

$$w<q^+<S_{+}(w).$$

If $M_{\square}$ is absent, the selector fails explicitly. The NLSC ceiling
alone is not treated as an exact emission rule, and the $d=4$ branch no longer
uses the generic left-boundary offset as its selector state.

The implementation also exposes an executable branch-target audit:

[`../../src/python/z_band_prime_predictor/gpe_nlsc_selector.py`](../../src/python/z_band_prime_predictor/gpe_nlsc_selector.py)
defines `audit_nlsc_branch_targets(...)`, which groups an oracle validation
surface by observed $d(w)$ and reports whether each branch has an exact selector
law or an explicit unresolved target. It also defines
`audit_d4_square_margin_collisions(...)`, which groups $d(w)=4$ rows by a
proposed reduced state key and reports keys that map to multiple
square-ceiling margins. On the focused branch smoke surface
`q in {3, 5, 11, 29}`, the observed classes are:

| $d(w)$ | Current status |
|---:|---|
| $3$ | unresolved target: define exact $B_3(q,S,w)$ |
| $4$ | ceiling and guarded selector surface exist; unresolved target: derive $M_{\square}=S_{+}(w)-q^+$ from rulebook state |
| $6$ | unresolved target: define exact $B_6(q,S,w)$ |
| $8$ | unresolved target: define exact $B_8(q,S,w)$ |

On the known reduced-state collision row pair `q in {13, 73}`, the margin audit
groups both rows under `(q mod 30, d(w), w-q) = (13, 4, 1)` and reports two
different square-ceiling margins: `8` and `42`. Therefore this reduced key is
not a $d=4$ margin selector.

## Validated Rows

The focused tests validate the first dominant branch examples and one non-floor
margin-`6` row:

| $q$ | $w$ | $d(w)$ | $q^+$ | $S_{+}(w)$ | $M_{\square}$ |
|---:|---:|---:|---:|---:|---:|
| $13$ | $14$ | $4$ | $17$ | $25$ | $8$ |
| $73$ | $74$ | $4$ | $79$ | $121$ | $42$ |
| $27851$ | $27857$ | $4$ | $27883$ | $27889$ | $6$ |

The non-$d(w)=4$ row $q=23$ remains an explicit unresolved branch target:

| $q$ | $w$ | $d(w)$ | $q^+$ |
|---:|---:|---:|---:|
| $23$ | $25$ | $3$ | $29$ |

## Current Catalog Obstruction

The committed catalog at
[`../../output/gwr_dni_gap_type_catalog_details.csv`](../../output/gwr_dni_gap_type_catalog_details.csv)
contains `81,569` rows. Its observed winner classes include many non-$4$
branches, and its $d(w)=4$ surface contains `60,726` rows.

On that surface, reduced $d(w)=4$ type keys are not boundary selectors. For
example, `o4_d4_a1_even_semiprime` maps to multiple exact gap widths, including
`4`, `6`, `10`, `16`, `12`, `24`, `18`, `22`, `30`, and `28` among its most
common observed targets. The exact selector therefore cannot be the existing
reduced type plus the NLSC ceiling.

## Remaining Milestone 2 Requirement

Milestone 2 is not complete. The unmet requirement is the exact d=4 branch law:

$$B_4(q,S,w)=q^+.$$

The current code proves only that the validation row is inside the NLSC horizon.
It does not yet derive $M_{\square}=S_{+}(w)-q^+$ from rulebook state. The
next highest-leverage step is to split the live $d=4$ rows by square-ceiling
margin state and prove or report the first unresolved collision family.

The nearest existing branch fact is the square-residue dead zone recorded in
[`../findings/d4_square_residue_dead_zone.md`](../findings/d4_square_residue_dead_zone.md):
after the floor package $q^+=S_{+}(w)-2$ fails on the live earliest-$d=4$
semiprime branch, $S_{+}(w)-4$ is wheel-forbidden, and the first admissible
non-floor margin splits by $S_{+}(w) \bmod 30$. That fact narrows the branch,
but it still does not select the deeper tail boundary in every row.
