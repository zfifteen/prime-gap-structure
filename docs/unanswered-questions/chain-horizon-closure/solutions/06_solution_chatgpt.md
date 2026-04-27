Recommendation: implement the least-factor maximum probe now. Do not promote any H law yet.

The best answer is 05_answer_chatgpt, with useful support from 03_answer_deepseek, 04_answer_copilot, and 06_answer_xai_grok. The central reason: the right theorem target is not “prove the terminal node is prime.” The right theorem target is “derive a PGS-visible horizon that closes every false shadow-chain node before the terminal next prime.” That matches the actual repo gap: chain_horizon_closure_result(..., horizon_bound=None) still lets divisor_witness fall through to complete divisor exhaustion, while DEFAULT_VISIBLE_DIVISOR_BOUND = 10000 only builds the sequence of candidates not eliminated by bounded factor checks.  ￼

The current unanswered question is framed correctly: can chain_horizon_closure become pure PGS by deriving H(p, s0, chain_state) rather than using fallback divisor exhaustion?  ￼ The answer after review and pilot testing is:

Possible, but unproven.
The next experiment must mine least-factor maximums.
No proposed answer currently supplies the actual horizon law.

Repo-grounded baseline

The current high-scale operational shape is strong. The repo summary shows:

10^15:
outputted = 249 / 256
unresolved = 7
audit_failed = 0
PGS = 43.37%
chain_horizon_closure = 56.63%
fallback = 0%
10^18:
outputted = 250 / 256
unresolved = 6
audit_failed = 0
PGS = 42.00%
chain_horizon_closure = 58.00%
fallback = 0%

So the bridge works operationally, but the pure PGS fraction is below the 50% campaign gate at 10^15 and 10^18.  ￼

The code confirms the exact theorem gap. visible_open_chain_offsets uses visible closure with DEFAULT_VISIBLE_DIVISOR_BOUND = 10000, but chain_horizon_closure_result accepts horizon_bound=None, which means the divisor witness check uses the complete divisor range up to sqrt(n). That is the non-PGS bridge arithmetic.  ￼

Experiment I ran

I ran a standalone reproduction of the current generator logic using the fetched repo implementation as the source model. Because the sandbox cannot clone GitHub directly, I reproduced the relevant functions locally:

candidate_bound = 128
chain_limit = 8
visible_divisor_bound = 10000
scales = 10^12, 10^15, 10^18
sample_size = 16 input primes per scale
factor_bound = 100000

This is a bounded pilot, not a full theorem result. It tests whether small, obvious horizon candidates already explain the false chain nodes.

For each sampled input prime, I rebuilt:

PGS search-interval-closure candidate q0
shadow sequence of candidates not eliminated by bounded factor checks
terminal chain node if one was prime
false pre-terminal nodes
least visible divisor <= 100000 where available

Pilot result

scale	PGS rows	chain rows	unresolved chain	false chain nodes	known least factor nodes <=100k	unknown >100k
10^12	10	6	0	9	5	4
10^15	4	11	1	12	5	7
10^18	7	9	0	12	3	9

For known least factors:

scale	max known least factor	median known least factor	p95 known least factor
10^12	19,001	14,887	15,467
10^15	93,911	47,293	49,549
10^18	34,381	16,477	16,477

This already rules out the smallest naive horizons. The current visible bound 10000 closed none of the false nodes in the pilot. The dynamic 0.5 log(q)^2 horizon also closed none. Several false nodes required more than 100000, so the least-factor maximum is not trivially small.

Candidate horizon laws tested in the pilot

candidate H	false nodes closed	total false nodes	lower-bound closure rate
visible_10000	0	33	0.00%
0.5 log(q)^2	0	33	0.00%
visible + max_chain_gap_so_far	0	33	0.00%
visible + chain_position * 64	1	33	3.03%
visible + seed_offset * 1000	7	33	21.21%
visible + prefix_lcm_gaps capped at 1e6	0	33	0.00%
fixed 100000	13	33	39.39%
fixed 1000000	13	33	39.39% in this bounded run, because the collection only searched divisors to 100000

The pilot does not say the horizon tracks sqrt(q). It only says the obvious low horizons do not close the false chain nodes. The decisive next step is a full least-factor maximum run, not another ranker.

Answer-by-answer evaluation

01_answer_meta_ai

Meta’s answer gets the main experiment right: mine H_obs = max least prime factor over false chain nodes, then compare it against sqrt(q), C(q), wheel/residue-state variables, and chain state. It also correctly frames semiprime-shadow nodes as structured, not random.  ￼

Where it overreaches: it predicts the least-factor maximum might be well under 200–300. My bounded pilot does not support that. I saw known least factors up to 93,911, and many false nodes had no divisor under 100,000. That does not kill compressibility, but it kills the “tiny horizon” optimism.

Experiment verdict:

Meta's experiment design: PASS
Meta's small-horizon intuition: FAIL on pilot evidence
Usefulness: high
Risk: overconfident about O(log q) / O(log^2 q)

02_asnwer_grok

This answer is the most overconfident. It says the bridge is “almost certainly” compressible and claims the repo already contains scripts like simple_pgs_recursive_shadow_chain_state_mine.py and simple_pgs_shadow_chain_terminal_diagnostic record_mine.py. A repo search at the referenced commit only found that claim inside the answer file itself, not the actual scripts.  ￼

It also claims “no evidence” that the horizon tracks sqrt(q), which is technically true but too strong. The correct statement is narrower: we do not yet know the least-factor maximum. The pilot shows many false nodes exceed 10000, and many exceed 100000, so the optimistic “small visible horizon” story is not established.

Experiment verdict:

Core direction: partly right
Infrastructure claims: not supported by repo search
Confidence level: too high
Usefulness: low to moderate
Actionable part: add explicit least-factor maximum miner

03_asnwer_deepseek

DeepSeek’s answer is conservative and mostly correct. It identifies the exact bridge gap: chain_horizon_closure_result calls divisor_witness(candidate, horizon_bound), and when horizon_bound is None, the check defaults to full divisor exhaustion. It then recommends collecting witness data and fitting a horizon law.  ￼

This answer does not add a novel theorem idea, but it is clean and safe. It aligns with the implementation.

Experiment verdict:

Implementation diagnosis: PASS
Experiment design: PASS
Novel insight: limited
Usefulness: high as a sanity check

04_answer_copilot

Copilot gives the most detailed engineering plan: add a least-factor maximum logger, run stratified probes, test polylog, residue-based, wheel-limited, and input prime-gap combined bounds.  ￼

The pilot directly supports Copilot’s caution. Simple polylog and low wheel-like bounds did not close the false chain nodes. A fixed 100000 bound only closed a lower-bound 39.39% of false nodes in the pilot. This means the full collector is necessary before any theorem claim.

Experiment verdict:

Engineering plan: PASS
Candidate H families: reasonable
Pilot outcome: simple versions fail
Usefulness: high
Caution: keep prime tables / wheel-sieved division strictly in probe or audit context, not pure generator logic

05_answer_chatgpt

This is the best conceptual answer. It sharpens the target: do not try to prove the terminal node prime; instead derive a horizon that closes all false pre-terminal chain nodes.  ￼

That distinction survives the pilot. The false-node closure least-factor maximum is the right object. The tested toy laws from that answer, such as visible, 0.5 log², visible + max gap, and prefix-gap expressions, failed on the pilot, but the experimental frame remains the strongest.

Experiment verdict:

Conceptual framing: PASS
Specific toy H laws: FAIL on pilot
Next experiment: exactly correct
Overall: strongest answer

06_answer_xai_grok

This answer correctly reads the code shape: construction of the sequence of candidates not eliminated by bounded factor checks is local and PGS-visible; horizon closure is the remaining non-PGS step because it still uses divisor witnesses up to a supplied bound or full sqrt(n).  ￼

It overstates the proof intuition when it says GWR and NLSC “strongly suggest” the invariant should exist. That may be true, but the pilot shows the horizon is not a tiny visible extension. The needed law, if it exists, is subtler than “visible bound plus small local residue features.”

Experiment verdict:

Code diagnosis: PASS
Theorem optimism: unproven
Experiment design: PASS
Usefulness: moderate to high

Synthesis

All serious answers converge on the same next experiment:

Mine the least-factor maximum of false shadow-chain nodes.

The differences are in confidence. Meta, Grok, and xAI are too optimistic about how small or obvious H will be. DeepSeek and Copilot are more sober. ChatGPT’s answer gives the cleanest theorem formulation.

The pilot result says:

The obvious H candidates are not enough.

It does not say:

No PGS-visible H exists.

The least-factor maximum may still be governed by a deterministic expression, but it is not simply:

10000
0.5 log(q)^2
visible bound plus chain gap
visible bound plus chain position

The likely next law, if it exists, must involve a stronger row-level or chain-level state, probably something like:

H(p, s0, chain_state)
= a function of seed offset, chain position, local residue vector,
and the visible obstruction pattern before each false node

But this must be discovered from data, not guessed.

Recommended next implementation

Create:

benchmarks/python/predictor/simple_pgs_shadow_chain_horizon_law_probe.py

Run:

scales:
10^12 exact sample
10^15 high probe
10^18 high probe
candidate_bound = 128
visible_divisor_bound = 10000
chain_limit = 8

Primary artifacts:

least_factor_maximum.csv
horizon_law_report.csv
horizon_law_summary.json

Per false chain node, output:

scale
input_prime_p
seed_s0
chain_index
node_n
terminal_index
least_factor_for_audit_only
least_factor_over_sqrt_node
least_factor_over_visible_bound
node_offset_from_anchor
node_offset_from_seed
delta_prev
delta_next
prefix_delta_vector
node_mod_30
offset_mod_30
visible_open_count_before_node
visible_closed_count_before_node
closure_reason_vector_before_node
candidate_bound
visible_divisor_bound

Then test these H families:

H_visible = 10000
H_dynamic = ceil(0.5 log(q)^2)
H_fixed_1e5
H_fixed_1e6
H_seed_offset_family
H_chain_position_family
H_prefix_delta_family
H_residue_vector_family
H_row_frontier_predictor from chain_state only

The promotion gate should be harsh:

Promote only if a PGS-visible H:
closes 100% of pre-terminal false chain nodes on tested surfaces;
selects the same first surviving terminal node as current chain_horizon_closure;
remains far below sqrt(n);
requires no audit labels or factorization to compute at generation time.

Final recommendation

Do not patch the generator yet.

Do not promote chain_horizon_closure to pure PGS.

Do not chase another ranker.

Implement the least-factor maximum miner and let the data decide whether H(p, s0, chain_state) exists. The strongest formulation is from 05_answer_chatgpt; the strongest engineering plan is from 04_answer_copilot; the safest implementation diagnosis is from 03_answer_deepseek.
