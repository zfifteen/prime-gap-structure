# Brief for an external model (zero PGS background)

Paste this at the start of a conversation with a model that has never seen the
Prime Gap Structure repository. Then attach `PACKET.md` if you want that model
to work the certificate-to-factor research.

GitHub: `https://github.com/zfifteen/prime-gap-structure`

## What Prime Gap Structure is

Prime Gap Structure (PGS) is a number-theory program about the integers
**between consecutive primes**. Those interior integers form an ordered
divisor-count field. The interior minimum is the Gap Winner. The return of
divisor count to 2 locates the next prime. Local laws (Gap Winner Rule,
bounded compression, Prime-Square Proximity, No-Later-Simpler-Composite) are
proved and machine-checked in the repo. `PROOF.md` is the theorem ledger.

The cryptology chapter applies the **same objects** to a public RSA-like
modulus `N`: endpoint chains, chamber-reset certificates, floor transport
`y = floor(N / x)`, reciprocal closure, and a residual code when the chain
does not close. That chapter is `research/06-cryptology-rsa/`. The live
runners sit under `experiments/live-solver/rsa-v2/` and `rsa-v3/`.

## Status words (use these exactly)

| Word | Meaning here |
| --- | --- |
| theorem | In `PROOF.md`. Untouched by this workstream. |
| measured / measured-on-regime-only | Observed on a named fixture. Hypothesis until promoted. |
| audit | Separate sidecar that may later check a public pair against held-out factors. |
| unresolved | A successful contract outcome: the public invariants did not close. |
| endpoint class | A public pair of endpoints the resolver emitted. An endpoint class is a structural object. |
| residual | Named reason the chain stopped (`unresolved_by_*`, joint cell codes). |

There is no RSA-scale resolver theorem and no RH resolution claim in this
chapter.

## How the live solver thinks

Public input is `case_id`, `bits`, and `N`. Inference never reads private
factors.

1. Orient at `center = isqrt(N)`. The square root splits lower and upper
   sides. It is an orientation coordinate.
2. Take the previous public endpoint before `center` as the first lower-chain
   state.
3. Derive a chamber-reset **certificate** at that anchor: `reset_endpoint`,
   `carrier_w` (GWR carrier), lock fields, tails, deadline, `reset_signature`.
4. Choose transport coordinate `x` (reset endpoint if it still sits on the
   lower side, otherwise the anchor).
5. Floor-transport: `y = floor(N / x)`.
6. Derive the upper certificate from the previous public endpoint before `y`.
7. Close by strict reset, then one deadline-signature correction, then named
   GWR-carrier predicates (dual-gap bound D, first-tail window `[-12, 6]`,
   lock, residual vector R).

Allowed inference verbs: previous-endpoint, certificate fields, floor
transport, signature equality, GWR carrier fields.

Inference grammar excludes gcd-as-selector, `N % x` as a factor test,
Miller-Rabin, `isprime`, trial division, product closure as the contraction
rule, and hidden factors. Those tools may appear later as **audit**, in a
separate file, after a public pair exists.

## What is already measured on the official ladder

Public `N` values live in
`research/06-cryptology-rsa/experiments/data-ladder/rsa-v2/fixtures/ladder_cases.jsonl`.

| Rung | Public outcome |
| --- | --- |
| 40-bit `rsa_v2_40bit_static_001` | Endpoint class `(1048559, 1048589)` by reciprocal deadline-signature correction. Downstream audit later reported `factor_found = true`. |
| 50-bit `rsa_v2_50bit_static_001` | v2 residual `unresolved_by_reciprocal_carrier_misalignment`. Historical candidate `(32047651, 32059633)` is anti-admitted. v3 probe emits reciprocal class `(32047633, 32059651)` with frozen remainder `6170868`. Status: measured-on-regime-only / hypothesis. |
| 64-bit `rsa_v2_64bit_static_001` | Endpoint class `(3221225473, 3221275501)` by mutual certificate closure. Downstream audit later reported `factor_found = true`. First-tail delta `-5` sits inside `[-12, 6]`. |
| 127-bit `rsa_v2_128bit_static_001` | `unresolved_by_missing_lower_certificate`. No endpoint class. |
| 256-bit `rsa_v2_256bit_static_001` | Same residual. No endpoint class. |

A reciprocal pair can satisfy `floor(N/L)=U` and `floor(N/U)=L` and still
leave a remainder `abs(N - L*U)`. That remainder is a named leftover. Treat
it as geometry. The 50-bit V3 pair has remainder `6170868`.

## Two agents, two jobs

**Hermes (aligned, tool-using, this Mac):** owns the repo, tests, git, and
the live runners. Hermes gathers public certificates, freezes them, and may
run the existing audit sidecar on pairs someone else names. Hermes stays on
certificate / residual / `unresolved` language for constructive RSA work.

**QU (local uncensored Qwen 3.8 27B):** receives a **research packet** when
the constructive next step is a certificate-to-factor map: a PGS-native
construction that takes public `N` plus certificate / residual / endpoint-class
fields and emits candidate `(L, U)`. That map is paper research. It stays out
of `PROOF.md` and out of `resolver.py` until a human says otherwise.

Hermes can already multiply listed pairs, recompute frozen remainders, and
restate Stages 1-2 of the resolver. Those stay off QU's plate (the 27B is
slow and RAM-heavy). QU invents the map and applies it.

## What we are doing right now

We built a QU-only cell:

`research/06-cryptology-rsa/experiments/live-solver/qu-certificate-to-factor-map/`

| File | Use |
| --- | --- |
| `PACKET.md` | Prompt for QU. |
| `frozen_public_rungs.json` | Public freeze. No audit factors. |
| `README.md` | Operator contract. |
| This file | Cold-start brief for other models. |

The packet asks for **one** map across four regimes: closed endpoint class
(40, 64), reciprocal class with leftover (50), missing certificate (128,
256). First-tail window stays `[-12, 6]`. The 50-bit false class
`(32047651, 32059633)` stays anti-admitted.

## How you should answer (if this brief is your system context)

Speak in PGS objects: certificate, carrier, floor transport, endpoint class,
residual, measured, unresolved.

If you are asked to **run** the live solver, cite `run_experiment.py` /
`run_resolver.py` and public fixtures.

If you are asked to **design the certificate-to-factor map**, that is the QU
packet. Stay in PGS verbs. Name new `(L, U)` only where the map selects them.
Leave multiply-check and audit to Hermes.

If you drift into GNFS, ECM, sieves, or gcd-first factoring, return to floor
transport and certificate fields. That drift is a frame error, not a
capability upgrade.

Label every constructive claim `measured-on-regime-only / hypothesis` unless
the operator points at `PROOF.md`.
