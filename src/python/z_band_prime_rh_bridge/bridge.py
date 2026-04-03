"""Dirichlet-series helpers for the DNI-to-RH bridge."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

from mpmath import mp

from z_band_prime_invariant import FIXED_POINT_V


@dataclass(frozen=True)
class BridgeCoefficientRow:
    """One coefficient-side row in the DNI-to-RH bridge."""

    n: int
    divisor_count: int
    normalization_load_coefficient: float
    mangoldt: float
    scaled_bridge_coefficient: float
    convolution_value: float
    abs_error: float

    def to_dict(self) -> dict[str, int | float]:
        """Return a JSON-ready mapping."""
        return asdict(self)


@dataclass(frozen=True)
class PartialSumBridgeEvaluation:
    """One direct partial-sum evaluation of the DNI-to-RH bridge."""

    s: complex
    terms: int
    divisor_series: complex
    normalization_load_series: complex
    normalized_ratio: complex
    mangoldt_series: complex
    analytic_ratio: complex
    normalized_ratio_error: float
    mangoldt_series_error: float

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-ready mapping with printable complex values."""
        return {
            "s": str(self.s),
            "terms": self.terms,
            "divisor_series": str(self.divisor_series),
            "normalization_load_series": str(self.normalization_load_series),
            "normalized_ratio": str(self.normalized_ratio),
            "mangoldt_series": str(self.mangoldt_series),
            "analytic_ratio": str(self.analytic_ratio),
            "normalized_ratio_error": self.normalized_ratio_error,
            "mangoldt_series_error": self.mangoldt_series_error,
        }


@dataclass(frozen=True)
class AnalyticBridgeEvaluation:
    """One analytic evaluation of the continued DNI ratio."""

    s: complex
    divisor_series: complex
    normalization_load_series: complex
    normalized_ratio: complex
    zeta_log_derivative: complex
    abs_error: float

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-ready mapping with printable complex values."""
        return {
            "s": str(self.s),
            "divisor_series": str(self.divisor_series),
            "normalization_load_series": str(self.normalization_load_series),
            "normalized_ratio": str(self.normalized_ratio),
            "zeta_log_derivative": str(self.zeta_log_derivative),
            "abs_error": self.abs_error,
        }


def _smallest_prime_factors(limit: int) -> list[int]:
    """Build the smallest-prime-factor table up to one positive limit."""
    if limit < 1:
        raise ValueError("limit must be at least 1")

    table = list(range(limit + 1))
    table[1] = 1
    root = int(limit ** 0.5)
    for prime in range(2, root + 1):
        if table[prime] != prime:
            continue
        for multiple in range(prime * prime, limit + 1, prime):
            if table[multiple] == multiple:
                table[multiple] = prime
    return table


def divisor_counts_up_to(limit: int) -> tuple[int, ...]:
    """Return exact divisor counts from `0` through one positive limit."""
    factors = _smallest_prime_factors(limit)
    counts = [0] * (limit + 1)
    counts[1] = 1

    for n in range(2, limit + 1):
        prime = factors[n]
        residual = n
        exponent = 0
        while residual % prime == 0:
            residual //= prime
            exponent += 1
        counts[n] = counts[residual] * (exponent + 1)

    return tuple(counts)


def mangoldt_values_up_to(limit: int) -> tuple[float, ...]:
    """Return the von Mangoldt values from `0` through one positive limit."""
    factors = _smallest_prime_factors(limit)
    values = [0.0] * (limit + 1)

    for n in range(2, limit + 1):
        prime = factors[n]
        residual = n
        while residual % prime == 0:
            residual //= prime
        if residual == 1:
            values[n] = math.log(prime)

    return tuple(values)


def normalization_load_coefficients_up_to(
    limit: int,
    divisor_counts: tuple[int, ...] | None = None,
) -> tuple[float, ...]:
    """Return the DNI normalization-load coefficients from `0` through one positive limit."""
    counts = divisor_counts or divisor_counts_up_to(limit)
    if len(counts) != limit + 1:
        raise ValueError("divisor_counts must have length limit + 1")

    coefficients = [0.0] * (limit + 1)
    for n in range(2, limit + 1):
        coefficients[n] = counts[n] * math.log(n) / (math.e ** 2)
    return tuple(coefficients)


def dirichlet_convolution(
    left: tuple[int | float, ...],
    right: tuple[int | float, ...],
) -> tuple[float, ...]:
    """Return one finite Dirichlet convolution with index `0` left unused."""
    if len(left) != len(right):
        raise ValueError("left and right must have the same length")
    if len(left) < 2:
        raise ValueError("left and right must have at least two entries")

    limit = len(left) - 1
    values = [0.0] * (limit + 1)
    for divisor in range(1, limit + 1):
        left_value = left[divisor]
        if left_value == 0:
            continue
        for multiple in range(divisor, limit + 1, divisor):
            values[multiple] += float(left_value) * float(right[multiple // divisor])
    return tuple(values)


def build_bridge_rows(limit: int) -> list[BridgeCoefficientRow]:
    """Build the coefficient-side bridge rows up to one positive limit."""
    divisor_counts = divisor_counts_up_to(limit)
    mangoldt = mangoldt_values_up_to(limit)
    normalization_load = normalization_load_coefficients_up_to(limit, divisor_counts)
    convolution = dirichlet_convolution(divisor_counts, mangoldt)

    rows: list[BridgeCoefficientRow] = []
    for n in range(1, limit + 1):
        scaled_bridge_coefficient = FIXED_POINT_V * normalization_load[n]
        abs_error = abs(convolution[n] - scaled_bridge_coefficient)
        rows.append(
            BridgeCoefficientRow(
                n=n,
                divisor_count=divisor_counts[n],
                normalization_load_coefficient=normalization_load[n],
                mangoldt=mangoldt[n],
                scaled_bridge_coefficient=scaled_bridge_coefficient,
                convolution_value=convolution[n],
                abs_error=abs_error,
            )
        )
    return rows


def evaluate_partial_sum_bridge(
    s: complex | float,
    terms: int,
    dps: int = 50,
) -> PartialSumBridgeEvaluation:
    """Evaluate the bridge from direct Dirichlet partial sums on `Re(s) > 1`."""
    if terms < 1:
        raise ValueError("terms must be at least 1")
    if dps < 15:
        raise ValueError("dps must be at least 15")

    s_complex = complex(s)
    if s_complex.real <= 1.0:
        raise ValueError("partial-sum evaluation requires Re(s) > 1")

    divisor_counts = divisor_counts_up_to(terms)
    mangoldt = mangoldt_values_up_to(terms)
    normalization_load = normalization_load_coefficients_up_to(terms, divisor_counts)

    with mp.workdps(dps):
        s_mp = mp.mpc(s_complex)
        divisor_series = mp.mpc(0)
        normalization_load_series = mp.mpc(0)
        mangoldt_series = mp.mpc(0)

        for n in range(1, terms + 1):
            n_power = mp.power(n, -s_mp)
            divisor_series += divisor_counts[n] * n_power
            normalization_load_series += normalization_load[n] * n_power
            mangoldt_series += mangoldt[n] * n_power

        normalized_ratio = FIXED_POINT_V * normalization_load_series / divisor_series
        analytic_ratio = -mp.diff(mp.zeta, s_mp) / mp.zeta(s_mp)

        return PartialSumBridgeEvaluation(
            s=s_complex,
            terms=terms,
            divisor_series=complex(divisor_series),
            normalization_load_series=complex(normalization_load_series),
            normalized_ratio=complex(normalized_ratio),
            mangoldt_series=complex(mangoldt_series),
            analytic_ratio=complex(analytic_ratio),
            normalized_ratio_error=float(abs(normalized_ratio - analytic_ratio)),
            mangoldt_series_error=float(abs(mangoldt_series - analytic_ratio)),
        )


def evaluate_analytic_bridge(
    s: complex | float,
    dps: int = 50,
) -> AnalyticBridgeEvaluation:
    """Evaluate the continued DNI ratio and compare it to `-zeta'/zeta`."""
    if dps < 15:
        raise ValueError("dps must be at least 15")

    s_complex = complex(s)
    with mp.workdps(dps):
        s_mp = mp.mpc(s_complex)
        zeta_value = mp.zeta(s_mp)
        divisor_series = zeta_value ** 2
        divisor_derivative = mp.diff(lambda value: mp.zeta(value) ** 2, s_mp)
        normalization_load_series = -divisor_derivative / (math.e ** 2)
        normalized_ratio = FIXED_POINT_V * normalization_load_series / divisor_series
        zeta_log_derivative = -mp.diff(mp.zeta, s_mp) / zeta_value

        return AnalyticBridgeEvaluation(
            s=s_complex,
            divisor_series=complex(divisor_series),
            normalization_load_series=complex(normalization_load_series),
            normalized_ratio=complex(normalized_ratio),
            zeta_log_derivative=complex(zeta_log_derivative),
            abs_error=float(abs(normalized_ratio - zeta_log_derivative)),
        )
