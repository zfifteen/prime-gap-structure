# The Gap Winner Rule

## How a geometric-looking score collapsed to a simple arithmetic law

Take two consecutive prime numbers, like $13$ and $17$.
The numbers in between, $14, 15, 16$, are the interior of the gap.
In a prime gap, every interior number is composite.

I wanted to compare those interior composites using one numerical score.
The score was designed to favor numbers with fewer divisors, while also taking
into account how large the number is. A number with fewer divisors is, in that
limited sense, arithmetically simpler than one with many divisors.

To make that comparison precise, I used the quantity

$$
Z(n) = \left(1 - \frac{d(n)}{2}\right)\ln(n),
$$

where $d(n)$ means the number of positive divisors of $n$, and $\ln(n)$ is the
natural logarithm of $n$. In the project notes, I call this the raw-$Z$ score.

At the beginning, I was not looking for a simple winner rule.
I was only trying to understand a repeated visual pattern: when I plotted this
score across the interior of many prime gaps, the peak kept leaning toward the
left side of the gap.

That is where the story starts.

## The score looked geometric before it looked arithmetic

If you look at individual gaps, the raw-$Z$ landscape really does look like a
profile. Some carriers sit high, some collapse deep negative, and the peak
often leans toward the left side of the gap. That is exactly why the result was
surprising once it appeared.

The key local fact is visible in exemplar gaps: the raw-$Z$ winner and the
minimum-divisor leftmost winner land on the same carrier.

![Exemplar prime gaps: the raw-Z winner and the GWR winner coincide](./plots/figure_01_exemplar_gap_profiles.png)

The top-left panel shows the smallest nontrivial eligible gap. The lower panels
show tighter-margin examples where several interiors compete more closely. Even
there, the black star marking the raw-$Z$ winner sits exactly on the red ring
marking the Gap Winner Rule winner.

That identity is the main discovery.

## The surprise was not that the winner leaned left

The surprise was that the winner collapsed completely.

On the tested prime-gap surface, the raw-$Z$ winner is exactly the same as the
integer selected by the simple rule:

1. choose the smallest interior divisor count $d(n)$,
2. among ties, choose the leftmost interior integer.

That is the Gap Winner Rule (GWR).

The important point is that GWR is not a loose summary on the tested surface.
It is an exact identity on the current validation ladder, from exact runs at
$10^6$ and $2 \times 10^7$ through sampled higher-scale windows out to $10^{12}$.

![GWR validation surface: every reported tested regime remains at match rate 1.0](./plots/figure_02_match_rate_surface.png)

The figure above shows the current ladder of reported validation regimes. The
line stays at match rate $1.0$ throughout. The anchor table beneath it keeps
the gap counts readable without overloading the chart.

So the headline is not “the score often agrees with a simpler rule.” The
headline is: on the tested surface, the score winner and the rule winner are
the same point.

## One winner law explains several separate-looking phenomena

Before GWR, several observations looked like distinct facts:

- $d(n)=4$ winners appeared unusually often,
- winners appeared unusually often in the left half of the gap,
- edge-distance `2` showed up again and again.

Once GWR is in view, those observations compress into one mechanism.

The divisor-count effect becomes clear when winners are compared against the
baseline availability of divisor classes across all interior composites.

![Winner selection is strongly enriched toward low divisor-count classes](./plots/figure_03_divisor_enrichment.png)

This plot is not showing raw counts. It is showing selection pressure. A bar
above $1$ means that divisor class is chosen more often than its baseline
availability would predict. The dominant winner classes are the lowest ones
available, especially $d(n)=3$ and $d(n)=4$. On the tested prime-gap surface,
the frequent winner class is $d(n)=4$ because it is the first abundant low-
divisor class that regularly appears in gap interiors.

The left-edge effect shows up just as clearly if winner positions are compared
with the baseline distribution of all interior positions.

![Winners cluster toward the left side of the gap](./plots/figure_04_normalized_position.png)

The gray histogram is what you would get from all interior positions. The blue
histogram is where the winners actually land. The winner mass is pulled left.

The edge-distance view isolates this even more sharply.

![Edge-distance 2 is heavily overrepresented among winners](./plots/figure_05_edge_distance.png)

Edge-distance $2$ stands out immediately. That is not a separate law. It is one
of the visible consequences of the same winner rule when low-divisor carriers
appear near the left boundary of the gap.

So the right reading is not that I discovered several unrelated regularities.
The right reading is that one exact winner law explains them together.

## The first theorem temptation was stronger than the truth

Once the collapse appeared, the natural next thought was that raw-$Z$ might be
globally lexicographic on composites, not just inside prime gaps.

That stronger claim would say, in effect, that lower divisor count always wins,
with smaller integer breaking ties, even for arbitrary unordered composite
pairs.

That stronger claim is false.

One explicit counterexample is the pair $49$ and $6$.

![Why the unrestricted global theorem fails: lower d(n) does not always win out of order](./plots/figure_06_counterexample_pair.png)

Here $49$ has smaller divisor count than $6$, but it does not have larger
raw-$Z$. That matters because it tells us not to over-read the empirical prime-
gap result into a broader unrestricted theorem that the score does not actually
satisfy.

This correction strengthens the story rather than weakening it. It tells us
exactly where the real mathematical question lives.

## What survives exactly

The exact theorem that survives is narrower and cleaner.

If $a < b$ are composite integers and $d(a) \le d(b)$, then $Z(a) > Z(b)$.

This is the Lexicographic Raw-Z Dominance Theorem. It is a directional
dominance result, not an unrestricted global ordering law. Earlier composite
plus no larger divisor count forces larger raw-$Z$.

That distinction matters. It means the theorem is not “lower divisor count wins
everywhere.” It is “lower-or-equal divisor count wins when it occurs earlier.”

That surviving statement is still powerful, because it suggests the prime-gap
question is no longer about proving a score identity from nothing. The question
becomes: why do prime-gap interiors appear always to place the winner inside
that ordered-dominance regime?

## The remaining open question is now sharper

The open problem is no longer vague.

It is not:

“Why does this score happen to look left-leaning?”

It is:

“Why do prime-gap interiors seem always to arrange themselves so that the
minimum-divisor leftmost carrier dominates the raw-$Z$ competition?”

The heatmap below shows where the winners actually live on the tested prime-gap
surface.

![Winner mass concentrates in the low-divisor, left-side corner](./plots/figure_07_winner_heatmap.png)

The winner mass sits heavily in the low-divisor, left-side corner. That picture
captures the whole story in one frame. The score looks continuous. The winner
law looks discrete. The tested prime-gap interiors land in the corner where the
discrete law wins.

That is why GWR matters.

It does not merely say that a geometric-looking score often peaks near the left
edge. On the tested surface, it says that the winner is governed by a simpler
arithmetic law than the score formula first suggests.

The strongest supported statement at this stage is therefore:

The Gap Winner Rule is an exact winner law on the tested prime-gap surface, and
it compresses several previously separate-looking observations into one
selection rule.

The central open question is whether prime-gap interiors satisfy a deeper
structural condition that forces that rule to hold, and whether that condition
can be stated and proved cleanly.

For the formal statement and the legacy-name notes, see
[`gwr/findings/gap_winner_rule.md`](../findings/gap_winner_rule.md).
