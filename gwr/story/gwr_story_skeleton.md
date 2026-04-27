# Gap Winner Rule Story Skeleton

## Working Title

**The Gap Winner Rule: how a geometric-looking score collapsed to a simple arithmetic law**

## Purpose

This document is the narrative scaffold for the long-form `GWR` story. It is
not the final polished essay. Its job is to fix the section order, the main
claims of each section, and the figures each section needs.

## Core Narrative

The story should move in this order:

1. start from the raw-$Z$ score inside prime gaps,
2. describe the original visual impression: a near-edge ridge,
3. present the surprise: the winner collapses to a simple arithmetic rule,
4. show that this one rule explains several separate-looking phenomena,
5. show the theorem temptation and the correction,
6. end on the bridge certificate that closes the main mathematical question
   under the recorded constants.

## Section Plan

## 1. The Starting Object

### Purpose

Introduce the raw-$Z$ score in plain language without opening with formalism.

### Main claim

We began with a score on composite interiors of prime gaps that looked like a
 mixed geometric-arithmetic object, not like a lexicographic ordering rule.

### Points to cover

- prime gaps have composite interiors,
- each interior composite gets a raw-$Z$ score,
- the original visual effect looked like a near-edge ridge rather than a
  discrete winner law.

### Figure needs

- one introductory exemplar gap plot showing raw-$Z$ across the interior of a
  prime gap,
- winner highlighted.

## 2. What The Score Seemed To Be Doing

### Purpose

Show the original intuition before the collapse.

### Main claim

At first the score looked like it was balancing divisor structure and position
inside the gap in a smooth way.

### Points to cover

- raw-$Z$ depends on both $d(n)$ and $\ln(n)$,
- visually the winner often sits near the left edge,
- this initially looks like a geometric field effect rather than a simple law.

### Figure needs

- a small panel of exemplar gaps at different scales,
- optional divisor-color overlay to show low-`d` carriers.

## 3. The Surprise: The Winner Collapses

### Purpose

State `GWR` cleanly and early as the central surprise.

### Main claim

On the tested prime-gap surface, and under the recorded BHP/Robin bridge
closure, the raw-$Z$ winner is always the same as the minimum-divisor leftmost
winner.

### Points to cover

- define `Gap Winner Rule (GWR)`,
- explain “minimum divisor count, then leftmost” in ordinary language,
- state the zero-counterexample validation surface.

### Figure needs

- identity plot of raw-$Z$ winner versus GWR winner,
- match-rate-by-regime summary plot.

## 4. One Rule, Several Consequences

### Purpose

Show that `GWR` compresses multiple previously separate observations.

### Main claim

$d(n)=4$ dominance, left-edge dominance, and edge-distance-$2$ enrichment are
not separate mysteries on the tested surface. They are consequences of the same
winner law.

### Points to cover

- winner divisor histogram versus baseline interior histogram,
- normalized winner position versus baseline,
- edge-distance distribution versus baseline.

### Figure needs

- divisor-count enrichment plot,
- normalized winner-position plot,
- edge-distance plot.

## 5. The Stronger Theorem We Wanted

### Purpose

Tell the mathematically honest version of the next step.

### Main claim

The first natural guess was a broad global theorem for arbitrary composite
pairs, but that stronger unrestricted statement is false.

### Points to cover

- explain the temptation: perhaps raw-$Z$ is globally lexicographic on
  composites,
- show the explicit counterexample,
- explain why this does not damage `GWR`.

### Figure needs

- possibly no plot,
- maybe one tiny comparison table or schematic for the counterexample pair.

## 6. The Exact Statement That Survives

### Purpose

Introduce the narrower dominance theorem cleanly.

### Main claim

What survives is an ordered-direction dominance statement: earlier composite
plus no larger divisor count implies larger raw-$Z$.

### Points to cover

- state the `Lexicographic Raw-Z Dominance Theorem`,
- explain why prime squares matter for the endpoint,
- connect the theorem to the prime-gap corollary carefully.

### Figure needs

- optional theorem-support plot or schematic,
- possibly none if prose is clearer.

## 7. The Bridge Certificate

### Purpose

End with the proof closure, not only the validation surface.

### Main claim

The exact finite scan becomes the base case for the proved universal GWR
theorem.

### Points to cover

- GWR was empirically exact on the tested surface before proof closure,
- the unrestricted global theorem is false,
- the ordered dominance theorem handles the later side,
- the bridge certificate handles the earlier side under the recorded
  BHP/Robin constants.

### Figure needs

- a gap-level map or heatmap showing winner concentration by normalized position
  and divisor count.

## Proposed Plot Inventory

These are the initial figures to generate after the skeleton is approved.

1. `figure_01_exemplar_gap_profiles`
   Raw-$Z$ profiles for selected prime gaps with raw-$Z$ and GWR winners marked.

2. `figure_02_winner_identity`
   Raw-`Z` winner versus GWR winner identity check.

3. `figure_03_match_rate_surface`
   Match rate by tested regime with annotations for gap counts.

4. `figure_04_divisor_enrichment`
   Winner divisor-count histogram or enrichment versus baseline.

5. `figure_05_normalized_position`
   Winner normalized position versus baseline interior positions.

6. `figure_06_edge_distance`
   Winner edge-distance distribution versus baseline.

7. `figure_07_counterexample_pair`
   Small schematic or table for the unrestricted-theorem counterexample.

8. `figure_08_winner_heatmap`
   Winner concentration in `(normalized position, divisor count)` space.

## Writing Standard

When this becomes the full story document:

- begin sections with observable facts before formal interpretation,
- use `Gap Winner Rule` / `GWR` as the forward name,
- retain the legacy name only where continuity matters,
- separate theorem-backed statements from empirical robustness statements,
- do not let caution bury the strongest supported finding,
- keep the prose calm and declarative.
