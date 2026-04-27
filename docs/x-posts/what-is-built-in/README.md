# What Is Built In, And What Prime Gaps Still Have To Explain

When someone first sees the Gap Winner Rule, the natural pushback is that the
score already prefers numbers with fewer divisors and earlier position, so the
result should not be very surprising. That criticism gets one thing right and
one thing wrong. It is right that taking the log does not create a second
maximizer rule. The log and the raw score pick the same point. But that does not
mean the full collapse inside prime gaps is automatic.

![Schematic of what the score already builds in](./score_bias_schematic.png)

---

If the whole rule were already built into the score, then the same maximizer rule
would hold on arbitrary ordered composite sets. It does not. The pair forty-
nine and six is the clean obstruction. Forty-nine has fewer divisors than six,
but it still loses on the score. So the score does not simply say “fewest
divisors always wins.” Something more specific has to be true inside prime
gaps.

![Counterexample pair showing that fewer divisors does not always win out of order](./counterexample_pair.png)

---

That is where the actual prime-gap result begins. Inside tested prime gaps, the
score maximizer and the leftmost carrier of the smallest divisor class present in
the gap land on the same integer. This is not a vague tendency. It is an exact
identity on the tested surfaces. The local gap pictures already show the
collapse directly, and the broader validation surface shows that it stays exact
as the scale grows.

![Exemplar prime gaps where the score maximizer and the arithmetic selection coincide](./exemplar_gap_profiles.png)

![Validation surface showing exact agreement across the tested regimes](./match_rate_surface.png)

---

So the real theorem is not “the score prefers simpler numbers.” That part is
elementary. The real theorem is that prime-gap interiors appear always to
organize themselves so that every earlier spoiler gets beaten by some later
admissible composite, while nothing strictly simpler appears after the selected integer
before the gap closes. That extra organization is what turns a directional bias
into a complete maximizer rule.

![Selected integer mass concentrated in the low-divisor, left-side corner](./winner_heatmap.png)

---

That is the actual open question. Not why the score leans left in a loose
sense, but why prime gaps seem to enforce exactly the local structure needed
for the collapse to be complete.

![Schematic of what prime gaps still have to explain](./open_question_schematic.png)
