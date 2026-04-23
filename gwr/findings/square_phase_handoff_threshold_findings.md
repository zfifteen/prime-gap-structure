# Square-Phase Handoff Threshold Findings

The strongest supported claim from the new exact probe is:

On the full consecutive prime-gap surface through $10^6$, every gap that
contains an interior prime square hands the winner offset exactly to that
square's offset. When no interior prime square is present, the gap falls into
an early $d=4$ winner regime most of the time, but not always.

That is close to the structural handoff you proposed, but it sharpens the
scope in two important ways:

- the square branch is exact on this surface;
- the square-free branch is dominantly early $d=4$, not globally or literally
  "always semiprime with four divisors."

The probe script is
[`../../benchmarks/python/predictor/gwr_square_phase_handoff_threshold_probe.py`](../../benchmarks/python/predictor/gwr_square_phase_handoff_threshold_probe.py),
and the generated summary JSON is
[`./generated/square_phase_handoff_threshold_exact_1e6/gwr_square_phase_handoff_threshold_summary.json`](./generated/square_phase_handoff_threshold_exact_1e6/gwr_square_phase_handoff_threshold_summary.json).

![Square-phase handoff exact through 1e6](./generated/square_phase_handoff_threshold_exact_1e6/gwr_square_phase_handoff_threshold_offsets.png)

## Exact Through $10^6$ Surface

The probe scanned every consecutive prime gap with left prime $q \le 10^6$.
That produced `78,497` nonempty gaps.

On that exact surface:

- `168 / 168` square-present gaps had
  $$\text{winner offset} = \text{first interior prime-square offset};$$
- every one of those square-present winners had divisor class `d=3`;
- the square branch winner-offset distribution had median `6`, `p90 = 18`,
  `p99 = 38`, and maximum `48`;
- after the interior square appears, the gap closes soon after on this
  surface: the remaining distance from the square to the right prime had
  median `10`, `p90 = 24`, and maximum `52`.

So the square branch is not merely "influenced" by the square. On this exact
surface it is locked to the first interior prime square.

## What Happens When No Square Is Present

Among the `78,329` square-free gaps:

- `58,305` had winner class `d=4`, which is `74.44%` of the square-free
  surface;
- those square-free `d=4` winners arrived early, with median offset `3`,
  `p90 = 6`, `p99 = 10`, and maximum `22`;
- among those `d=4` winners, the family split was:
  `45,268` odd semiprimes,
  `13,030` even semiprimes,
  `7` prime cubes.

So the square-free branch is strongly concentrated in the early `d=4` regime,
and the odd-semiprime lane is its largest family. But the stricter sentence

> before a square appears in the interior, the winner is always a semiprime
> with four divisors

is too strong on this exact surface.

There are two separate reasons:

- `20,024` square-free gaps had winner class other than `d=4`;
- even inside the square-free `d=4` branch, the winner is not always an odd
  semiprime.

The right repo-safe version is:

- if an interior prime square appears, the winner offset locks to it;
- if no interior prime square appears, the dominant branch is an early `d=4`
  winner, usually but not exclusively an odd semiprime.

## What The Figure Says

The right-hand panel is the clean part: every square-present row sits on the
diagonal, so the winner offset and square offset coincide exactly on the full
through-$10^6$ surface.

The left-hand panel is more nuanced. It does show a split in shape:

- square-free `d=4` winners are packed tightly near the left prime;
- square-present winners have a longer late-offset tail.

But it is not yet a clean unconditional two-peak histogram. The square-present
branch is only about `0.214%` of all nonempty gaps on this surface, and many
of its offsets still overlap the early `d=4` band.

So the strongest exact conclusion is not "winner offset alone detects square
presence." It is:

- the local square clock determines the winner exactly when it fires;
- otherwise the dominant survivor law is early `d=4` arrival.

## Better Theorem Target

The promising next claim is not a universal scalar cutoff on winner offset.
The better target is a branch law:

1. if the gap contains an interior prime square at offset $s$, then the winner
   offset is exactly $s$;
2. if the gap contains no interior prime square, then the dominant winner
   branch is early `d=4` arrival.

Attached to your actual scope, that is where the novelty looks strongest.
It turns the square branch from a loose influence story into an exact local
handoff law, while keeping the square-free branch stated at the level the data
actually support.
