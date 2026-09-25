# RSA Live Solver: Endpoint-Chain Closure Plan

**Status:** planning / not started
**Date:** 2026-08-21
**Supersedes:** `docs/plans/rsa_live_solver_factor_favoring_plan.md` (withdrawn; objective function was a factorization score)
**Surface owners (keep separate):**
- v3 A1 resolver: `research/06-cryptology-rsa/experiments/live-solver/rsa-v3/`
- v2 public runner: `research/06-cryptology-rsa/experiments/live-solver/rsa-v2/`
- story-law obligations: `research/06-cryptology-rsa/experiments/proof-workbenches/rsa-v2/`
- QU packet only: `research/06-cryptology-rsa/experiments/live-solver/qu-certificate-to-factor-map/`

## Goal

Flesh out the live solver as a PGS-native engine on public RSA moduli: locked endpoint chain, floor transport through `N`, reciprocal closure, GWR-carrier transport, then a **structural certificate or a named residual**. Audit confirmation stays a downstream column. Scale work measures residual histograms on named surfaces. Promotion waits on transported-story-law obligations.

## Governing contracts

- `AGENTS.md` (repo): PGS-first frame; theorem / measured / audit / unresolved split; no classical primality or factor gates as inference; Grok may not declare RSA-scale resolution
- `research/06-cryptology-rsa/experiments/AGENTS.md`: live inference starts in `live-solver/rsa-v2/`; sidecars stay sidecars; QU packet stays out of `resolver.py` and `PROOF.md`
- v2 `README.md` next live work: transported-story-law obligations; unresolved geometry stays unresolved until those lemmas exist
- Continuity: `research/00-index/continuity/notes/ACTIVE_GOAL_50bit_residual_discriminator.md`

Status words allowed in this plan and its later reports: theorem, finite-certified premise, implementation, measured-on-regime-only, hypothesis-gate, audit-confirms, unresolved.

## Non-goals

- No metric whose numerator is “exposed factor pair”
- No writing a factor-favor rate into `ALGORITHM.md`
- No treating v2 runner rows, v3 probe rows, and v3 corpora as one ladder
- No installing QU-named public pairs as a candidate rule in `resolver.py`
- No `PROOF.md` edits from measured results
- No program-level verified or validated language (no executed `10^18` surface on this track)

## Current state, pinned (read 2026-08-21 off-disk)

| Item | Status | Location of truth |
| --- | --- | --- |
| v3 resolver core | implementation, live | `live-solver/rsa-v3/resolver.py`, `algorithm_version = pgs_rsa_endpoint_resolver_v3.1`, `rule_id = reciprocal_pgs_gwr_carrier_transport_v3` |
| 40-bit v3 golden | resolved (historical golden) | `live-solver/rsa-v3/fixtures/golden_40bit_structural_certificate.json` |
| 50-bit v3 probe | measured-on-regime-only / hypothesis; carrier reciprocal closure finds public pair `(32047633, 32059651)` with `N//L == U` and `N//U == L`; first-tail window fixed `[-12, 6]`; historical false class blocked | `live-solver/rsa-v3/residual_discriminator_v2/probe_c1t2l1_v3_resolve.py`; `live-solver/rsa-v3/output/DOCUMENTATION_LOCK_50BIT_V3.md` |
| 64-bit v2 runner | endpoint class by mutual certificate closure; downstream audit reports factor found on that row | `live-solver/rsa-v2/README.md` |
| v3 corpora | ready, separate from v2 ladder | `live-solver/rsa-v3/corpora/corpus_128bit.jsonl`, `corpus_256bit.jsonl`, `corpus_512bit.jsonl`, `GENERATION_RECIPE.json` |
| Transported-story-law obligations | unproved; named blocker for promotion | v2 `README.md` “Next Live Work”; `experiments/proof-workbenches/rsa-v2/` |
| First-tail obstruction | residual class on 50-bit decision path before V3 resolve; D holds as fixture gate only; dual-gap constants are hypothesis gates | `ACTIVE_GOAL_50bit_residual_discriminator.md`; prediction inventory H1/H2/H3 |
| QU packet | frozen, QU-only | `qu-certificate-to-factor-map/PACKET.md`, `frozen_public_rungs.json` |

## What gets measured (replaces factor-favor rate)

Per named surface (one engine, one corpus, one run):

1. Residual histogram: count of each residual code plus certificate-class codes from `RESIDUAL_TAXONOMY.md`
2. Certificate emission count (structural certificate rows)
3. Downstream audit column, physically separate: `factor_found` true / false / not-run

Those three stay three columns. A residual-labeled row is unresolved, never a miss against a factor target.

## Phases

Do not start a later phase until its gate is met.

### Phase 1. Freeze committed surfaces

**Gate to start:** none (current pin)

Tasks:

1. Reproduce v2 live surface from repo root: `data-ladder/rsa-v2/build_ladder_fixtures.py`, `live-solver/rsa-v2/run_experiment.py`, `live-solver/rsa-v2/audit_experiment.py`
2. Reproduce v3 regression: `live-solver/rsa-v3/run_resolver.py` on `fixtures/regression_cases.jsonl`, then `verifier.py` on emitted certificates
3. Hash-pin outputs under `live-solver/rsa-v3/output/freeze_YYYYMMDD/` and a sibling v2 freeze dir under `live-solver/rsa-v2/output/` if that tree already holds run artifacts; do not invent a new cell
4. Confirm existing anti-admission test still blocks historical false class `(32047651, 32059633)`

Exit: freeze commit; v2 and v3 freezes labeled as **separate** surfaces; no new metric in `ALGORITHM.md`

### Phase 2. Transported-story-law obligations

**Gate to start:** Phase 1 freeze exists

This is the next live mathematical work named by v2.

Tasks:

1. Inventory every obligation doc under `experiments/proof-workbenches/rsa-v2/`
2. For each obligation record: statement, dependencies, finite-certifiable or open-analytic, kill condition
3. Finite-certifiable items: emit certificates with pinned hashes on the existing certificate path; add replay to CI
4. Open-analytic items: lemma shells in PGS objects (reset certificates, floor transport, reciprocal closure, carrier) with scope naming the exact rung class covered

Exit: each obligation is finite-certified, proved-with-review, or a hypothesis-gate with a kill condition. Silent assumptions are named. Phase 5 stays blocked until at least one law-grade invariant exists.

### Phase 3. First-tail obstruction

**Gate to start:** Phase 2 inventory exists (full closure of every lemma is not required; the named residual must sit next to named obligations)

Tasks:

1. Run `live-solver/rsa-v3/test_h2_constant_sweep.py` on the 40-bit and 50-bit v3 fixtures with windows **fixed**
2. Repeat with widened windows only as a labeled contrast run; residual codes on the fixed-window ledger stay unchanged
3. Name two candidate invariants for tail alignment under floor transport, each with a kill condition and the fixture that would kill it
4. QU packet reuse is optional and operator-gated: object is frozen public `N` plus first-tail residuals; question is a PGS-native law for tail alignment under floor transport; Hermes may keep the answer as research notes in the QU cell. QU does not name pairs for install

Exit: obstruction labeled as measured geometry plus candidate invariant, or as widening-only artifact. `residual.py` windows stay fixed unless Phase 2 supplies a law to install.

### Phase 4. Measured residual histograms on named corpora

**Gate to start:** Phase 1 freeze exists. Phase 2 and 3 may still be open. This phase **measures**; it does not promote.

Tasks:

1. Run v3 resolver on `corpus_128bit.jsonl`, then `corpus_256bit.jsonl`, each as its own report
2. Record the three-column measured table (residual histogram, certificate count, audit column)
3. Write reports under `live-solver/rsa-v3/output/scale_ladder_2026-08/` with exact commands, corpus hashes, status **measured-on-regime-only**
4. Keep v2 64-bit runner results in v2 reports. Do not plot v2 64-bit, v3 50-bit, and v3 128-bit as one curve

Exit: one honest report per corpus, or a named residual class showing where closure fails. Breakdown is a valid exit.

### Phase 5. Candidate-rule merge (law-gated)

**Gate to start:** Phase 2 names at least one law-grade invariant that explains observed closures. Phase 3 has named the first-tail obstruction. Otherwise this phase produces research notes only.

Protocol:

1. A candidate rule comes from a Phase 2 lemma or a Phase 3 invariant, written in PGS objects
2. Hermes may install it behind a flag in `live-solver/rsa-v3/resolver.py`, guarded by anti-admission tests and a regression pin for every previously resolved v3 rung
3. Downstream audit runs on new rows; `factor_found = true` under unchanged public geometry is confirmation, not the install criterion
4. QU packet answers stay in the QU cell. They may motivate a lemma statement. They are not a pair list to paste into the resolver
5. Promotion toward theorem follows the human-approved process in `AGENTS.md`

## Risks

| Risk | Watch for | Contract response |
| --- | --- | --- |
| Search-for-factors metric returns | numerator is pair exposure or audit hits | keep residual histogram as the inference score |
| Mixed-engine chart | one table spanning v2 runner and v3 corpora | one engine per report |
| QU pair list becomes inference | `resolver.py` gains named `(L, U)` from PACKET.md | packet stays QU-only; install path is a lemma, then a flag |
| Window retune dressed as closure | residual code changes after a wider first-tail window | H2: pass must hold under the locked `[-12, 6]` window |
| Verified language on local corpora | report title says validated | measured-on-regime-only until a `10^18` surface exists |

## Open question for operator

Phase 4 corpora include 512-bit. This plan stops the first measured pass at 256-bit so the residual ledger stays readable. Say if 512-bit should join that first pass.

## File placement

- This plan: `docs/plans/rsa_live_solver_endpoint_closure_plan.md`
- Withdrawn draft: `docs/plans/rsa_live_solver_factor_favoring_plan.md` (delete on adopt)
- Phase outputs stay in existing cells: `live-solver/rsa-v3/output/`, `live-solver/rsa-v2/`, `proof-workbenches/rsa-v2/`, `qu-certificate-to-factor-map/`
