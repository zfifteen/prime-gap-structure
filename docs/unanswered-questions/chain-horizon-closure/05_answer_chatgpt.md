Yes. The answer is:

chain_horizon_closure can plausibly become a pure PGS next-prime selection rule, but only if the horizon law is about closing false shadow-chain nodes, not about proving the terminal node prime by trial division.

That distinction is the missing key.

Plain-language mode:

Right now chain_horizon_closure works because it walks the shadow chain and uses divisor exhaustion to close composite nodes until one survives. That is operationally excellent, but it is not pure PGS yet.

The theorem target should not be:

How do we prove q is prime from local PGS state?

That is too strong and collapses back toward classical primality proving.

The theorem target should be:

How far must the generator look to expose every false shadow-chain node before the true next prime?

If we can derive a horizon H(p, s0, chain_state) that always closes the false chain nodes before the terminal next prime, then the terminal node becomes the first survivor of a deterministic PGS chain process. That is the bridge-to-theorem conversion.

Technical-domain mode:

The repo implementation makes the gap very precise. In simple_pgs_generator.py, DEFAULT_VISIBLE_DIVISOR_BOUND = 10000 is used to build the visible-open chain, while chain_horizon_closure_result(..., horizon_bound=None) makes divisor_witness(candidate, horizon_bound) use complete divisor exhaustion up to sqrt(candidate) for the chain node. That is exactly the non-PGS part we need to replace.  ￼

The high-scale bridge result says the operational shape is right: at 10^15, the probe emits 249 / 256 rows with 0 audit failures, 43.37% pure PGS and 56.63% chain_horizon_closure; at 10^18, it emits 250 / 256 rows with 0 audit failures, 42.00% pure PGS and 58.00% chain_horizon_closure.  ￼

So the current status is:

Search object: solved.
Operational recovery: solved on tested high-scale probes.
Pure terminal law: not solved.

The most important refinement: H should not be asked to certify the terminal node as prime. It should be asked to certify the pre-terminal chain nodes as false.

That gives the theorem candidate a sharper form:

Shadow-Chain Horizon Law
Given anchor p and semiprime-shadow seed s0, construct the visible-open chain
C = (s1, s2, ..., sk).
There exists a PGS-visible horizon H(p, s0, C_i) such that every false chain node
before the true next prime has a divisor witness <= H, while the true next prime is
the first chain node not closed by that horizon.

This is much more plausible than proving primality directly.

The immediate experiment should be:

Least-Factor Frontier Probe

Create a benchmark that only analyzes chain_horizon_closure rows from 10^12, 10^15, and 10^18. For every chain node before the terminal node, record the least divisor that closes it. For the terminal node, record only that it survived until audit confirmed it. Do not use terminal primality as a feature.

Per false chain node, emit:

scale
anchor_p
seed_s0
chain_index
node_n
terminal_index
is_preterminal_false_node
least_factor_for_audit_only
cofactor_for_audit_only
least_factor_rank_vs_visible_bound
least_factor_minus_visible_bound
least_factor_over_visible_bound
node_offset_from_anchor
node_offset_from_seed
delta_prev
delta_next
prefix_delta_vector
chain_position
node_mod_30
offset_mod_30
carrier_to_node_delta
closure_reason_vector_before_node
visible_open_count_before_node
visible_closed_count_before_node
candidate_bound
visible_divisor_bound

Then test candidate horizon laws:

H0 = visible_divisor_bound
H1 = visible_divisor_bound + max chain gap so far
H2 = visible_divisor_bound + product or lcm of visible-open residue gaps in prefix
H3 = max visible divisor witness observed in closure_reason_vector_before_node
H4 = visible_divisor_bound + f(chain_position, delta_prev, delta_next)
H5 = smallest divisor horizon that closes all prior false chain nodes in the same row
H6 = row-level horizon predicted from seed_s0 residue, carrier_to_seed_delta, and prefix delta vector

The key report should not be accuracy first. It should be horizon compression:

scale
chain_rows
false_chain_nodes
max_least_factor_false_node
median_least_factor_false_node
p95_least_factor_false_node
max_least_factor / sqrt(node)
max_least_factor / visible_divisor_bound
for each candidate H:
false_nodes_closed
false_nodes_unclosed
terminal_nodes_improperly_closed
first_survivor_correct_count
projected_pgs_rate

The decisive success condition:

A horizon law is promising if it closes 100% of pre-terminal false chain nodes
on 10^12, 10^15, and 10^18 samples while remaining far below sqrt(n).

The decisive failure condition:

If the least factors needed to close false chain nodes grow like sqrt(n),
or if no PGS-visible state predicts them better than a generic factor search,
then chain_horizon_closure is operationally good but not locally compressible
at candidate_bound = 128.

But I would not jump straight to pessimism. The semiprime-shadow behavior already suggests the least-factor frontier may be structured: earlier witness-horizon runs showed failures appearing just beyond active witness bounds, and the new chain data says false nodes repeat the same hidden-obstruction object. That means the required horizon may be a moving frontier tied to the chain state, not sqrt(q).

Next instruction:

Implement:

simple_pgs_shadow_chain_horizon_law_probe.py

Do not patch the generator.

Run:

10^12 exact sample
10^15 high probe
10^18 high probe
candidate_bound = 128
visible_divisor_bound = 10000
chain_limit = 8

Primary output:

least_factor_frontier.csv
horizon_law_report.csv
horizon_law_summary.json

Acceptance gate for theorem-candidate promotion:

Promote Shadow-Chain Horizon Law if a PGS-visible H satisfies:
1. closes all pre-terminal false chain nodes on the tested surfaces;
2. selects the same first surviving terminal node as chain_horizon_closure;
3. H / sqrt(n) trends downward or stays tiny at 10^12, 10^15, 10^18;
4. no audit labels or factorization are needed to compute H at generation time.

Current objective: convert chain_horizon_closure from bridge arithmetic into a PGS theorem candidate.

Already established: chain-horizon closure operationally removes high-scale semiprime-shadow failures and preserves zero audit failures on tested probes.

Main blocker: the current chain horizon uses complete divisor checking, not a derived PGS horizon.

Smallest next action: mine the least-factor frontier of false chain nodes and fit candidate H(p, s0, chain_state) laws.

Expected achievement: either identify the missing deterministic horizon law or prove that this bridge is not locally compressible under the current chamber state.
