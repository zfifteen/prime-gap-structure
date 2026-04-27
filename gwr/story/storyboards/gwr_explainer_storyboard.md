# GWR Explainer Static Storyboard

Working title: **The Gap Winner Rule Inside a Prime Gap**

This storyboard is a static mockup pass only. It does not request Manim rendering
and does not create video assets.

Visual style: dark technical background, integer blocks on a number line, warm
highlight for the selected integer, cyan scan accents, and sparse labels. The
audience should see the arithmetic happening before the formal name appears.

Static storyboard sheet:

![GWR explainer storyboard sheet](./gwr_explainer_storyboard_sheet.svg)

## Scene 1 - A Prime Gap And Its Interior

Observable state:

The left endpoint is the prime $p = 23$. The right endpoint is the next prime
$q = 29$. The interior integers $24,25,26,27,28$ are the composite integers
inside this prime gap.

Screen action:

The block at $23$ locks as the left endpoint. A bracket opens over $24..28$.
The endpoint primes stay visually distinct; the interior composite integers
become available for inspection.

Narration intent:

"Start with two consecutive primes. The integers between them are all
composite. GWR compares those interior composites."

## Scene 2 - Divisor Counts On The Interior

Observable state:

Each interior integer receives its exact divisor count:

| n | 24 | 25 | 26 | 27 | 28 |
|---|---:|---:|---:|---:|---:|
| d(n) | 8 | 3 | 4 | 4 | 6 |

Screen action:

The blocks lift into small columns. The label above each block changes from
integer-only to $d(n)$. Larger divisor counts appear lower and dimmer; lower
divisor counts remain visually available.

Narration intent:

"Inside a prime gap, every interior integer is composite. The measured quantity
is the divisor count $d(n)$."

## Scene 3 - Minimum Divisor Count

Observable state:

The minimum divisor count is $3$, attained at $25$.

Screen action:

A horizontal threshold line drops to $d(n)=3$. Blocks with larger divisor count
fade into the background. The block $25$ receives the selected-integer color.

Narration intent:

"GWR first chooses the smallest divisor count among the interior composites."

## Scene 4 - Leftmost Tie Rule

Observable state:

Use the gap $89..97$:

| n | 90 | 91 | 92 | 93 | 94 | 95 | 96 |
|---|---:|---:|---:|---:|---:|---:|---:|
| d(n) | 12 | 4 | 6 | 4 | 4 | 4 | 12 |

The minimum divisor count is $4$, with a tie at $91,93,94,95$. GWR selects
$91$ because it is the leftmost minimizer of $d(n)$.

Screen action:

All $d(n)=4$ blocks light in cyan. A scan cursor moves left to right and stops
at $91$. The later tied minimizers stay marked but unselected.

Narration intent:

"If several interior composites share the minimum divisor count, GWR takes the
first one from left to right."

## Scene 5 - Raw-Z Winner Collapses Onto GWR

Observable state:

The raw-$Z$ score is

$$Z_{\mathrm{raw}}(n) = n^{1 - d(n)/2}.$$

Because the logarithm is order-preserving, the implemented comparison can use

$$L(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).$$

For the prime gap from $23$ to $29$, the score winner is the same block selected
by GWR: $25$.

Screen action:

A score curve rises over the gap interior. The peak marker lands on the same
gold block already selected by GWR. The equation appears as a compact caption,
not as the first visual element.

Narration intent:

"The surprise is not that the score often leans left. The surprise is that the
score winner is the same integer selected by this discrete rule."

## Scene 6 - Interior Winner Versus Next Prime

Observable state:

GWR selects an interior composite integer. That selected interior integer is not
automatically the next prime. The identity $q = w + 1$ is not a general rule.

Screen action:

The selected interior integer remains gold. The next prime endpoint remains a
separate marked block at the right. A short caption says: "interior winner is
not the prime endpoint."

Narration intent:

"GWR is a rule about the interior composites of a prime gap. It identifies an
interior winner; it does not by itself say that the next prime is one more than
that winner."

## Flaming Horse Notes

The corresponding Flaming-Horse-shaped plan draft is
[`gwr_explainer_plan.json`](./gwr_explainer_plan.json). It stays at the plan
level and avoids scene files, narration files, voice caching, Manim rendering,
and final assembly.

## Style Decisions To Review

- Integer blocks are the primary visual grammar.
- Divisor count is shown as the measured quantity on the gap interior.
- The GWR selected-integer color is stable across all scenes.
- The raw-$Z$ equation appears after the viewer has seen the block mechanics.
- The final frame preserves the distinction between the selected interior
  integer and the next prime endpoint.
