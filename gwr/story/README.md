# The Gap Winner Rule

## How a geometric-looking score collapsed to a simple arithmetic law

Take two consecutive prime numbers, like $13$ and $17$.
The numbers in between, $14, 15, 16$, are the interior of the gap.
In a prime gap, every interior number is composite.

I wanted to compare those interior composites using one numerical quantity.
The quantity was designed to favor numbers with fewer divisors, while also taking
into account how large the number is. A number with fewer divisors is, in that
limited sense, arithmetically simpler than one with many divisors.

The underlying multiplicative quantity is

$$
Z_{\mathrm{raw}}(n) = n^{\,1 - d(n)/2}.
$$

Here $d(n)$ means the number of positive divisors of $n$. In the project notes,
this is the raw-$Z$ quantity.

The implementation compares selected integers using its logarithm,

$$
L(n) = \ln Z_{\mathrm{raw}}(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n).
$$

Because the logarithm is strictly increasing on positive inputs, maximizing
$L(n)$ is equivalent to maximizing raw-$Z$.

At the beginning, I was not looking for a simple selection rule.
I was only trying to understand a repeated visual pattern: when I plotted this
log-score across the interior of many prime gaps, the peak kept leaning toward
the left side of the gap.

That is where the story starts.

## The log-score looked geometric before it looked arithmetic

If you look at individual gaps, the implemented log-score landscape really does
look like a profile. Some carriers sit high, some collapse deep negative, and
the peak often leans toward the left side of the gap. That is exactly why the
result was surprising once it appeared.

The key local fact is visible in exemplar gaps: the log-score maximizer and the
leftmost minimum-divisor integer land on the same carrier.

![Exemplar prime gaps: the log-score maximizer and the GWR-selected integer coincide](./plots/figure_01_exemplar_gap_profiles.png)

The top-left panel shows the smallest nontrivial eligible gap. The lower panels
show tighter-margin examples where several interiors compete more closely. Even
there, the black star marking the log-score maximizer sits exactly on the red ring
marking the Gap Winner Rule selected integer.

That identity is the main discovery.

## The surprise was not that the selected integer leaned left

The surprise was that the selected integer collapsed completely.

On the repository's current proof surface, the implemented log-score maximizer is
exactly the same as the integer
selected by the simple rule:

1. choose the smallest interior divisor count $d(n)$,
2. among ties, choose the leftmost interior integer.

That is the Gap Winner Rule (GWR).

The important point is that GWR is not a loose summary. It was first an exact
identity on the validation ladder, from exact runs at $10^6$ and
$2 \times 10^7$ through sampled higher-scale windows out to $10^{12}$. The
current repo proof surface closes that maximizer rule rather than leaving it as a
proof-program target.

![GWR validation surface: every reported tested regime remains at match rate 1.0](./plots/figure_02_match_rate_surface.png)

The figure above shows the current ladder of reported validation regimes. The
line stays at match rate $1.0$ throughout. The anchor table beneath it keeps
the gap counts readable without overloading the chart.

So the headline is not “the log-score often agrees with a simpler rule.” The
headline is: the log-score maximizer and the rule selection are the same point, and
the repository now presents that maximizer rule as closed.

## One maximizer rule explains several separate-looking phenomena

Before GWR, several observations looked like distinct facts:

- $d(n)=4$ selected integers appeared unusually often,
- selected integers appeared unusually often in the left half of the gap,
- edge-distance $2$ showed up again and again.

Once GWR is in view, those observations compress into one mechanism.

The divisor-count effect becomes clear when selected integers are compared against the
baseline availability of divisor classes across all interior composites.

![Selected integer selection is strongly enriched toward low divisor-count classes](./plots/figure_03_divisor_enrichment.png)

This plot is not showing raw counts. It is showing selection pressure. A bar
above $1$ means that divisor class is chosen more often than its baseline
availability would predict. The dominant selected divisor-count classes are the lowest ones
available, especially $d(n)=3$ and $d(n)=4$. On the tested prime-gap surface,
the frequent selected divisor-count class is $d(n)=4$ because it is the first abundant low-
divisor class that regularly appears in gap interiors.

The left-edge effect shows up just as clearly if selected-integer positions are compared
with the baseline distribution of all interior positions.

![Selected integers cluster toward the left side of the gap](./plots/figure_04_normalized_position.png)

The gray histogram is what you would get from all interior positions. The blue
histogram is where the selected integers actually land. The selected-integer mass is pulled left.

The edge-distance view isolates this even more sharply.

![Edge-distance 2 is heavily overrepresented among selected integers](./plots/figure_05_edge_distance.png)

Edge-distance $2$ stands out immediately. That is not a separate law. It is one
of the visible consequences of the same selection rule when low-divisor carriers
appear near the left endpoint of the gap.

So the right reading is not that I discovered several unrelated regularities.
The right reading is that one exact maximizer rule explains them together.

## The first theorem temptation was stronger than the truth

Once the collapse appeared, the natural next thought was that the log-score,
equivalently raw-$Z$, might be
globally lexicographic on composites, not just inside prime gaps.

That stronger claim would say, in effect, that lower divisor count always wins,
with smaller integer breaking ties, even for arbitrary unordered composite
pairs.

That stronger claim is false.

One explicit counterexample is the pair $49$ and $6$.

![Why the unrestricted global theorem fails: lower d(n) does not always win out of order](./plots/figure_06_counterexample_pair.png)

Here $49$ has smaller divisor count than $6$, but it does not have larger
log-score. Equivalently, it does not have larger raw-$Z$. That matters because
it tells us not to over-read the empirical prime-gap result into a broader
unrestricted theorem that the implemented comparison does not actually satisfy.

This correction strengthens the story rather than weakening it. It tells us
exactly where the real mathematical question lives.

## What survives exactly

The exact theorem that survives is narrower and cleaner.

If $a < b$ are composite integers and $d(a) \leq d(b)$, then
$L(a) > L(b)$, equivalently $Z_{\mathrm{raw}}(a) > Z_{\mathrm{raw}}(b)$.

This is the Lexicographic Raw-Z Dominance Theorem. It is a directional
dominance result, not an unrestricted global ordering law. Earlier composite
plus no larger divisor count forces larger log-score, equivalently larger
raw-$Z$.

That distinction matters. It means the theorem is not “lower divisor count wins
everywhere.” It is “lower-or-equal divisor count wins when it occurs earlier.”

That surviving statement is still powerful, because it suggests the prime-gap
question is no longer about proving a score identity from nothing. The question
becomes: why do prime-gap interiors appear always to place the selected integer inside
that ordered-dominance regime?

## The proof bridge now lands

The former open problem now has a certificate for the main bridge.

It is not:

“Why does this log-score happen to look left-leaning?”

It is:

“Why do prime-gap interiors arrange themselves so that the minimum-divisor
leftmost carrier dominates the log-score competition?”

The answer now has a two-part proof shape: ordered dominance eliminates every
later candidate after the leftmost minimum-divisor carrier, and the
no-early-spoiler bridge eliminates every earlier higher-divisor candidate. The
committed certificate puts the analytic bridge threshold below the exact
finite base through $p < 20{,}000{,}001$.

The heatmap below shows where the selected integers actually live on the tested prime-gap
surface.

![Selected integer mass concentrates in the low-divisor, left-side corner](./plots/figure_07_winner_heatmap.png)

The selected-integer mass sits heavily in the low-divisor, left-side corner. That picture
captures the whole story in one frame. The log-score looks continuous. The
maximizer rule looks discrete. The tested prime-gap interiors land in the corner
where the discrete law wins.

That is why GWR matters.

It does not merely say that a geometric-looking score often peaks near the left
edge. It says that the implemented log-score maximizer, equivalently the raw-$Z$
selected integer, is governed by a simpler arithmetic law than the formula first
suggests.

The strongest supported statement at this stage is therefore:

The Gap Winner Rule is a proved universal maximizer theorem in this repository,
and it compresses several previously separate-looking observations into one
selection rule.

See [gap_winner_rule.md](../findings/gap_winner_rule.md) for the formal
statement and legacy-name notes.
