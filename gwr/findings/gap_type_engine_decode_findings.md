# Gap-Type Model Decode Findings

The reduced grammar is now decoded far enough to separate what is already
model-like from what is still missing.

Three facts survive the stronger test surface:

- the persistent `14`-state reduced grammar is real;
- the **Semiprime Wheel Attractor** remains the dominant dynamical object;
- the current deterministic second-order rotor is not yet the whole hidden
  model, because it underproduces higher-order concentration at long
  horizons.

That is a strong result, not a retreat. The grammar generates the right
surface better than weaker baselines do, but the million-step stress test now
shows where the missing structure still lives.

## The Rulebook

The compact `12`-rule decode of the trained `10^7..10^17` core is:

1. `current_state not in Semiprime Wheel Attractor => next_state in Semiprime Wheel Attractor`
   Natural-language form: after any non-triad core state, the next state lands in the attractor with share `0.6752`.
2. `current_state family = higher_divisor_* => next_state in Semiprime Wheel Attractor`
   Natural-language form: higher-divisor states feed into the attractor with share `0.6701`.
3. `current_state family = even_semiprime => next_state in Semiprime Wheel Attractor`
   Natural-language form: even-semiprime states feed into the attractor with share `0.6836`.
4. `current_state in Semiprime Wheel Attractor => next_state in Semiprime Wheel Attractor`
   Natural-language form: once the walk is inside the attractor, it stays there with share `0.6552`.
5. `(o2_odd_semiprime|d<=4, o2_higher_divisor_even|5<=d<=16) => o4_odd_semiprime|d<=4`
   Natural-language form: when an `o2` attractor state is followed by a medium higher-divisor even intrusion, the next state returns to the `o4` odd-semiprime lane with share `0.5333`.
6. `(o4_odd_semiprime|d<=4, o4_higher_divisor_even|5<=d<=16) => o2_odd_semiprime|d<=4`
   Natural-language form: an `o4` higher-divisor-even excursion feeds back to the `o2` attractor lane with share `0.4800`.
7. `(o2_even_semiprime|d<=4, o4_odd_semiprime|d<=4) => o2_odd_semiprime|d<=4`
   Natural-language form: after an `o2` even-semiprime followed by the `o4` attractor lane, the walk returns to the `o2` attractor lane with share `0.4706`.
8. `(o6_odd_semiprime|d<=4, o2_higher_divisor_even|17<=d<=64) => o4_odd_semiprime|d<=4`
   Natural-language form: a large higher-divisor even interruption after the `o6` attractor lane still returns most often to the `o4` attractor lane, with share `0.4667`.
9. `(o4_odd_semiprime|d<=4, o4_higher_divisor_odd|5<=d<=16) => o2_odd_semiprime|d<=4`
   Natural-language form: odd higher-divisor intrusions in the `o4` lane most often feed back to the `o2` attractor lane, with share `0.4500`.
10. `(o4_odd_semiprime|d<=4, o6_higher_divisor_even|5<=d<=16) => o2_odd_semiprime|d<=4`
    Natural-language form: a medium higher-divisor-even detour after `o4` tends to re-enter through `o2`, with share `0.4444`.
11. `(o6_odd_semiprime|d<=4, o4_even_semiprime|d<=4) => o2_odd_semiprime|d<=4`
    Natural-language form: the `o6` attractor lane followed by an `o4` even-semiprime state returns to `o2` with share `0.4231`.
12. `(o4_higher_divisor_odd|5<=d<=16, o6_odd_semiprime|d<=4) => o4_odd_semiprime|d<=4`
    Natural-language form: once the walk exits an odd higher-divisor intrusion into the `o6` lane, it re-enters the attractor through `o4` with share `0.4211`.

The important structural fact is not any one row by itself. It is the repeated
pattern:

- non-triad states flow toward the triad;
- the triad retains the walk;
- the attractor lanes hand the walk back and forth in biased ways;
- intrusions are usually transient rather than autonomous.

## The Million-Step Stress Test

The current second-order rotor was trained on the persistent core from
`10^7..10^17` and then run for `1,000,000` synthetic gaps.

Against the real extreme-scale pool formed from sampled `10^12..10^18`
windows, the long walk settles to:

- family L1 distance `0.0692`;
- peak-offset L1 distance `0.1657`;
- higher-divisor share `0.2107` against real `0.1962`.

Those are stable and reasonably close.

The concentration story is sharper:

| Metric | Real extreme-scale pool | Synthetic `10^6` walk | Error |
|---|---:|---:|---:|
| one-step concentration | `0.3284` | `0.2849` | `0.0435` |
| two-step concentration | `0.5059` | `0.3345` | `0.1715` |
| three-step concentration | `0.7594` | `0.3478` | `0.4116` |

So the current rotor captures the vocabulary and the broad family balance, but
it does **not** preserve the real higher-order concentration surface at long
horizons.

That is the crucial stress-test result. The grammar is real, but the present
second-order rotor is still too diffuse.

The drift is visible across horizon checkpoints:

- by `16,384` steps the family and peak distributions have largely settled;
- by `262,144` steps those distribution errors are nearly stationary;
- the higher-order concentration keeps collapsing downward instead of staying
  near the real extreme-scale pool.

This means the missing ingredient is not the alphabet. It is the memory or
deterministic scheduling law acting on that alphabet.

## Record-Gap Probe

The record-gap test used a local extract of `387` known maximal-or-first
occurrence prime gaps with starts in `10^12..10^18`, taken from the Prime Gap
List and scored against the trained second-order grammar.

Of those records:

- `348` land inside the persistent `14`-state core;
- `39` land outside the core.

The control mean transition surprisal on the real sampled `10^12..10^18`
surface is `2.6266` bits.

The record subsets do **not** exceed that baseline on average:

| Subset | Count | Mean transition surprisal (bits) | Share above control mean |
|---|---:|---:|---:|
| all core records | `348` | `2.4415` | `0.3190` |
| maximal records | `22` | `2.2509` | `0.2727` |
| nonmaximal first occurrences | `326` | `2.4544` | `0.3221` |

So the record-gap verdict is currently negative:

- maximal gaps are **not** concentrated in the low-probability tails of the
  trained grammar;
- first-occurrence gaps are only slightly more surprising than maximal gaps,
  but still below the control mean on average.

The strongest rare-tail examples are not maximal gaps. They are first
occurrence gaps whose current reduced state is `even_semiprime`.

The top `20` most surprising core record gaps are all `even_semiprime`
arrivals.

So the present evidence says:

- record gaps are not rare because they force the grammar into exceptional
  transition paths;
- the current rare tails live more in specific even-semiprime arrival
  patterns than in maximal-gap status itself.

## Reading

This stage produces a clean split between what is already supported and what
must come next.

Supported:

- there is a persistent `14`-state grammar;
- the Semiprime Wheel Attractor is its dominant object;
- the grammar is generative, not merely descriptive.

Not yet supported:

- that the current second-order rotor is the full hidden model;
- that maximal gaps are explained as low-probability tails of that grammar.

The strongest next target is now obvious:

The alphabet appears to be right. The missing structure is the transition rule.

In practical terms, the next model candidate should preserve the same
`14`-state scaffold but tighten the long-horizon two-step and three-step
concentration surface. That is where the present rotor still leaks.

![Gap-type model decode overview](../../output/gwr_dni_gap_type_engine_decode_overview.png)
