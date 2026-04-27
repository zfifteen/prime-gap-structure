# GPE Development Roadmap

This roadmap turns the blocker analysis in
[`gpe_blocker_resolution.md`](./gpe_blocker_resolution.md) into a staged
development plan for the GWR-DNI Generative Prime Engine.

The requirements are not reduced. Each milestone exists to remove one blocker
standing between the current exact DNI/GWR oracle and the GPE target contract:
a deterministic prime emitter driven by the rulebook rather than by traditional
candidate primality tests.

## Roadmap Table

| Milestone | Blocker Resolved | Requirement Document | Required Outcome |
|---:|---|---|---|
| 1 | Winner is not the endpoint | [Endpoint Selector Requirements](./gpe_milestone_01_boundary_selector_requirements.md) | Replace `winner + 1` with an explicit exact endpoint-selector contract. |
| 2 | NLSC gives a ceiling, not a selector | [NLSC Selector Requirements](./gpe_milestone_02_nlsc_selector_requirements.md) | Refine the NLSC threat horizon into branch-specific exact next-prime selection. |
| 3 | Reduced state is not deterministic enough | [State Refinement Requirements](./gpe_milestone_03_state_refinement_requirements.md) | Find the minimal state needed to make the next-prime selector single-valued. |
| 4 | Exact DNI evaluation uses the divisor field | [Zero-Test Arithmetic Requirements](./gpe_milestone_04_zero_test_arithmetic_requirements.md) | Replace hidden divisor-field or primality-test dependence with rulebook arithmetic. |

## Development Order

### Milestone 1: Endpoint Selector Contract

The current skeleton cannot emit `winner + 1`. The first milestone defines the
exact function shape:

$$q^+=B(q,S,w,d(w))$$

and establishes the validation harness that every later selector must satisfy.

This milestone does not try to solve every branch. It prevents the engine from
building on a false closure rule.

### Milestone 2: NLSC Selector

NLSC gives the invariant ceiling:

$$q^+ \le T_{<}(w)$$

For the dominant $d(w)=4$ branch, this becomes:

$$q^+ \le S_{+}(w)$$

The second milestone attacks the exact selector inside that interval, starting
with the dominant $d(w)=4$ branch.

### Milestone 3: State Refinement

The current 14-state reduced type is not enough to determine the next prime
offset. This milestone identifies the smallest additional state variables that
make the selector collision-free on the committed validation surface.

The goal is not a generalized state framework. The goal is the smallest
auditable state that makes $B(q,S,w,d(w))$ single-valued.

### Milestone 4: Zero-Test Arithmetic Path

The existing exact oracle reads the divisor field and detects the prime endpoint
with $d(n)=2$. The GPE target forbids hiding that dependency inside a new name.

The fourth milestone replaces the divisor-field dependency with deterministic
rulebook arithmetic, or else marks the remaining dependency as an unresolved
contract failure.

## Completion Standard

The roadmap is complete only when all four milestone requirement documents are
satisfied together:

- the emitted next-prime value is exact,
- the selector is single-valued under the chosen state,
- the NLSC ceiling is refined into equality,
- and the implementation path contains no hidden primality test, trial division
  of gap interiors, candidate sieve list, Miller-Rabin step, or Eratosthenes
  marking.

Until then, the current repo still has the exact DNI/GWR oracle, but not the GPE
target engine.
