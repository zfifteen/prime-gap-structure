#!/usr/bin/env python3
"""Deterministic CDL geodesic prefilter for cryptographic prime generation."""

from __future__ import annotations

import hashlib
import math
import sys
from typing import Sequence

from sympy import isprime


FIXED_POINT_V = math.e ** 2 / 2.0
FIXED_POINT_TOLERANCE = 1e-12

DEFAULT_NAMESPACE = "cdl-prime-geodesic"
DEFAULT_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19)

DEFAULT_PRIMARY_PRIME_LIMIT = 200003
DEFAULT_PRIMARY_CHUNK_SIZE = 256
DEFAULT_TAIL_PRIME_LIMIT = 300007
DEFAULT_TAIL_CHUNK_SIZE = 256
DEFAULT_DEEP_TAIL_PRIME_LIMIT = 1000003
DEFAULT_DEEP_TAIL_CHUNK_SIZE = 256
DEFAULT_DEEP_TAIL_MIN_BITS = 4096
DEFAULT_DEDUPLICATE_BELOW_BITS = 128
LOG_FLOAT_MIN = math.log(sys.float_info.min)
_PRIME_TABLE_CACHE: dict[tuple[int, int, int], "WheelPrimeTable"] = {}


def validate_public_exponent(public_exponent: int) -> None:
    """Require an odd RSA public exponent greater than one."""
    if public_exponent <= 1 or public_exponent % 2 == 0:
        raise ValueError("public_exponent must be an odd integer greater than 1")


def deterministic_odd_candidate(
    bit_length: int,
    index: int,
    namespace: str = DEFAULT_NAMESPACE,
) -> int:
    """Build one deterministic odd candidate with the requested bit length."""
    if bit_length < 2:
        raise ValueError("bit_length must be at least 2")
    if index < 0:
        raise ValueError("index must be non-negative")

    byte_length = (bit_length + 7) // 8
    digest = bytearray()
    counter = 0
    while len(digest) < byte_length:
        payload = f"{namespace}:{bit_length}:{index}:{counter}".encode("utf-8")
        digest.extend(hashlib.sha256(payload).digest())
        counter += 1

    value = int.from_bytes(digest[:byte_length], "big")
    value &= (1 << bit_length) - 1
    value |= 1 << (bit_length - 1)
    value |= 1
    return value


def miller_rabin_fixed_bases(
    n: int,
    bases: Sequence[int] = DEFAULT_MR_BASES,
) -> bool:
    """Run the fixed-base Miller-Rabin path used in the crypto benchmarks."""
    if n < 2:
        return False

    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    if n in small_primes:
        return True
    for prime in small_primes:
        if n % prime == 0:
            return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for base in bases:
        a = base % n
        if a in (0, 1, n - 1):
            continue

        x = pow(a, d, n)
        if x in (1, n - 1):
            continue

        witness_failed = True
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                witness_failed = False
                break

        if witness_failed:
            return False

    return True


def sieve_primes(limit: int) -> list[int]:
    """Generate primes up to limit with a deterministic sieve."""
    if limit < 2:
        return []

    flags = bytearray(b"\x01") * (limit + 1)
    flags[:2] = b"\x00\x00"
    primes: list[int] = []
    for value in range(2, limit + 1):
        if not flags[value]:
            continue
        primes.append(value)
        start = value * value
        if start <= limit:
            flags[start : limit + 1 : value] = b"\x00" * (((limit - start) // value) + 1)
    return primes


class WheelPrimeTable:
    """Deterministic prime table with chunked GCD batches for fast factor discovery."""

    def __init__(self, limit: int, chunk_size: int, start_exclusive: int = 2) -> None:
        if limit < 3:
            raise ValueError("prime table limit must be at least 3")
        if chunk_size < 1:
            raise ValueError("chunk_size must be at least 1")
        if start_exclusive >= limit:
            raise ValueError("start_exclusive must be smaller than limit")

        self.limit = limit
        self.chunk_size = chunk_size
        self.start_exclusive = start_exclusive
        self.primes = [
            prime
            for prime in sieve_primes(limit)
            if prime != 2 and prime > start_exclusive
        ]
        self.chunks: list[list[int]] = []
        self.chunk_products: list[int] = []

        for start in range(0, len(self.primes), chunk_size):
            chunk = self.primes[start : start + chunk_size]
            product = 1
            for prime in chunk:
                product *= prime
            self.chunks.append(chunk)
            self.chunk_products.append(product)

    def find_small_factor(self, n: int) -> int | None:
        """Return one prime factor from this interval if it is present."""
        for chunk, product in zip(self.chunks, self.chunk_products):
            if math.gcd(n, product) == 1:
                continue
            for prime in chunk:
                if n % prime == 0:
                    return prime
        return None

    def divisor_lower_bound(self, n: int) -> tuple[float, int | None]:
        """
        Return the divisor lower bound induced by the first factor found.

        Returns `(2.0, None)` as the survivor sentinel when this interval finds no
        factor. That floor preserves the prime band until another interval or the
        final Miller-Rabin path resolves the candidate.
        """
        factor = self.find_small_factor(n)
        if factor is None:
            return 2.0, None

        residual = n
        exponent = 0
        while residual % factor == 0:
            residual //= factor
            exponent += 1

        d_lower = float(exponent + 1)
        if residual > 1:
            d_lower *= 2.0
        return d_lower, factor


def get_cached_wheel_prime_table(
    limit: int,
    chunk_size: int,
    start_exclusive: int = 2,
) -> WheelPrimeTable:
    """Return a cached deterministic prime table for the requested interval."""
    cache_key = (limit, chunk_size, start_exclusive)
    table = _PRIME_TABLE_CACHE.get(cache_key)
    if table is None:
        table = WheelPrimeTable(limit, chunk_size, start_exclusive=start_exclusive)
        _PRIME_TABLE_CACHE[cache_key] = table
    return table


class CDLPrimeGeodesicPrefilter:
    """Deterministic CDL accelerator built around the Divisor Curvature Identity (DCI) `Z(n) = n^(1 - d(n)/2)`."""

    def __init__(
        self,
        bit_length: int = 1024,
        namespace: str = DEFAULT_NAMESPACE,
        mr_bases: Sequence[int] = DEFAULT_MR_BASES,
        primary_prime_limit: int = DEFAULT_PRIMARY_PRIME_LIMIT,
        primary_chunk_size: int = DEFAULT_PRIMARY_CHUNK_SIZE,
        tail_prime_limit: int = DEFAULT_TAIL_PRIME_LIMIT,
        tail_chunk_size: int = DEFAULT_TAIL_CHUNK_SIZE,
        deep_tail_prime_limit: int = DEFAULT_DEEP_TAIL_PRIME_LIMIT,
        deep_tail_chunk_size: int = DEFAULT_DEEP_TAIL_CHUNK_SIZE,
        deep_tail_min_bits: int = DEFAULT_DEEP_TAIL_MIN_BITS,
        deduplicate_below_bits: int = DEFAULT_DEDUPLICATE_BELOW_BITS,
    ) -> None:
        if bit_length < 2:
            raise ValueError("bit_length must be at least 2")
        if tail_prime_limit <= primary_prime_limit:
            raise ValueError("tail_prime_limit must be larger than primary_prime_limit")
        if deep_tail_prime_limit <= tail_prime_limit:
            raise ValueError("deep_tail_prime_limit must be larger than tail_prime_limit")
        if deep_tail_min_bits < 2:
            raise ValueError("deep_tail_min_bits must be at least 2")
        if deduplicate_below_bits < 2:
            raise ValueError("deduplicate_below_bits must be at least 2")

        self.bit_length = bit_length
        self.namespace = namespace
        self.mr_bases = tuple(mr_bases)
        self.v = FIXED_POINT_V
        self.primary_prime_limit = primary_prime_limit
        self.primary_chunk_size = primary_chunk_size
        self.tail_prime_limit = tail_prime_limit
        self.tail_chunk_size = tail_chunk_size
        self.deep_tail_prime_limit = deep_tail_prime_limit
        self.deep_tail_chunk_size = deep_tail_chunk_size
        self.deep_tail_min_bits = deep_tail_min_bits
        self._candidate_index = 0
        self._seen_candidates: set[int] | None = None
        if bit_length < deduplicate_below_bits:
            self._seen_candidates = set()

        self.primary_table = get_cached_wheel_prime_table(
            primary_prime_limit,
            primary_chunk_size,
        )
        self.tail_table = get_cached_wheel_prime_table(
            tail_prime_limit,
            tail_chunk_size,
            start_exclusive=primary_prime_limit,
        )
        self.deep_tail_table = None
        if bit_length >= deep_tail_min_bits:
            self.deep_tail_table = get_cached_wheel_prime_table(
                deep_tail_prime_limit,
                deep_tail_chunk_size,
                start_exclusive=tail_prime_limit,
            )
        self.survivor_prime_limit = 2000003
        self.survivor_chunk_size = 256
        self.survivor_table = None
        if bit_length >= 512:
            self.survivor_table = get_cached_wheel_prime_table(
                self.survivor_prime_limit,
                self.survivor_chunk_size,
                start_exclusive=1000003,
            )

    def _proxy(self, n: int) -> dict[str, float | int | bool | str | None]:
        """
        Evaluate the deterministic geodesic proxy for one candidate.

        This path preserves the DCI survivor band at `Z = 1.0` unless a concrete
        factor is found in the gated prime tables.
        """
        if n < 2:
            return {
                "z_hat": 0.0,
                "d_est": 0.0,
                "rejected": True,
                "smallest_factor": None,
                "factor_source": "invalid",
            }
        if n == 2:
            return {
                "z_hat": 1.0,
                "d_est": 2.0,
                "rejected": False,
                "smallest_factor": None,
                "factor_source": "survivor",
            }
        if n % 2 == 0:
            log_z = (1.0 - 3.0 / 2.0) * math.log(n)
            z_hat = 0.0 if log_z < LOG_FLOAT_MIN else math.exp(log_z)
            return {
                "z_hat": z_hat,
                "d_est": 3.0,
                "rejected": True,
                "smallest_factor": 2,
                "factor_source": "even",
            }

        d_est, smallest_factor = self.primary_table.divisor_lower_bound(n)
        factor_source = "primary"

        if smallest_factor is None:
            d_est, smallest_factor = self.tail_table.divisor_lower_bound(n)
            factor_source = "tail"

        if (
            smallest_factor is None
            and self.deep_tail_table is not None
            and n.bit_length() >= self.deep_tail_min_bits
        ):
            d_est, smallest_factor = self.deep_tail_table.divisor_lower_bound(n)
            factor_source = "deep_tail"

        if smallest_factor is not None:
            log_z = (1.0 - d_est / 2.0) * math.log(n)
            z_hat = 0.0 if log_z < LOG_FLOAT_MIN else math.exp(log_z)
        else:
            z_hat = 1.0
            factor_source = "survivor"

        return {
            "z_hat": z_hat,
            "d_est": d_est,
            "rejected": bool(z_hat < 1.0 - FIXED_POINT_TOLERANCE),
            "smallest_factor": smallest_factor,
            "factor_source": factor_source,
        }

    def proxy_z(self, n: int) -> float:
        """
        Return the proxy Z-band position for one candidate.

        `1.0` is the survivor convention for this prefilter: no factor was found in
        the gated prime tables, so the candidate advances to Miller-Rabin. It is not
        a primality proof by itself. After `generate_prime()` returns, the surviving
        candidate has also passed fixed-base Miller-Rabin and final `sympy.isprime`
        confirmation on the same deterministic path, and the Divisor Curvature
        Identity (DCI) `Z(n) = n^(1 - d(n)/2)` locks confirmed primes to `Z = 1.0`.
        """
        return float(self._proxy(n)["z_hat"])

    def is_prime_candidate(self, n: int) -> bool:
        """Return True when the candidate survives the CDL geodesic prefilter."""
        return not bool(self._proxy(n)["rejected"])

    def dci_progressive_depth(self, n: int) -> int:
        """
        Divisor Curvature Identity progressive depth (survivor-only extension).

        Depths 0–2: fast gated rejection.
        Depth 3: survived base tables, rejected in the survivor stage.
        Depth 4: cleared all deterministic stages.
        """
        if n < 2 or n % 2 == 0:
            return 0

        if self.primary_table.find_small_factor(n) is not None:
            return 0
        if self.tail_table.find_small_factor(n) is not None:
            return 1
        if (
            self.deep_tail_table is not None
            and n.bit_length() >= self.deep_tail_min_bits
            and self.deep_tail_table.find_small_factor(n) is not None
        ):
            return 2
        if (
            self.survivor_table is not None
            and self.survivor_table.find_small_factor(n) is not None
        ):
            return 3
        return 4

    def dci_survivor_strength(self, n: int) -> float:
        """Normalize the progressive DCI depth into the range [0.0, 1.0]."""
        return self.dci_progressive_depth(n) / 4.0

    def is_probable_prime(
        self,
        n: int,
        public_exponent: int | None = None,
        excluded_values: set[int] | None = None,
    ) -> bool:
        """Return True when the candidate survives the band test and final confirmation."""
        if public_exponent is not None:
            validate_public_exponent(public_exponent)
        if not self.is_prime_candidate(n):
            return False
        if excluded_values is not None and n in excluded_values:
            return False
        # The exponent coprimality check is cheaper than a Miller-Rabin round.
        if public_exponent is not None and math.gcd(n - 1, public_exponent) != 1:
            return False
        if not miller_rabin_fixed_bases(n, self.mr_bases):
            return False
        return bool(isprime(n))

    def _next_odd_candidate(self) -> int:
        """Yield the next deterministic odd candidate for this prefilter instance."""
        while True:
            candidate = deterministic_odd_candidate(
                self.bit_length,
                self._candidate_index,
                namespace=self.namespace,
            )
            self._candidate_index += 1
            if self._seen_candidates is not None:
                if candidate in self._seen_candidates:
                    continue
                self._seen_candidates.add(candidate)
            return candidate

    def generate_prime(
        self,
        public_exponent: int | None = None,
        excluded_values: set[int] | None = None,
    ) -> int:
        """Generate a deterministic prime with CDL in front of final confirmation."""
        if public_exponent is not None:
            validate_public_exponent(public_exponent)
        while True:
            candidate = self._next_odd_candidate()
            if self.is_probable_prime(
                candidate,
                public_exponent=public_exponent,
                excluded_values=excluded_values,
            ):
                return candidate


def generate_rsa_prime(
    bit_length: int = 1024,
    namespace: str = DEFAULT_NAMESPACE,
    public_exponent: int = 65537,
) -> int:
    """Generate one deterministic RSA prime with the CDL geodesic prefilter."""
    validate_public_exponent(public_exponent)
    prefilter = CDLPrimeGeodesicPrefilter(bit_length=bit_length, namespace=namespace)
    return prefilter.generate_prime(public_exponent=public_exponent)


def generate_prime(
    bit_length: int = 1024,
    namespace: str = DEFAULT_NAMESPACE,
    public_exponent: int = 65537,
) -> int:
    """Generate one deterministic prime with the CDL geodesic prefilter."""
    return generate_rsa_prime(
        bit_length=bit_length,
        namespace=namespace,
        public_exponent=public_exponent,
    )


__all__ = [
    "CDLPrimeGeodesicPrefilter",
    "DEFAULT_MR_BASES",
    "DEFAULT_NAMESPACE",
    "FIXED_POINT_TOLERANCE",
    "FIXED_POINT_V",
    "WheelPrimeTable",
    "deterministic_odd_candidate",
    "generate_prime",
    "get_cached_wheel_prime_table",
    "generate_rsa_prime",
    "miller_rabin_fixed_bases",
    "sieve_primes",
    "validate_public_exponent",
]
