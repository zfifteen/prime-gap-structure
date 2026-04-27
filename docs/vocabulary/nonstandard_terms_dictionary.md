# Dictionary Of Non-Standard Project Terms

This dictionary separates project vocabulary into two migration groups.

The first group is easy word swaps: terms where the project word mostly maps to
a conventional word or phrase. These should be revised first.

The second group is concept terms: terms that bundle a repository-specific
idea, rule, or artifact. These need judgment. Some should be renamed, some
should be defined carefully, and some may remain as internal vocabulary.

Approximate occurrence counts are computed from project-authored text and code,
excluding this vocabulary directory and obvious vendor/output noise. They are
prioritization signals, not exact metrics. Generic words such as "field",
"phase", and "boundary" may include ordinary uses.

## Priority Labels

| Label | Meaning |
|---|---|
| Easy | Swap the word or phrase directly in most prose. |
| Review | The concept is real, but the name may need a better public-facing form. |
| Keep | Keep as a named result, API term, or implementation term, but define it plainly. |
| Restrict | Keep only in code, release history, internal diagnostics, or legacy notes. |
| Retire | Avoid in new prose unless quoting historical material. |

## Easy Word Swaps

These terms usually do not need conceptual redesign. They can be replaced with
ordinary wording while preserving the claim.

| Project term | Approx. occurrences | Prefer | Notes | Priority |
|---|---:|---|---|---|
| boundary | 1162 | next prime `q`; right endpoint; candidate next prime | Avoid when the object is simply a prime. | Easy |
| winner | 1068 | score maximizer; selected interior integer | Use "winner" only after the rule has been defined. | Easy |
| carrier | 828 | integer; selected integer; minimizer; occurrence of divisor count `d` | This is the highest-priority easy swap. | Easy |
| anchor | 760 | input prime `p`; left endpoint prime; start value | Context decides whether it means a prime, a benchmark scale, or a run start. | Easy |
| chamber | 488 | bounded interval after `p`; search interval; prime-gap interior | If both endpoint primes are known, use "prime-gap interior." | Easy |
| phase | 428 | regime; state; stage | Direct swap. | Easy |
| certificate | 375 | diagnostic record unless it is a standard certificate | High-priority public wording cleanup. | Easy |
| frontier | 329 | open problem; current research target | Direct swap. | Easy |
| visible divisor bound | 219 | factor-search bound; divisor-check bound | Direct swap. | Easy |
| field | 215 | score values over an interval; function values over an interval | Another high-priority easy swap. | Easy |
| emit | 214 | output; return; write | Choose the verb that matches the operation. | Easy |
| survivor | 193 | remaining candidate; non-eliminated candidate | Use "accepted candidate" only after selection. | Easy |
| gap-ridge | 179 | near-endpoint concentration of raw-$Z$ maxima | Direct swap for prose; concept details in second table. | Easy |
| engine | 177 | algorithm; implementation | High-priority easy swap. | Easy |
| selector | 171 | selection rule; generator rule | Direct swap. | Easy |
| spoiler | 152 | counterexample candidate; competing integer | Direct swap. | Easy |
| emission | 150 | output record; generated record | "Emission" is tolerable in code, but prose can be plainer. | Easy |
| scheduler | 132 | branch-selection rule | Direct swap. | Easy |
| resolved survivor | 111 | accepted candidate; selected candidate next prime | Direct swap. | Easy |
| prime inference generator | 104 | next-prime generator | Direct swap. | Easy |
| collision | 103 | conflict; competing candidates | Direct swap. | Easy |
| gap winner | 85 | selected interior integer; score maximizer | Keep only when defining Gap Winner Rule. | Easy |
| visible-open | 85 | not eliminated by the current factor bound | Direct swap. | Easy |
| hardening | 80 | rule refinement | Direct swap. | Easy |
| higher-divisor pressure | 80 | constraints from higher-divisor candidates | Direct swap. | Easy |
| forensics | 67 | failure analysis; diagnostic analysis | Direct swap. | Easy |
| chamber reset | 65 | reset at the accepted candidate; restart the search at `q` | Easy when describing mechanics; concept details stay in the second table. | Easy |
| hidden state | 63 | unobserved variable; missing state variable | Direct swap. | Easy |
| label-free | 62 | without using the known answer | Direct swap. | Easy |
| positive witness | 61 | found factor | Direct swap. | Easy |
| lexicographic winner | 57 | leftmost minimizer of `d(n)` | Direct swap. | Easy |
| bundle | 54 | feature group | Direct swap. | Easy |
| memory | 46 | state dependence | Direct swap. | Easy |
| open candidate | 45 | remaining candidate | Direct swap. | Easy |
| GWR carrier | 41 | GWR-selected integer; leftmost minimizer of `d(n)` | Direct swap. | Easy |
| miner | 40 | pattern search script | Direct swap. | Easy |
| pressure ceiling | 40 | constraint cutoff | Direct swap. | Easy |
| gap-local | 39 | within a prime gap | Direct swap. | Easy |
| horizon law | 39 | proposed bound for factor checks | Direct swap. | Easy |
| fixed-point locus | 36 | value $Z=1$ for primes; fixed point $Z=1$ | Avoid "locus" unless geometry is actually being discussed. | Easy |
| leftmost carrier | 36 | leftmost occurrence; first minimizer | Direct swap. | Easy |
| recursive walk | 36 | iterative walk; recurrence | Direct swap. | Easy |
| landmark | 35 | marker; candidate state; selected integer | Avoid unless it truly means a visual marker. | Easy |
| orientation | 34 | left/right location of the selected integer | Direct swap. | Easy |
| witness horizon | 34 | factor-search bound | Direct swap. | Easy |
| earlier spoiler | 30 | earlier counterexample candidate | Direct swap. | Easy |
| chain node | 26 | candidate in the sequence | Direct swap. | Easy |
| lower-divisor threat | 25 | later lower-divisor composite | Direct swap. | Easy |
| graph solver | 24 | constraint-graph solver | Fine internally. | Easy |
| near-edge ridge | 23 | near-endpoint concentration | Direct swap. | Easy |
| first carrier | 22 | first occurrence; leftmost minimizer | Direct swap. | Easy |
| Minimal PGS Generator | 20 | deterministic next-prime generator; two-field next-prime generator | Keep old title in release history if needed. | Easy |
| boundary candidate | 19 | candidate next prime; candidate right endpoint | Direct swap. | Easy |
| phase reset | 19 | state reset | Direct swap. | Easy |
| semiprime-shadow landmark | 19 | unresolved possible semiprime | Direct swap. | Easy |
| shock | 19 | abrupt change; transition | Direct swap. | Easy |
| wheel-open offset | 19 | offset whose value is coprime to 30 | Direct swap. | Easy |
| accepted anchor | 18 | input prime `p`; left endpoint prime; known prime `p` | Use "left endpoint" when discussing an actual prime gap. | Easy |
| terminal node | 18 | final candidate; selected candidate | Direct swap. | Easy |
| bridge certificate | 17 | verification certificate; finite-check certificate | Direct swap if it is really a certificate; otherwise diagnostic record. | Easy |
| band ladder | 16 | sequence of factor-check ranges | Direct swap. | Easy |
| hunter | 16 | search script | Direct swap. | Easy |
| execution surface | 15 | tested runs; committed validation runs | Direct swap. | Easy |
| autopsy | 14 | failure analysis | Direct swap. | Easy |
| boundary certificate | 14 | selection certificate; diagnostic record | Use "certificate" only for a real proof certificate. | Easy |
| generative engine | 14 | generator | Direct swap. | Easy |
| raw composite Z | 14 | $Z_{\mathrm{raw}}(n)$ on composites | Direct swap. | Easy |
| raw composite field | 13 | raw-$Z$ values on composite integers | Direct swap. | Easy |
| carrier enrichment | 12 | overrepresentation of selected integers with `d(n)=...` | Direct swap. | Easy |
| survivor convention | 12 | `proxy_z=1.0` for unrejected candidates | Internal API behavior. | Restrict |
| unresolved alternative | 12 | unresolved candidate | Direct swap. | Easy |
| current chamber | 11 | current search interval | Direct swap. | Easy |
| chamber material | 10 | later interval data; later candidate states | Direct swap. | Easy |
| legal candidate | 10 | allowed candidate | Direct swap. | Easy |
| visible-open chain | 10 | sequence of candidates not eliminated by bounded factor checks | Direct swap. | Easy |
| dead zone | 9 | excluded region; absent residue class in the tested data | Direct swap. | Easy |
| factor-gated | 9 | trial division by configured small-prime tables | Public prose should say what operation is performed. | Easy |
| gated prime tables | 9 | configured small-prime tables | Direct swap. | Easy |
| phase handoff | 9 | regime transition | Direct swap. | Easy |
| right flank | 9 | integers to the right of the selected interior integer | Direct swap. | Easy |
| true-boundary rejection | 8 | rejected the true next prime | Direct swap. | Easy |
| consistency collapse | 7 | candidate elimination | Direct swap. | Easy |
| invariant target | 7 | target value; invariant value | Direct swap. | Easy |
| carrier structure | 6 | positions of low-divisor integers; divisor-count pattern | Direct swap. | Easy |
| edge-distance enrichment | 6 | overrepresentation by distance from endpoint | Direct swap. | Easy |
| emitted boundary | 6 | output `q`; emitted next-prime candidate | Use "emitted" only for records. | Easy |
| false chain node | 6 | composite candidate before `q` | Direct swap. | Easy |
| iprime | 6 | inferred prime; next prime `q` | Internal shorthand; remove from prose. | Retire |
| left flank | 6 | integers to the left of the selected interior integer | Direct swap. | Easy |
| post-reset chamber material | 6 | candidates after the accepted endpoint | Direct swap. | Easy |
| sidecar diagnostics | 6 | separate diagnostic records | Direct swap. | Easy |
| tail after reset | 6 | later candidates after the accepted endpoint | Direct swap. | Easy |
| winner carrier | 6 | score maximizer; selected interior integer | Direct swap. | Easy |
| chamber arithmetic | 5 | arithmetic in the search interval; divisor counts on the interval | Direct swap. | Easy |
| chamber bound | 5 | search bound; offset bound | Direct swap. | Easy |
| `d=4` carrier | 5 | integer with `d(n)=4` | When useful, specify semiprime or prime cube. | Easy |
| edge insulation | 5 | absence of near-endpoint examples under the tested condition | Direct swap. | Easy |
| later chamber | 5 | subsequent search interval | Direct swap. | Easy |
| proof bridge | 5 | finite verification plus analytic reduction | Direct swap. | Easy |
| wheel-open position | 5 | integer coprime to 30 | Direct swap. | Easy |
| admissibility censorship | 4 | restrictions imposed by prime gaps on interior divisor-count patterns | Retire the phrase. | Retire |
| candidate-loop speedup | 4 | candidate-search speedup | Direct swap. | Easy |
| exact raw DNI field | 4 | exact $Z_{\mathrm{raw}}$ values from divisor counts | Direct swap. | Easy |
| fallback displacement | 4 | removal of fallback prime search | Direct swap. | Easy |
| final confirmation path | 4 | final primality checks | Direct swap. | Easy |
| high-scale decade-window surface | 4 | decade-window validation sample | Direct swap. | Easy |
| midpoint ridge | 4 | midpoint concentration | Direct swap. | Easy |
| minimal record | 4 | two-field output record | Direct swap. | Easy |
| production surface | 4 | production validation runs | Direct swap. | Easy |
| source label | 4 | diagnostic selection label | Direct swap. | Easy |
| threat frontier | 4 | obstruction search boundary | Direct swap. | Easy |
| contraction | 3 | composites have $Z(n)<1$ | Direct swap. | Easy |
| hold open | 3 | retain as unresolved | Direct swap. | Easy |
| locked carrier | 3 | committed minimizer; committed selected integer | Direct swap. | Easy |
| locus convention | 3 | survivor convention `proxy_z=1.0` | Internal prefilter language. | Restrict |
| semiprime-shadow seed | 3 | initial unresolved possible semiprime | Direct swap. | Easy |
| boundary hypothesis | 2 | candidate next-prime hypothesis | Direct swap. | Easy |
| bridge arithmetic | 2 | auxiliary computation; intermediate verification | Direct swap. | Easy |
| center of gravity | 2 | current focus | Direct swap. | Easy |
| factor-gated surrogate | 2 | small-prime factor screen | Direct swap. | Easy |
| lock activation profile | 2 | activation profile for a commit condition | Direct swap. | Easy |
| p-chamber | 2 | interval after `p` | Direct swap. | Easy |
| state mask | 2 | selected state variables | Direct swap. | Easy |
| unresolved hold | 2 | unresolved candidate; retained candidate | Direct swap. | Easy |
| bridge-to-theorem conversion | 1 | proving the auxiliary condition | Direct swap. | Easy |
| carrier-lock pressure rule | 1 | constraints after committing to the selected minimizer | Direct swap. | Easy |
| closed candidate | 1 | eliminated candidate | Direct swap. | Easy |
| divisor-class spoiler | 1 | divisor-count obstruction | Direct swap. | Easy |
| divisor-count ridge | 1 | concentration of low divisor counts near gap endpoints | Direct swap. | Easy |
| false boundary promotion | 1 | incorrectly accepting a composite candidate | Direct swap. | Easy |
| fixed traversal rate | 1 | parameter value $v=e^2/2$ | Direct swap. | Easy |
| load-weighted normalization | 1 | normalization $Z(n)=n/\exp(v\kappa(n))$ | Prefer the formula. | Easy |
| proof pressure | 1 | proof obligation; open proof task | Direct swap. | Easy |
| residue-conditioned orientation | 1 | dependence on residue class modulo 30 | Direct swap. | Easy |
| scale expansion | 1 | larger-scale validation | Direct swap. | Easy |
| true-boundary label | 1 | known true next prime used only for audit | Direct swap. | Easy |
| unresolved selector state | 1 | unresolved search; no candidate selected within the bound | Direct swap. | Easy |
| bridge row | 0 | auxiliary-method row | Direct swap. | Easy |
| closed offset | 0 | eliminated offset | Direct swap. | Easy |
| decoder | 0 | classifier | Direct swap. | Easy |
| deterministic stream | 0 | deterministic candidate sequence | Direct swap. | Easy |
| enhanced walk | 0 | extended iterative procedure | Direct swap. | Easy |
| low exact surface | 0 | complete low-range validation | Direct swap. | Easy |
| primary, tail, deep-tail intervals | 0 | small-prime range; later factor-check ranges | Internal config names. | Restrict |
| tail candidate | 0 | later candidate | Direct swap. | Easy |


## Concept Terms

These terms do not collapse to a single conventional word. They point to a
specific repository concept, result, implementation contract, or historical
artifact. Decide case by case whether to keep, rename, or replace with a short
definition.

| Project term | Approx. occurrences | Prefer | Notes | Priority |
|---|---:|---|---|---|
| GWR | 800 | Abbreviation for Gap Winner Rule. | Use only after "Gap Winner Rule (GWR)." | Keep |
| PGS | 687 | Broad abbreviation for "prime-gap structure"; also a diagnostic source label for the current generator path. | Restrict. In public prose, say exactly which rule is being used: "the divisor-count rule on prime-gap interiors" or "the next-prime generator without primality-test fallback." | Review |
| witness | 612 | Divisor or factor proving a candidate composite. | Keep; "factor witness" is conventional enough. | Keep |
| probe | 583 | Script testing one hypothesis or behavior. | Keep in internal docs; "experiment" in public prose. | Keep |
| audit | 462 | Downstream check against known truth or contract. | Keep, but state audit does not choose `q`. | Keep |
| DNI | 294 | Abbreviation for Divisor Normalization Identity. | Use only after "Divisor Normalization Identity (DNI)." | Keep |
| pressure | 281 | Constraint from unresolved candidates or lower-divisor candidates. | Directly use "constraint" unless a specific quantitative pressure is defined. | Review |
| prefilter | 275 | Deterministic screen before Miller-Rabin and final primality confirmation. | Keep; this is conventional enough. | Keep |
| prime-gap structure | 152 | Broad phrase for arithmetic patterns in prime-gap interiors and generator state. | Replace in prose with the specific object: divisor-count pattern, prime-gap interior, residue class, candidate state. | Review |
| wheel-open | 141 | Residues coprime to 30. | Replace in prose, but keep as code shorthand if useful. | Review |
| milestone | 123 | Named completed state of the project. | Keep. | Keep |
| pure PGS | 111 | Generated only by the PGS-labeled rule path. | Restrict until PGS is renamed. Public prose should spell out the actual exclusion of fallback and primality tests. | Restrict |
| gap type | 107 | Classification of a prime gap under project features. | Keep if classification is explicitly defined. | Keep |
| Gap Winner Rule | 100 | Rule selecting the leftmost interior integer with minimum divisor count in a prime gap; used to identify the raw-$Z$ maximizer. | Keep as the named result if public prose defines it as "leftmost minimum-divisor rule." | Keep |
| NLSC | 89 | Abbreviation for no-later-simpler-composite. | Retire in public prose. Spell out the condition. | Retire |
| log-score | 69 | $L(n)=(1-d(n)/2)\ln n$, the logarithm of raw-$Z$. | Keep; this is ordinary enough when formula is shown. | Keep |
| semiprime shadow | 67 | Candidate that may be semiprime with both factors above the current factor-search bound. | Concept is real; public wording should be "possible semiprime not eliminated by bounded factor checks." | Review |
| carrier lock | 62 | Commit point where a selected minimizer begins constraining later candidates. | Concept needs judgment; rename away from "carrier." | Review |
| shadow seed | 59 | Initial unresolved candidate in the old semiprime-shadow workflow. | Retire term; preserve concept only in historical notes. | Retire |
| catalog | 55 | Listing of cases or gap types. | Keep. | Keep |
| Z-band | 51 | Project label for the prefilter family derived from DNI. | Restrict to legacy prefilter references. | Restrict |
| abstention | 50 | No candidate selected. | Keep; common term in classification settings. | Keep |
| least-factor frontier | 50 | Largest least factor among false candidates that must be eliminated. | Concept is useful in analysis; rename if public. | Review |
| proof surface | 50 | Range or assumptions covered by a proof artifact. | Usually replace with "proved range" or "proved conditions." | Review |
| chain horizon closure | 46 | Eliminating earlier composite candidates by checking enough factors. | Concept needs a conventional name tied to bounded factor checks. | Review |
| raw-$Z$ | 46 | Score $Z_{\mathrm{raw}}(n)=n^{1-d(n)/2}$, often compared through its logarithm. | Keep as a compact score name after the formula is shown. | Keep |
| Rule X | 44 | Historical/internal label for a candidate-elimination rule stack. | Retire. Use a descriptive name for the actual rule. | Retire |
| PGS source | 38 | Diagnostic source label for records emitted by the current generator. | Keep as internal diagnostic vocabulary until source labels are renamed. | Restrict |
| Divisor Normalization Identity | 37 | Project name for $Z(n)=n^{1-d(n)/2}$ derived from the repository's divisor-count normalization. | Keep if the formula is written at first use. Public prose should lead with the formula and then name it. | Keep |
| winner law | 37 | Claim that the raw-$Z$ maximizer equals the leftmost minimum-divisor interior integer. | Consider replacing with "maximizer theorem" or "leftmost minimum-divisor rule." | Review |
| shadow chain | 35 | Sequence of unresolved candidates in old high-scale probes. | Retire term; use direct description. | Retire |
| Z-Band Prime Prefilter | 33 | Legacy API/name for the cryptographic prefilter. | Keep when referring to the API or historical artifact. | Keep |
| proxy_z | 29 | Runtime field set to `1.0` for unrejected prefilter candidates and below `1.0` for rejected candidates. | Keep only as API/code vocabulary. | Restrict |
| no-later-simpler composite | 26 | Later composite with smaller divisor count than the selected one. | Replace phrase in prose; concept remains important. | Review |
| validation surface | 21 | Exact ranges or sampled windows tested. | Keep if immediately followed by the tested ranges. | Keep |
| PGS selector | 19 | The generator rule that selects `q` from local state. | Rename toward "next-prime selection rule." Keep only in code until broader rename. | Review |
| PGS-only | 19 | Claim that generation uses the target local rule without trial division, primality tests, or fallback prime search. | Preserve the claim, but spell out the forbidden mechanisms instead of relying on the abbreviation. | Review |
| normalization load | 18 | $\kappa(n)=d(n)\ln(n)/e^2$ in the DNI derivation. | Keep only with formula; otherwise say "the quantity $\kappa(n)$." | Keep |
| winner-take-all peak rule | 16 | Name for the exact match between raw-$Z$ maximization and the leftmost minimum-divisor rule. | Rename or retire; it sounds more dramatic than necessary. | Review |
| resonance | 15 | Experimental shorthand for repeated residue/state alignment. | Retire unless formalized. | Retire |
| synthesis | 15 | Generating candidate rules from observed cases. | Keep internally; define if public. | Keep |
| dominant `d=4` regime | 12 | Common case where the selected interior integer has exactly four divisors. | Keep concept; write as "gaps whose selected integer has `d(n)=4`." | Review |
| boundary certificate graph | 11 | Graph of candidate constraints used by experimental solvers. | Rename to "candidate-constraint graph." | Review |
| RH bridge | 8 | Short form of DNI-to-RH bridge. | Restrict. | Restrict |
| geofac | 7 | Experimental shorthand in predictor probes. | Retire. | Retire |
| taxonomy | 6 | Classification of observed cases. | Keep. | Keep |
| threat ceiling | 6 | Cutoff induced by a later lower-divisor composite. | Concept may matter; rename toward "lower-divisor cutoff." | Review |
| DNI-to-RH bridge | 5 | Dirichlet-series helper code relating DNI coefficients to zeta-function expressions. | Restrict to that module; define mathematically if discussed. | Restrict |
| absorption lock | 4 | Experimental commit/acceptance phrase. | Retire unless a precise algorithmic state requires it. | Retire |
| result surface | 4 | Scope over which a result has been measured or proved. | Usually replace with "result scope." | Review |
| Rule X with chamber reset | 3 | Candidate-elimination plus reset at the accepted candidate. | Retire phrase; concept should be renamed if kept. | Retire |
| left-prefix exclusion | 2 | Condition that earlier interior integers have larger divisor count than the selected one. | Concept is useful; name should probably become "left-side divisor-count condition." | Review |
| right-suffix exclusion | 2 | Condition that later interior integers do not have smaller divisor count than the selected one. | Concept is useful; name should probably become "right-side divisor-count condition." | Review |
| score profile | 2 | Graph of $L(n)$ or raw-$Z$ over an interval. | Keep; define plotted score. | Keep |
| candidate-elimination engine | 1 | Implementation of a rule stack that eliminates candidate next primes. | Rename to "candidate-elimination algorithm" in prose. | Review |
| divisor-profile admission condition | 1 | Required shape of divisor counts across a gap if GWR holds. | Concept is useful; rename toward "divisor-count condition on the gap interior." | Review |
| fallback removal | 1 | Removal of backup prime-search paths from generation. | Keep; concept is operationally important. | Keep |
| horizon compression | 1 | Reducing the factor-search bound below trial division up to $\sqrt n$. | Concept is useful; phrase can become "reduced factor-search bound." | Review |
| spoiler family | 1 | Parametrized family of possible counterexample candidates. | Concept maps to "obstruction family"; change term unless old proof notes require it. | Review |
| freeze id | 0 | Version identifier for a generator milestone. | Keep in release metadata; replace in prose. | Restrict |
| no-later-simpler-composite ceiling | 0 | Bound induced by the first later composite with smaller divisor count. | Rename toward "lower-divisor cutoff." | Review |

## Public-Facing Rewrite Rules

1. Start with consecutive primes and the integers between them.
2. Say "interior composite integer" instead of introducing a new object name.
3. Say "divisor count $d(n)$" before naming any rule.
4. Define GWR as "choose the leftmost interior integer with minimum divisor count."
5. Use "raw-$Z$ score" only after writing the formula.
6. Avoid "carrier", "chamber", "shadow", "pressure", "locus", and "engine" in
   public-facing exposition unless quoting or explaining legacy repo language.
7. When a term survives only as code/API vocabulary, mark it as implementation
   vocabulary rather than mathematics.
8. Do not use "certificate" unless the artifact is actually a certificate in
   the conventional sense; otherwise say "diagnostic record" or "verification
   record."

## First Cleanup Batch

These are the easiest high-impact edits to make first.

| Replace this | With this |
|---|---|
| chamber | bounded interval after `p`; prime-gap interior |
| carrier | selected integer; minimizer; integer with divisor count `d` |
| anchor | left endpoint prime; input prime `p` |
| boundary | next prime; right endpoint; candidate next prime |
| landmark | marker; unresolved candidate; selected integer |
| survivor | remaining candidate; accepted candidate when selected |
| fixed-point locus | value $Z=1$ for primes |
| field | score values over an interval |
| pressure | constraint |
| ceiling | cutoff or bound |
| engine | algorithm or implementation |

## Concept Review Batch

These should wait until the easy swaps are done.

| Term | Decision needed |
|---|---|
| PGS | Decide whether to rename the project-level method or restrict the abbreviation to internal source labels. |
| Gap Winner Rule | Likely keep, but public prose should define it as the leftmost minimum-divisor rule. |
| Divisor Normalization Identity | Likely keep, but lead with the equation. |
| no-later-simpler composite / NLSC | Decide whether the condition needs a short name at all. |
| Rule X | Retire or replace with a descriptive algorithm name. |
| semiprime shadow / shadow seed / shadow chain | Replace with bounded-factor-check language or quarantine as historical vocabulary. |
| chamber reset | Decide whether "reset at accepted candidate" is enough or whether the implementation needs a named rule. |
| carrier lock | Rename after "carrier" is removed. |
| validation surface | Keep only if every use names the exact tested ranges or samples. |
