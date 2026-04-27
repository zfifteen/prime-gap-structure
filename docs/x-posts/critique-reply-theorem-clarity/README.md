# The 'Gap Winner Rule' Explained

I think there is one real terminology issue here, and fixing it makes the
theorem easier to see. Low-divisor integers are not highly composite numbers in
the standard sense. Composite just means not prime. Highly composite means a
record-setting number of divisors among all smaller integers. The dominant
selected integer layer in these gaps is usually divisor-count four, which is low-divisor,
not highly composite.

![Term clarity schematic separating composite, low-divisor, and highly composite](./term_clarity_schematic.png)

---

I do think there is a related intuition hiding inside your comment. Numbers
near prime endpoints are not arithmetically generic. That may help explain why
low-divisor integers often appear early in a gap. But that is still weaker than
the actual result. An early low-divisor arrival is only part of the structure.
The theorem also has to control what happens before that point and after it.

![Endpoint intuition versus the stronger theorem](./boundary_bias_vs_theorem.png)

---

The actual theorem is gap-local and three-part. First, the selected integer is the first
appearance of the lowest divisor class present in the gap. Second, every
earlier spoiler is beaten by some later admissible composite. Third, no later
strictly simpler composite appears before the gap closes. Those three facts
together force the score maximizer. That is stronger than saying the score leans
left or that numbers near primes are composite-rich.

![Three-part theorem structure that forces the selected integer](./theorem_structure_schematic.png)

![Example gaps where the score maximizer and the arithmetic selection coincide](./exemplar_gap_profiles.png)

---

This is also why the result is not already built into the score. Outside prime
gaps, a later number with fewer divisors can still lose. Forty-nine and six is
the clean example. So the score does have a directional bias, but the full
collapse still needs extra prime-gap structure. That extra structure is the
mathematical content of the theorem.

![Counterexample pair showing why the score alone does not force the full rule](./counterexample_pair.png)

---

So I think the right next question is narrower than “why does the score lean
left.” That part is elementary. The sharper question is: what exact arithmetic
filtering by consecutive primes forces gap interiors into this local-dominator
regime so consistently? If that can be stated cleanly, it would explain not
just the score collapse, but why the collapse is so stable across scale.

![Open question schematic for what prime gaps still have to explain](./open_question_schematic.png)
