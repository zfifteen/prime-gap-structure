# Gap-Type Generative Grammar Findings

The first generative test is positive.

A deterministic second-order rotor machine trained on the persistent
`14`-state reduced grammar from sampled `10^7..10^17` windows generates a
held-out `10^18` prefix more faithfully than weaker baselines do.

The object tested here is the reduced state
`open_family|d_bucket`, where the divisor buckets are:

- `d<=4`
- `5<=d<=16`
- `17<=d<=64`
- `d>64`

The training surface is restricted to contiguous segments that remain inside
the persistent `14`-state core. That keeps the generator honest: it is tested
as a grammar on the settled high-scale vocabulary, not on transient spillover
states.

## Main Result

Three deterministic emitters were trained on the same `10^7..10^17` core
surface and judged on the held-out `10^18` window:

- `iid_balanced_cycle`: no state memory, only the reduced-state frequency table;
- `first_order_rotor`: one-step memory on the reduced state;
- `second_order_rotor`: two-step rotor grammar on the reduced state.

On the held-out `10^18` window, the second-order grammar is the strongest
model:

| Model | state L1 | pair L1 | family L1 | peak-offset L1 | triad-share error | pair-top error | max-peak error |
|---|---:|---:|---:|---:|---:|---:|---:|
| `iid_balanced_cycle` | `0.2422` | `0.7059` | `0.2031` | `0.4219` | `0.0742` | `0.0353` | `6` |
| `first_order_rotor` | `0.2656` | `0.5569` | `0.1953` | `0.4219` | `0.0664` | `0.0510` | `6` |
| `second_order_rotor` | `0.2344` | `0.4627` | `0.1172` | `0.3594` | `0.0234` | `0.0078` | `2` |

The largest gain is where the grammar claim actually lives:

- reduced-state pair structure improves from `0.7059` and `0.5569` to `0.4627`;
- odd-semiprime triad share error falls from `0.0742` and `0.0664` to `0.0234`;
- family-share error falls from `0.2031` and `0.1953` to `0.1172`;
- the held-out pair-top concentration `0.3412` is matched closely by
  `0.3333`;
- the held-out maximum emitted peak offset `30` is approximated by `32`.

So the `14`-state grammar is not only descriptive. It already carries enough
information to generate a held-out high-scale window more faithfully than
weaker memory baselines do.

## The First 10,000 Synthetic Gaps

The second-order rotor was then run for `10,000` synthetic rows.

That walk:

- stays inside the `14`-state persistent core for the full run;
- keeps the odd-semiprime triad dominant at share `0.6586`;
- reaches emitted peak offset `50`;
- concentrates most heavily on the three odd-semiprime core states:
  `o2_odd_semiprime|d<=4`, `o4_odd_semiprime|d<=4`,
  `o6_odd_semiprime|d<=4`.

The top six reduced states on the `10,000`-step synthetic walk are:

| Reduced state | Share |
|---|---:|
| `o2_odd_semiprime|d<=4` | `0.2576` |
| `o4_odd_semiprime|d<=4` | `0.2415` |
| `o6_odd_semiprime|d<=4` | `0.1595` |
| `o4_even_semiprime|d<=4` | `0.0565` |
| `o4_higher_divisor_even|5<=d<=16` | `0.0441` |
| `o6_even_semiprime|d<=4` | `0.0417` |

## Human-Readable Grammar Rules

The trained core already compresses into readable transition laws.

On the `10^7..10^17` training surface:

1. After any non-triad core state, the next state lands in the odd-semiprime
   triad with share `0.6752`.
2. After any higher-divisor core state, the next state lands in the triad with
   share `0.6701`.
3. After any even-semiprime core state, the next state lands in the triad with
   share `0.6836`.
4. Once the walk is inside the triad, it stays inside the triad with share
   `0.6552`.
5. `o2_higher_divisor_even|5<=d<=16 -> o4_odd_semiprime|d<=4` is the strongest
   single row rule, with share `0.5490`.
6. `o2_higher_divisor_even|17<=d<=64 -> o4_odd_semiprime|d<=4` occurs with
   share `0.4459`.
7. `o4_higher_divisor_even|5<=d<=16 -> o2_odd_semiprime|d<=4` occurs with
   share `0.4180`.
8. `o2_higher_divisor_even|d>64 -> o6_odd_semiprime|d<=4` occurs with share
   `0.3462`.
9. `o4_higher_divisor_odd|5<=d<=16 -> o2_odd_semiprime|d<=4` occurs with
   share `0.3370`.
10. `o6_higher_divisor_odd|5<=d<=16 -> o2_odd_semiprime|d<=4` occurs with
    share `0.3125`.

## The Attractor

The triad

- `o2_odd_semiprime|d<=4`
- `o4_odd_semiprime|d<=4`
- `o6_odd_semiprime|d<=4`

is the dominant dynamical object on this surface.

This note uses the working name **Semiprime Wheel Attractor** for that triad.

That name is justified by the measured transition law:

- non-triad states return to it with share `0.6752`;
- higher-divisor states feed into it with share `0.6701`;
- even-semiprime states feed into it with share `0.6836`;
- once entered, it retains the walk with share `0.6552`.

This is not yet a proof of a global attractor theorem. It is the correct
working object for the next theorem-facing pass.

## Reading

The strongest supported claim from this probe is:

The persistent `14`-state grammar is already generative enough to beat weaker
deterministic baselines on a held-out `10^18` window.

That is not the final theorem. It is the first nontrivial generative success.

The next step should not be another descriptive catalog. The next step is to
stress-test whether the second-order rotor law, or a nearby finite-memory law,
continues to reproduce later-regime statistics when trained strictly below the
target decade.

![Gap-type generative grammar probe overview](../../output/gwr_dni_gap_type_generative_probe_overview.png)
