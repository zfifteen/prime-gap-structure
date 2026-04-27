# Large-Gap Margin Findings

This note records the executed large-gap surface extraction from
[`large_gap_margin_scan.py`](../experiments/proof/large_gap_margin_scan.py).

The target is narrow:

- record the worst realized no-early-spoiler margin inside each of the largest
  exact prime gaps on the current surface,
- and record the worst realized margin for each exact gap size.

This is the direct companion to the pair-frontier artifact. The pair frontier
identifies which divisor-class pairs get closest to the ratio-form threshold.
This large-gap artifact asks whether the largest actual prime gaps are where
the no-early-spoiler condition tightens.

## Executed Artifact

- [`large_gap_margin_scan_2e7.json`](../../output/gwr_proof/large_gap_margin_scan_2e7.json)

## Strongest Supported Result

On the exact through-$2 \cdot 10^7$ surface:

- `1163198` prime gaps have composite interior,
- `1054235` of those have at least one earlier candidate before the true
  `GWR` integer,
- the extractor records the top `100` largest such gaps exactly.

On that large-gap surface, the largest gaps do not lead the ratio-form
frontier.

The current frontier leaders already come from tiny gap-4 cases. The large-gap
surface therefore supports the same reading in a different coordinate system:

- the hardest realized ratio-form cases are not the largest prime gaps,
- and the largest prime gaps still retain positive no-early-spoiler margins
  against the true `GWR` integer.

The smallest realized critical-ratio margin among the top `100` largest gaps is
about `0.9999998973`, at the gap `(3851459, 3851587)` of length `128`, with:

- selected integer `3851473`,
- selected divisor-count class `d_{\min} = 4`,
- earlier candidate `3851467`,
- earlier class `d = 6`.

By contrast, the global gap-size frontier leader remains the gap-4 pair

$$ (d_{\min}, d(k)) = (30, 32). $$

with critical-ratio margin about `0.0714285168`.

So even the worst realized margin among the largest exact gaps sits far above
the current global frontier.

## Current Reading

This artifact is the exact gap-geometry companion to the ratio-frontier note.

Together the two executed surfaces say:

- the global ratio frontier is led by higher adjacent divisor-class pairs such
  as `(30, 32)`, `(15, 16)`, and `(22, 24)`,
- and those leaders are realized in tiny gap-4 configurations, not in the
  largest gaps on the current exact surface.

So the current exact evidence does not point to large gap length as the regime
where the no-early-spoiler condition becomes hardest.
