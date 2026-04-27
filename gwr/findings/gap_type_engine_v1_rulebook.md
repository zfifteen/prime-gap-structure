# GWR Gap-Type Model v1.0 Rulebook

The reduced model is now simple enough to state as a short rulebook.

These rules describe the frozen `v1.0` model on the persistent `14`-state
reduced gap-type surface. They are not meant to replace the exact transition
matrices. They are the readable laws that those matrices imply.

## Definitions

Three odd-semiprime lanes dominate the reduced stream:

- `o2_odd_semiprime|d<=4`
- `o4_odd_semiprime|d<=4`
- `o6_odd_semiprime|d<=4`

We call that triad the **Semiprime Wheel Attractor**.

The rules below are arranged from the fast core to the slow controller.

## Core Rules

1. **Finite alphabet**. The persistent reduced model closes to `14` states on
   the sampled `10^7..10^18` surface.
2. **Attractor definition**. The Semiprime Wheel Attractor is the triad
   `o2/o4/o6` odd-semiprime lanes at `d<=4`.
3. **Non-triad return law**. From any non-triad state, the next state lands in
   the attractor with share `0.6752`.
4. **Higher-divisor return law**. From any higher-divisor state, the next
   state lands in the attractor with share `0.6701`.
5. **Even-semiprime return law**. From any even-semiprime state, the next
   state lands in the attractor with share `0.6836`.
6. **Attractor retention law**. Once the walk is already inside the attractor,
   the next state stays inside it with share `0.6552`.
7. **`o2` to `o4` repair law**. After
   `(o2_odd_semiprime|d<=4, o2_higher_divisor_even|5<=d<=16)`, the next state
   is `o4_odd_semiprime|d<=4` with share `0.5333`.
8. **`o4` to `o2` repair law**. After
   `(o4_odd_semiprime|d<=4, o4_higher_divisor_even|5<=d<=16)`, the next state
   is `o2_odd_semiprime|d<=4` with share `0.4800`.
9. **Even-semiprime bridge law**. After
   `(o2_even_semiprime|d<=4, o4_odd_semiprime|d<=4)`, the next state is
   `o2_odd_semiprime|d<=4` with share `0.4706`.
10. **Large-intrusion repair law**. After
    `(o6_odd_semiprime|d<=4, o2_higher_divisor_even|17<=d<=64)`, the next
    state is `o4_odd_semiprime|d<=4` with share `0.4667`.
11. **Odd-intrusion repair law**. After
    `(o4_odd_semiprime|d<=4, o4_higher_divisor_odd|5<=d<=16)`, the next state
    is `o2_odd_semiprime|d<=4` with share `0.4500`.

## Scheduler Rules

12. **Lag-2 scheduler law**. A lag-2 finite scheduler is enough to cut the
    pooled-window concentration error to `0.0201`, which is the first clean
    closure of the higher-order gap beyond the plain second-order rotor.
13. **Periodic-state law**. A small periodic controller is real on this
    surface. The working hybrid uses cycle `8`, the best plain modulo cycle in
    the current reduced sweep is `11`, and the best higher-divisor reset cycle
    in that sweep is `2`.
14. **Local reset law**. Resetting the hybrid state when the walk leaves the
    attractor gives the current best local model,
    `hybrid_lag2_mod8_reset_nontriad_scheduler`, with pooled-window
    concentration L1 `0.0116`.

## Long-Horizon Controller Rules

15. **Higher-divisor event-lock law**. A higher-divisor-triggered event lock is
    the cleanest current long-horizon controller family. `L = 3` gives the
    best balanced operating profile with pooled-window concentration L1 `0.0150` and
    full-walk three-step `0.5564`. `L = 6` gives the best event-lock
    stationary profile with full-walk three-step `0.6278`.

## Reading

The model does not behave like a diffuse memoryless stream.

The readable picture is:

- the walk spends most of its time in the Semiprime Wheel Attractor;
- non-attractor states usually act as transient excursions;
- higher-divisor states are repair and reset events;
- a lag-2 plus periodic scheduler closes the short-window structure;
- higher-divisor-triggered locks sharpen the long-horizon walk.

That is the frozen rulebook for `v1.0`.
