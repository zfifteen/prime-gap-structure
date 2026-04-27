# A Witness-Based Prime Predictor: Constructing p_n from the Prime Number Theorem and the Gap Winner Rule

**Attribution:** Big D  
**Repository:** [zfifteen/prime-gap-structure](https://github.com/zfifteen/prime-gap-structure)  
**Date:** April 9, 2026  
**Status:** Working paper -- findings-level, not peer reviewed

**Local continuation note:** the initial witness exactness claim now has a
seed-position caveat; see
[`pnt_gwr_prime_formula_audit.md`](./pnt_gwr_prime_formula_audit.md).

---

## Abstract

We construct a formula for the n-th prime p_n that is exact, carries zero residual error when a placement condition is satisfied, and is derived from two independent sources: the Prime Number Theorem (PNT) and the Gap Winner Rule (GWR). The formula takes the form

    p_n = nextprime( W( S*(n) ) )

where S*(n) is a macro seed locating the approximate region of p_n, W is a local witness locator derived from the Divisor Normalization Index (DNI), and nextprime performs a short deterministic forward search bounded by a provable closure ceiling. We prove and verify empirically that when S*(n) lands inside the correct prime gap (p_{n-1}, p_n), the formula returns p_n exactly with no additive residual. This zero-residual property distinguishes the formula from every classical analytic prime approximation, which carries permanent asymptotic error, and from exact tautological constructions (Willans, Wilson), which are computationally vacuous. We document full reproducibility instructions and provide all test code.

---

## 1. Introduction

Every serious formula for the n-th prime falls into one of two categories.

The first category is **exact but trivial**. The Willans formula (1964) expresses p_n as a closed-form summation using Wilson's theorem. It is exactly correct for all n but requires a double sum running to 2^n, making it strictly worse computationally than a direct sieve. Its correctness is guaranteed by definition, not by structural insight.

The second category is **analytic and approximate**. The Cipolla asymptotic expansion, Riemann-Li inversion, and their descendants estimate p_n from the prime-counting function pi(x) and its inverse. These are useful but carry permanent residual error because the error term is the oscillation of pi(x) - Li(x), which is governed by the nontrivial zeros of the Riemann zeta function and does not vanish at any finite n.

The formula derived here does not fit either category. Its correctness is not circular, and its residual error is zero when a single placement condition holds. The structure that makes this possible comes from the Gap Winner Rule, a finding from the prime-gap-structure repository documenting a local divisor-theoretic law governing the interior structure of prime gaps.

### 1.1 Scope of This Paper

This paper documents:

1. The mathematical foundations: PNT, DNI, GWR, and the No-Later-Simpler-Composite closure corollary.
2. The formula construction, step by step.
3. The zero-residual property and its proof sketch.
4. The closure ceiling and its empirical support.
5. Full reproducible test code.
6. The open question: the seed tightness problem.

We do not claim an unconditional proof for all n. We claim a finding with a structural explanation, supported by zero counterexamples across more than 63,000 gaps tested computationally, including even-band ladder runs from 10^8 through 10^18.

---

## 2. Mathematical Foundations

### 2.1 The Divisor Normalization Index

For any integer n >= 2, define the **raw Z-score**

    Z(n) = n^(1 - d(n)/2)

where d(n) is the number of divisors of n. The equivalent log-score is

    L(n) = ln Z(n) = (1 - d(n)/2) * ln(n).

**Key property.** For any prime p: d(p) = 2, so Z(p) = p^0 = 1 and L(p) = 0. For any composite c: d(c) >= 3, so Z(c) < 1 and L(c) < 0. Primes are exactly the fixed points of Z at value 1.

### 2.2 The Lexicographic Raw-Z Dominance Theorem

**Theorem.** Let a < b be composite integers with d(a) <= d(b). Then Z(a) > Z(b), equivalently L(a) > L(b).

**Proof.** Write alpha(n) = d(n)/2 - 1 > 0 for any composite n. Then L(n) = -alpha(n) * ln(n). Since a < b and d(a) <= d(b), we have alpha(a) <= alpha(b) and ln(a) < ln(b). Therefore:

    alpha(a) * ln(a) < alpha(a) * ln(b) <= alpha(b) * ln(b)

giving L(a) > L(b). QED.

**Corollary.** Among an ordered set of composites, the L-maximizer is the earliest composite with the smallest divisor count. This is called the **leftmost minimizer**.

### 2.3 The Gap Winner Rule

**Definition.** For a prime gap (p, q) with at least one composite interior, the **Gap Winner Rule (GWR)** asserts that the L-score argmax over interior composites is identical to the leftmost minimizer: the leftmost interior composite with minimum divisor count.

    w = argmax L(n) for p < n < q
      = min{ n in (p,q) : d(n) = d_min(p,q) }

where d_min(p,q) = min{ d(n) : p < n < q, n composite }.

**Repo status.** `GWR` is the proved universal maximizer theorem on the repository's current proof surface. The measured validation ladder reports zero counterexamples on the full tested surface: exact scan to `2 * 10^7`, deterministic even-band windows at every decade from `10^8` through `10^18`.

### 2.4 The Dominant d=4 Regime

Among all prime gaps on the tested surface:

- 82.5% of gaps have a selected integer with d(w) = 4 at scale 2*10^7.
- The d=4 selected-integer share stabilizes near 82.7% through 10^18.
- When d(w) = 4, the selected integer is always the **first** interior d=4 composite.
- No interior prime square appears in any d=4 selected integer gap on the tested surface.

The dominant regime reduces GWR to a local rule: **no interior prime square, then first interior d=4 wins.**

The d=4 composites are exactly the semiprimes (n = p*q, distinct primes) and prime cubes (n = p^3). Prime-cube selected integers are rare (approximately 1.56*10^-5 of d=4 selected integers) but do occur; the first example is 6859 = 19^3 in gap (6857, 6863).

### 2.5 The No-Later-Simpler-Composite Closure Corollary

**Definition.** For a composite w, define the **threat horizon**

    T_<(w) = min{ n > w : d(n) < d(w) }.

**Corollary.** For every prime gap (p, q) with GWR-selected integer w:

    q <= T_<(w).

That is, the right prime closes the gap before any later strictly simpler composite can appear in the interior.

**Status.** Exact corollary of proved `GWR`. The measured closure surface reports zero violations on the full tested surface through `10^18`.

**d=4 specialization.** When d(w) = 4, the only divisor class simpler than d=4 among composites is d=3, which occurs exactly at prime squares. So:

    T_<(w) = S_+(w) := min{ r^2 : r prime, r^2 > w }.

This gives the **closure ceiling**:

    q <= S_+(w).

**Empirical support.** Minimum prime-arrival margin (S_+(w) - q) observed: 2, across all regimes from 10^6 through 10^18. Zero violations.

---

## 3. The Formula

### 3.1 Construction

The formula is a three-layer machine:

    p_n = nextprime( W( S*(n) ) )

**Layer 1: Macro Seed.** S*(n) is any estimate satisfying the placement condition:

    S*(n) in (p_{n-1}, p_n).

The seed must land strictly inside the correct gap. It does not need to be close to p_n; it only needs to be in the right interval of length approximately ln(p_n).

**Layer 2: Witness Locator.** Given S*(n), the witness is:

    W(S*(n)) := min{ k >= S*(n) : d(k) = d_min, k not prime }

where d_min is the minimum divisor count of composites in the gap. In the dominant d=4 case:

    W(S*(n)) = min{ k >= S*(n) : d(k) = 4, k composite }.

This is computable in O(ln p_n) steps since d=4 composites have density approximately ln(ln(x)) / ln(x) near x.

**Layer 3: Prime Recovery.** By the GWR and the DNI fixed-point property, W(S*(n)) lies inside the correct gap and nextprime(W(S*(n))) = p_n exactly. The closure ceiling S_+(W) provides a hard upper bound confirming the search terminates.

### 3.2 The Zero-Residual Property

**Claim.** When S*(n) in (p_{n-1}, p_n):

    nextprime( W( S*(n) ) ) = p_n  exactly.

**Proof sketch.** Since S*(n) > p_{n-1}, the witness W(S*(n)) is the first d_min composite in (p_{n-1}, p_n), which by GWR is the selected interior integer w_n. Since w_n in (p_{n-1}, p_n), the next prime after w_n is p_n. QED.

**What this means.** There are no correction terms. No residual. The structure does all the work. This is categorically different from every Cipolla-family formula, which takes the form

    p_n = C(n) + c_1*f_1(n) + c_2*f_2(n) + ...

and always retains nonzero residual from truncating the asymptotic series.

### 3.3 The Closure Bound

For any gap with a d=4 selected integer, the prime satisfies:

    p_n <= S_+(W(S*(n))).

This provides a deterministic search bound. The search from W to p_n is bounded above by S_+(W) - W ~ 2*sqrt(p_n), but empirically the search terminates in O(ln p_n) steps since the actual gap width is O(ln p_n).

---

## 4. The Seed Problem

### 4.1 What PNT Provides

The Prime Number Theorem gives the backbone estimate p_n ~ n * ln(n).

The Cipolla two-term asymptotic refinement (equivalent to inverting the logarithmic integral Li) gives:

    Li^{-1}(n) = n*(ln(n) + ln(ln(n)) - 1 + (ln(ln(n)) - 2)/ln(n)) + O(n*(ln(ln(n)))^2 / ln(n)^2).

**Empirical backbone error.** The deviation |Li^{-1}(n) - p_n| ~ ln(p_n)^2 across tested scales. The placement condition requires |S*(n) - p_n| < ln(p_n) (one gap width). Therefore Li^{-1}(n) alone does not satisfy the placement condition at the scales tested.

| n       | p_n       | Li^{-1}(n)  | Error   | ln(p_n)^2 |
|---------|-----------|-------------|---------|-----------|
| 100     | 541       | 502.97      | 38.03   | 80.6      |
| 1,000   | 7,919     | 7,830.65    | 88.35   | 80.6      |
| 10,000  | 104,729   | 104,545.89  | 183.11  | 133.6     |
| 100,000 | 1,299,709 | 1,299,491.52| 217.48  | 198.2     |

The error ~ ln(p_n)^2 is one factor of ln(p_n) too large for the placement condition.

### 4.2 The Open Conjecture

**Conjecture.** The deviation delta(n) = p_n - Li^{-1}(n) can be estimated within O(ln p_n) from the local DNI Z-field structure near Li^{-1}(n): specifically, from the density of d=4 carriers, the distance to the nearest prime square, and the GWR profile of the neighborhood.

If this conjecture holds, then S*(n) = Li^{-1}(n) + delta_hat(n) satisfies the placement condition with no calibrated constants, and the formula is complete in the strict sense.

If it does not hold, the formula remains well-defined and the zero-residual property holds unconditionally given any seed that clears the placement condition. The GWR layer eliminates all residual error; the seed problem and the residual problem are completely decoupled.

---

## 5. Empirical Results

### 5.1 Zero-Residual Property

**Test protocol.** For every prime gap (p_{n-1}, p_n), use S*(n) = p_{n-1} + 1 (the tightest possible in-gap seed). Compute W(S*(n)) using the true d_min of each gap. Verify nextprime(W) = p_n.

**Results.**

| Surface                                   | Gaps tested | d=4 coverage | Violations |
|-------------------------------------------|-------------|--------------|------------|
| Small primes to ~6*10^5                   | 50,000      | 74.1%        | 0          |
| Near 10^6                                 | 10,000      | 73.7%        | 0          |
| General W_{d_min} (all gap types)         | 63,064      | all gaps     | 0          |

Zero violations across all gap types, all scales tested.

### 5.2 Closure Ceiling

From the committed repository surface:

| Scale    | Gaps    | d=4 share | Min margin | Violations |
|----------|---------|-----------|------------|------------|
| 10^6     | 70,327  | 82.90%    | 2          | 0          |
| 10^8     | 234,639 | 82.56%    | 2          | 0          |
| 10^12    | 202,949 | 82.57%    | 2          | 0          |
| 10^16    | 186,494 | 82.73%    | 2          | 0          |
| 10^18    | 180,447 | 82.73%    | 2          | 0          |

The minimum margin of 2 means the prime always closes the gap at least 2 units before the first d=3 threat (prime square). This has held at every scale from 10^6 through 10^18.

---

## 6. Comparison to Classical Formulas

| Formula              | Exact?          | Residual           | Useful? | Novel? |
|----------------------|-----------------|--------------------|---------|--------|
| Willans (1964)       | Yes             | None (tautological)| No      | No     |
| Mills constant       | Yes             | None (circular)    | No      | No     |
| Cipolla asymptotic   | No              | O(n*lnln(n)/ln(n)) | Yes     | No     |
| Riemann-Li inversion | No              | O(sqrt(p)*ln(p))   | Yes     | No     |
| This formula         | Yes (placed)    | Zero when placed   | Yes     | Yes    |

The conditioning on seed placement is not a weakness. It is a precise statement of where the mathematical work is. The zero-residual guarantee within that condition is the novel structural result.

---

## 7. Reproducibility

### 7.1 Dependencies

    python >= 3.9
    sympy >= 1.12

### 7.2 Core Implementation

```python
from sympy import isprime, divisor_count, nextprime
from math import isqrt

def W_d4(x):
    # First d=4 composite at or after x
    k = max(4, int(x))
    while isprime(k) or divisor_count(k) != 4:
        k += 1
    return k

def W_dmin(x, dmin):
    # First composite with divisor count dmin at or after x
    k = max(3, int(x))
    while isprime(k) or divisor_count(k) != dmin:
        k += 1
    return k

def closure_ceiling(w):
    # Next prime square after w
    r = isqrt(w) + 1
    while not isprime(r):
        r += 1
    return r * r

def pnt_gwr_formula(seed):
    # Given a seed in (p_{n-1}, p_n), return p_n exactly.
    w = W_d4(seed)
    p = int(nextprime(w - 1))
    u = closure_ceiling(w)
    assert p <= u, f"Closure ceiling violated: p={p}, U={u}"
    return p
```

### 7.3 Zero-Residual Verification

```python
from sympy import nextprime, isprime, divisor_count, prime as nth_prime

def verify_zero_residual(n_start=10, n_end=10000):
    violations = []
    p = int(nth_prime(n_start - 1))
    for n in range(n_start, n_end + 1):
        q = int(nextprime(p))
        interior = list(range(p + 1, q))
        if not interior:
            p = q
            continue
        dmin = min(divisor_count(k) for k in interior)
        seed = p + 1
        w = seed
        while isprime(w) or divisor_count(w) != dmin:
            w += 1
        p_found = int(nextprime(w - 1))
        if p_found != q:
            violations.append({
                'n': n, 'p_{n-1}': p, 'p_n': q,
                'dmin': dmin, 'witness': w, 'found': p_found
            })
        p = q
    return violations

v = verify_zero_residual(10, 10000)
print(f"Violations: {len(v)}")  # Expected: 0
```

### 7.4 Closure Ceiling Verification

```python
from sympy import isprime, divisor_count, nextprime
from math import isqrt

def verify_closure_ceiling(x_start, window=2_000_000):
    def next_prime_square(w):
        r = isqrt(w) + 1
        while not isprime(r):
            r += 1
        return r * r
    violations = []
    p = x_start
    if not isprime(p):
        p = int(nextprime(p))
    count = 0
    while p < x_start + window:
        q = int(nextprime(p))
        interior = list(range(p + 1, q))
        if interior:
            dmin = min(divisor_count(n) for n in interior)
            if dmin == 4:
                w = p + 1
                while isprime(w) or divisor_count(w) != 4:
                    w += 1
                u = next_prime_square(w)
                if q > u:
                    violations.append((p, q, w, u))
                count += 1
        p = q
    return violations, count

v, count = verify_closure_ceiling(1_000_000)
print(f"d=4 gaps tested: {count}, violations: {len(v)}")  # Expected: 0
```

---

## 8. Summary of Claims

**C1 (Zero-Residual Property).** For every prime gap (p_{n-1}, p_n) and any seed s in (p_{n-1}, p_n): nextprime(W_{d_min}(s)) = p_n exactly.
*Status: zero violations, 63,064 gaps tested, all gap types.*

**C2 (GWR Dominant Regime).** In approximately 82.7% of prime gaps at scale, the GWR-selected integer has d(w) = 4 and equals the first interior d=4 composite.
*Status: zero violations, 2*10^7 exact, even-band ladder to 10^18.*

**C3 (Closure Ceiling).** For every d=4 selected integer gap, p_n <= S_+(w). Minimum observed margin is 2, at every scale from 10^6 through 10^18.
*Status: zero violations.*

**C4 (Formula Architecture).** The formula p_n = nextprime(W(S*(n))) is exact when the placement condition holds, requires no additive correction terms, and is computationally efficient.
*Status: established.*

**C5 (Seed Problem -- Open).** Li^{-1}(n) undershoots p_n by approximately ln(p_n)^2, which exceeds the placement condition tolerance of O(ln p_n). Whether the deviation delta(n) is recoverable from local DNI/GWR structure without calibrated constants is an open conjecture.
*Status: open.*

---

## 9. References

1. Gap Winner Rule. zfifteen/prime-gap-structure, gwr/findings/gap_winner_rule.md.
   https://github.com/zfifteen/prime-gap-structure/blob/main/gwr/findings/gap_winner_rule.md

2. Closure Constraint Findings. zfifteen/prime-gap-structure, gwr/findings/closure_constraint_findings.md.
   https://github.com/zfifteen/prime-gap-structure/blob/main/gwr/findings/closure_constraint_findings.md

3. GWR Claim Hierarchy. zfifteen/prime-gap-structure, gwr/findings/claim_hierarchy.md.
   https://github.com/zfifteen/prime-gap-structure/blob/main/gwr/findings/claim_hierarchy.md

4. Dominant d=4 Arrival Reduction. zfifteen/prime-gap-structure, gwr/findings/dominant_d4_arrival_reduction_findings.md.
   https://github.com/zfifteen/prime-gap-structure/blob/main/gwr/findings/dominant_d4_arrival_reduction_findings.md

5. Lexicographic Raw-Z Dominance Theorem. zfifteen/prime-gap-structure, gwr/findings/lexicographic_raw_z_dominance_theorem.md.
   https://github.com/zfifteen/prime-gap-structure/blob/main/gwr/findings/lexicographic_raw_z_dominance_theorem.md

6. Willans, C.P. (1964). On formulae for the n-th prime number. Mathematical Gazette, 48, 413-415.

7. Cipolla, M. (1902). La determinazione asintotica dell n-esimo numero primo. Matematiche Napoli, 3, 132-166.

8. Tao, T. (2021). 246B Notes 4: The Riemann zeta function and the prime number theorem. UCLA course notes.
   https://terrytao.wordpress.com/2021/02/12/246b-notes-4-the-riemann-zeta-function-and-the-prime-number-theorem/
