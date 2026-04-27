# Lexicographic Winner-Take-All Peak Rule

This note records the strongest gap-ridge finding developed in this session.

## Finding

On the tested surface, the exact raw-$Z$ peak inside every tested prime gap is
identical to the leftmost minimizer:

1. choose the smallest interior divisor count $d(n)$,
2. if several interiors share that minimum divisor count, choose the leftmost
   one.

This is not an approximate summary on the tested surface. It is an exact match
in every tested regime.

## Validation Rule

The rule was evaluated with a direct counterexample search:

- validate on the tested surface if and only if every tested regime contains
  zero gaps where the exact raw-$Z$ peak differs from the leftmost minimizer,
- falsify immediately if even one such counterexample appears.

## Visual Evidence

![Lexicographic peak validation summary](../../benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation_summary.svg)

Artifacts:

- [lexicographic_peak_validation_summary.svg](../../benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation_summary.svg)
- [lexicographic_peak_validation.json](../../benchmarks/output/python/gap_ridge/lexicographic_peak_validation/lexicographic_peak_validation.json)
- [lexicographic_peak_validation.py](../../benchmarks/python/gap_ridge/lexicographic_peak_validation.py)

Additional probe figures:

- [lexicographic_rule_match_rate.svg](../../benchmarks/output/python/gap_ridge/insight_probes/lexicographic_rule_match_rate.svg)
- [lexicographic_rule_match_by_scale.svg](../../benchmarks/output/python/gap_ridge/insight_probes/lexicographic_rule_match_by_scale.svg)

## Tested Surface

The validation run found zero counterexamples in:

- exact `10^6`: `70,327 / 70,327`
- exact `10^7`: `605,597 / 605,597`
- sampled `10^8`: `444,133 / 444,133`
- sampled `10^9`: `411,157 / 411,157`
- sampled `10^10`: `384,721 / 384,721`
- sampled `10^11`: `362,773 / 362,773`
- sampled `10^12`: `344,454 / 344,454`
- sampled `10^13`: `328,342 / 328,342`
- sampled `10^14`: `315,617 / 315,617`
- sampled `10^15`: `303,475 / 303,475`
- sampled `10^16`: `293,408 / 293,408`
- sampled `10^17`: `283,989 / 283,989`
- sampled `10^18`: `275,466 / 275,466`

That list is the current committed execution surface.

The smallest observed score margin in log-score remained positive in every
tested regime, though it shrank with scale as expected.

## Plain Reading

The near-edge ridge is not only a visual field effect on the tested surface.

Its selected integer is fully determined by a simple arithmetic ordering rule:

- first minimize divisor count,
- then take the leftmost carrier of that minimum.

This gives one exact tested explanation for:

- $d(n)=4$ carrier dominance,
- left-edge dominance,
- and the frequent edge-distance-`2` peak.
