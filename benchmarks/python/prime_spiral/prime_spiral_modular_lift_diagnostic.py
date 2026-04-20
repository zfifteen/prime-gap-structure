#!/usr/bin/env python3
"""Run a deterministic prime-spiral modular-lift diagnostic and render plots."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/z-band-prime-prefilter-mpl")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from sympy import divisor_sigma, primerange


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "benchmarks"
    / "output"
    / "python"
    / "prime_spiral"
    / "prime_spiral_modular_lift_diagnostic"
)
DEFAULT_PRIME_LIMIT = 4_000
DEFAULT_SPIRAL_PRIME_COUNT = 300
DEFAULT_Q_SERIES_LIMIT = 120
DEFAULT_SIGMA = 2.0
DEFAULT_T_MIN = -12.0
DEFAULT_T_MAX = 12.0
DEFAULT_T_SAMPLES = 401
DEFAULT_TAU_REAL = 0.31
DEFAULT_TAU_IMAG = 0.91
DEFAULT_Z_REAL_SAMPLES = 121
DEFAULT_Z_IMAG_SAMPLES = 81
DEFAULT_Z_IMAG_HALF_SPAN = 0.25


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Run the prime-spiral -> Dirichlet-field -> modular-lift diagnostic "
            "and write JSON plus plot artifacts."
        ),
    )
    parser.add_argument(
        "--prime-limit",
        type=int,
        default=DEFAULT_PRIME_LIMIT,
        help="Largest prime included in the prime sums and spiral plot.",
    )
    parser.add_argument(
        "--spiral-prime-count",
        type=int,
        default=DEFAULT_SPIRAL_PRIME_COUNT,
        help="Number of primes shown in the spiral projection plot.",
    )
    parser.add_argument(
        "--q-series-limit",
        type=int,
        default=DEFAULT_Q_SERIES_LIMIT,
        help="Largest q exponent used for the modular witness series.",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=DEFAULT_SIGMA,
        help="Real part sigma used in the Dirichlet-field collapse scan.",
    )
    parser.add_argument(
        "--t-min",
        type=float,
        default=DEFAULT_T_MIN,
        help="Smallest imaginary ordinate t used in the collapse scan.",
    )
    parser.add_argument(
        "--t-max",
        type=float,
        default=DEFAULT_T_MAX,
        help="Largest imaginary ordinate t used in the collapse scan.",
    )
    parser.add_argument(
        "--t-samples",
        type=int,
        default=DEFAULT_T_SAMPLES,
        help="Number of t samples used in the collapse scan.",
    )
    parser.add_argument(
        "--tau-real",
        type=float,
        default=DEFAULT_TAU_REAL,
        help="Real part of the upper-half-plane test point tau.",
    )
    parser.add_argument(
        "--tau-imag",
        type=float,
        default=DEFAULT_TAU_IMAG,
        help="Imaginary part of the upper-half-plane test point tau.",
    )
    parser.add_argument(
        "--z-real-samples",
        type=int,
        default=DEFAULT_Z_REAL_SAMPLES,
        help="Number of real-axis samples in the elliptic residual grid.",
    )
    parser.add_argument(
        "--z-imag-samples",
        type=int,
        default=DEFAULT_Z_IMAG_SAMPLES,
        help="Number of imaginary-axis samples in the elliptic residual grid.",
    )
    parser.add_argument(
        "--z-imag-half-span",
        type=float,
        default=DEFAULT_Z_IMAG_HALF_SPAN,
        help="Imaginary half-span for the elliptic residual grid.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON and PNG artifacts.",
    )
    return parser


def _relative_residual(lhs: complex, rhs: complex) -> float:
    """Return the scale-normalized residual of two complex values."""
    scale = max(abs(lhs), abs(rhs), 1e-30)
    return float(abs(lhs - rhs) / scale)


def primes_up_to(prime_limit: int) -> list[int]:
    """Return the primes up to the inclusive bound."""
    return [int(value) for value in primerange(2, prime_limit + 1)]


def prime_spiral_coordinates(primes: list[int], point_count: int) -> dict[str, np.ndarray]:
    """Return the prime spiral coordinates for the first requested primes."""
    actual_count = min(point_count, len(primes))
    subset = np.asarray(primes[:actual_count], dtype=np.float64)
    logarithms = np.log(subset)
    radii = np.sqrt(subset)
    return {
        "primes": subset,
        "logarithms": logarithms,
        "x": radii * np.cos(logarithms),
        "y": radii * np.sin(logarithms),
    }


def dirichlet_resonance_values(
    primes: list[int],
    sigma: float,
    t_values: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return the partial Dirichlet resonance field and the shifted prime zeta sum."""
    prime_array = np.asarray(primes, dtype=np.float64)
    log_primes = np.log(prime_array)
    s_grid = sigma + 1j * t_values[:, None]

    # D(s) = sum p^{-s} exp(i log p)
    resonance = (
        np.exp(-s_grid * log_primes[None, :]) * np.exp(1j * log_primes[None, :])
    ).sum(axis=1)

    # P(s-i) = sum p^{-(s-i)}
    shifted_prime_zeta = np.exp(-(s_grid - 1j) * log_primes[None, :]).sum(axis=1)
    return resonance, shifted_prime_zeta


def prime_indicator_coefficients(q_series_limit: int) -> np.ndarray:
    """Return the q-series coefficients of the truncated prime indicator series."""
    coefficients = np.zeros(q_series_limit + 1, dtype=np.float64)
    for prime_value in primerange(2, q_series_limit + 1):
        coefficients[int(prime_value)] = 1.0
    return coefficients


def eisenstein_e4_coefficients(q_series_limit: int) -> np.ndarray:
    """Return the normalized E4 coefficients through the requested order."""
    coefficients = np.zeros(q_series_limit + 1, dtype=np.float64)
    coefficients[0] = 1.0
    for n in range(1, q_series_limit + 1):
        coefficients[n] = 240.0 * float(divisor_sigma(n, 3))
    return coefficients


def eisenstein_e6_coefficients(q_series_limit: int) -> np.ndarray:
    """Return the normalized E6 coefficients through the requested order."""
    coefficients = np.zeros(q_series_limit + 1, dtype=np.float64)
    coefficients[0] = 1.0
    for n in range(1, q_series_limit + 1):
        coefficients[n] = -504.0 * float(divisor_sigma(n, 5))
    return coefficients


def multiply_q_series(
    left: np.ndarray,
    right: np.ndarray,
    q_series_limit: int,
) -> np.ndarray:
    """Multiply two q-series and truncate at the requested order."""
    return np.convolve(left, right)[: q_series_limit + 1]


def qd_derivative(coefficients: np.ndarray) -> np.ndarray:
    """Apply the q d/dq operator to one q-series."""
    weights = np.arange(coefficients.size, dtype=np.float64)
    return coefficients * weights


def rankin_cohen_bracket_order_1(
    left: np.ndarray,
    right: np.ndarray,
    left_weight: float,
    right_weight: float,
    q_series_limit: int,
) -> np.ndarray:
    """Return the first Rankin-Cohen bracket [left, right]_1."""
    return (
        left_weight * multiply_q_series(left, qd_derivative(right), q_series_limit)
        - right_weight * multiply_q_series(qd_derivative(left), right, q_series_limit)
    )


def evaluate_q_series(coefficients: np.ndarray, tau: complex) -> complex:
    """Evaluate one q-series at q = exp(2 pi i tau)."""
    q_value = np.exp(2j * math.pi * tau)
    powers = q_value ** np.arange(coefficients.size, dtype=np.int64)
    return complex(np.dot(coefficients, powers))


def elliptic_tau_shift_grid(
    tau: complex,
    z_real_samples: int,
    z_imag_samples: int,
    z_imag_half_span: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the z grid and the normalized elliptic residual heatmap."""
    z_real = np.linspace(-0.5, 0.5, z_real_samples)
    z_imag = np.linspace(-z_imag_half_span, z_imag_half_span, z_imag_samples)
    z_real_grid, z_imag_grid = np.meshgrid(z_real, z_imag)
    z_grid = z_real_grid + 1j * z_imag_grid
    residual_grid = np.abs(1.0 - np.exp(-2j * math.pi * (tau + 2.0 * z_grid)))
    return z_real, z_imag, residual_grid


def plot_prime_spiral(
    spiral: dict[str, np.ndarray],
    output_path: Path,
) -> None:
    """Render the prime spiral projection plot."""
    fig, ax = plt.subplots(figsize=(8.6, 8.0))
    scatter = ax.scatter(
        spiral["x"],
        spiral["y"],
        c=np.arange(spiral["primes"].size),
        cmap="viridis",
        s=18,
        linewidths=0.0,
    )
    ax.plot(spiral["x"], spiral["y"], color="#8ecae6", linewidth=0.7, alpha=0.4)
    ax.set_title("Prime Spiral Projection")
    ax.set_xlabel(r"$\sqrt{p}\cos(\log p)$")
    ax.set_ylabel(r"$\sqrt{p}\sin(\log p)$")
    ax.grid(alpha=0.15)
    ax.set_aspect("equal", adjustable="box")
    fig.colorbar(scatter, ax=ax, label="Prime index")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_dirichlet_collapse(
    t_values: np.ndarray,
    resonance: np.ndarray,
    shifted_prime_zeta: np.ndarray,
    output_path: Path,
) -> None:
    """Render the Dirichlet-field collapse plot."""
    absolute_difference = np.abs(resonance - shifted_prime_zeta)
    fig, axes = plt.subplots(2, 1, figsize=(10.4, 7.6), sharex=True)

    axes[0].plot(
        t_values,
        np.abs(resonance),
        color="#28536b",
        linewidth=2.0,
        label=r"$|D(\sigma + it)|$",
    )
    axes[0].plot(
        t_values,
        np.abs(shifted_prime_zeta),
        color="#b23a48",
        linewidth=1.4,
        linestyle="--",
        label=r"$|P(\sigma + it - i)|$",
    )
    axes[0].set_title("Dirichlet Resonance Collapse")
    axes[0].set_ylabel("Magnitude")
    axes[0].grid(alpha=0.2)
    axes[0].legend(loc="upper right")

    axes[1].plot(
        t_values,
        np.log10(np.maximum(absolute_difference, 1e-30)),
        color="#2f7d32",
        linewidth=2.0,
    )
    axes[1].set_xlabel("Imaginary ordinate t")
    axes[1].set_ylabel(r"$\log_{10}|D - P(\cdot - i)|$")
    axes[1].grid(alpha=0.2)

    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_jacobi_failure(
    residual_grid: np.ndarray,
    tau_shift_residual: float,
    unit_shift_residual: float,
    modular_t_residual: float,
    modular_s_residual: float,
    z_real: np.ndarray,
    z_imag: np.ndarray,
    output_path: Path,
) -> None:
    """Render the Jacobi-law failure plot for the tau-only witness."""
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.0), width_ratios=[1.05, 1.0])

    status_labels = [
        "T",
        "S",
        "z+1",
        "z+tau",
    ]
    status_values = [
        modular_t_residual,
        modular_s_residual,
        unit_shift_residual,
        tau_shift_residual,
    ]
    colors = ["#2f7d32", "#2f7d32", "#2f7d32", "#b23a48"]
    bars = axes[0].bar(status_labels, status_values, color=colors, width=0.7)
    axes[0].set_yscale("log")
    axes[0].set_title("Transformation Residuals")
    axes[0].set_ylabel("Relative residual")
    axes[0].grid(axis="y", alpha=0.2)
    for bar, value in zip(bars, status_values, strict=True):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2.0,
            value,
            f"{value:.2e}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    axes[0].text(
        0.03,
        0.97,
        "T: tau -> tau + 1\nS: tau -> -1/tau\nz+1: elliptic unit shift\nz+tau: elliptic tau shift",
        transform=axes[0].transAxes,
        va="top",
        ha="left",
        fontsize=8,
        bbox={"facecolor": "white", "edgecolor": "#d8dee9", "boxstyle": "round,pad=0.3"},
    )

    heatmap = axes[1].imshow(
        np.log10(np.maximum(residual_grid, 1e-30)),
        extent=[float(z_real[0]), float(z_real[-1]), float(z_imag[0]), float(z_imag[-1])],
        origin="lower",
        aspect="auto",
        cmap="magma",
    )
    axes[1].set_title(r"Index-1 Elliptic Residual for $z \mapsto z + \tau$")
    axes[1].set_xlabel(r"$\Re(z)$")
    axes[1].set_ylabel(r"$\Im(z)$")
    fig.colorbar(heatmap, ax=axes[1], label=r"$\log_{10}$ residual")

    fig.subplots_adjust(left=0.07, right=0.96, bottom=0.13, top=0.88, wspace=0.28)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def run_diagnostic(
    prime_limit: int,
    spiral_prime_count: int,
    q_series_limit: int,
    sigma: float,
    t_min: float,
    t_max: float,
    t_samples: int,
    tau_real: float,
    tau_imag: float,
    z_real_samples: int,
    z_imag_samples: int,
    z_imag_half_span: float,
) -> tuple[dict[str, object], dict[str, object]]:
    """Run the full diagnostic and return summary data plus plot inputs."""
    if prime_limit < 11:
        raise ValueError("prime_limit must be at least 11")
    if spiral_prime_count < 1:
        raise ValueError("spiral_prime_count must be positive")
    if q_series_limit < 12:
        raise ValueError("q_series_limit must be at least 12")
    if tau_imag <= 0.0:
        raise ValueError("tau_imag must be positive")
    if t_samples < 2:
        raise ValueError("t_samples must be at least 2")
    if z_real_samples < 2 or z_imag_samples < 2:
        raise ValueError("z grid samples must each be at least 2")

    primes = primes_up_to(prime_limit)
    if not primes:
        raise ValueError("prime_limit produced no primes")

    spiral = prime_spiral_coordinates(primes, spiral_prime_count)
    t_values = np.linspace(t_min, t_max, t_samples)
    resonance, shifted_prime_zeta = dirichlet_resonance_values(primes, sigma, t_values)
    absolute_difference = np.abs(resonance - shifted_prime_zeta)
    baseline = np.maximum(np.abs(shifted_prime_zeta), 1e-30)
    relative_difference = absolute_difference / baseline

    prime_indicator = prime_indicator_coefficients(q_series_limit)
    e4 = eisenstein_e4_coefficients(q_series_limit)
    e6 = eisenstein_e6_coefficients(q_series_limit)
    modular_witness = rankin_cohen_bracket_order_1(e4, e6, 4.0, 6.0, q_series_limit)

    tau = complex(tau_real, tau_imag)
    witness_at_tau = evaluate_q_series(modular_witness, tau)
    if abs(witness_at_tau) <= 1e-24:
        raise ValueError("modular witness vanished at the chosen tau")

    witness_t = evaluate_q_series(modular_witness, tau + 1.0)
    witness_s = evaluate_q_series(modular_witness, -1.0 / tau)
    modular_t_residual = _relative_residual(witness_t, witness_at_tau)
    modular_s_residual = _relative_residual(witness_s, (tau**12) * witness_at_tau)
    unit_shift_residual = 0.0

    z_real, z_imag, residual_grid = elliptic_tau_shift_grid(
        tau=tau,
        z_real_samples=z_real_samples,
        z_imag_samples=z_imag_samples,
        z_imag_half_span=z_imag_half_span,
    )
    tau_shift_residual = float(np.mean(residual_grid))

    summary = {
        "prime_limit": int(prime_limit),
        "prime_count": int(len(primes)),
        "spiral_prime_count": int(spiral["primes"].size),
        "q_series_limit": int(q_series_limit),
        "dirichlet_collapse": {
            "sigma": float(sigma),
            "t_min": float(t_min),
            "t_max": float(t_max),
            "t_samples": int(t_samples),
            "max_absolute_difference": float(np.max(absolute_difference)),
            "mean_absolute_difference": float(np.mean(absolute_difference)),
            "max_relative_difference": float(np.max(relative_difference)),
            "status": "collapsed_to_shifted_prime_zeta",
        },
        "named_path_closure": {
            "prime_indicator_tau_only": True,
            "tau_only_operations": [
                "linear_combination_with_tau_only_series",
                "petersson_inner_product_returns_scalar",
                "rankin_cohen_bracket_preserves_tau_only_dependence",
            ],
            "modular_witness": "[E4, E6]_1",
            "modular_witness_weight": 12,
            "modular_witness_abs_at_tau": float(abs(witness_at_tau)),
            "conclusion": "named_path_stays_tau_only_without_explicit_z_insertion",
        },
        "jacobi_check": {
            "tau_real": float(tau_real),
            "tau_imag": float(tau_imag),
            "modular_t_residual": modular_t_residual,
            "modular_s_residual": modular_s_residual,
            "elliptic_unit_shift_residual": unit_shift_residual,
            "elliptic_tau_shift_residual_min": float(np.min(residual_grid)),
            "elliptic_tau_shift_residual_mean": tau_shift_residual,
            "elliptic_tau_shift_residual_max": float(np.max(residual_grid)),
            "passes_weight_12_modular_checks": bool(
                modular_t_residual < 1e-10 and modular_s_residual < 1e-10
            ),
            "fails_index_1_elliptic_check": bool(tau_shift_residual > 1e-3),
        },
        "fourier_match": {
            "status": "blocked",
            "reason": (
                "no positive-index Jacobi form was constructed on the named path, "
                "so Leech-linked Fourier matching is undefined at the claimed stage"
            ),
        },
    }

    plot_inputs = {
        "spiral": spiral,
        "t_values": t_values,
        "resonance": resonance,
        "shifted_prime_zeta": shifted_prime_zeta,
        "residual_grid": residual_grid,
        "z_real": z_real,
        "z_imag": z_imag,
        "tau_shift_residual": tau_shift_residual,
        "unit_shift_residual": unit_shift_residual,
        "modular_t_residual": modular_t_residual,
        "modular_s_residual": modular_s_residual,
    }
    return summary, plot_inputs


def write_artifacts(
    output_dir: Path,
    summary: dict[str, object],
    plot_inputs: dict[str, object],
) -> dict[str, Path]:
    """Write the JSON summary and all plot artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = output_dir / "prime_spiral_modular_lift_diagnostic_summary.json"
    spiral_path = output_dir / "prime_spiral_projection.png"
    collapse_path = output_dir / "dirichlet_resonance_collapse.png"
    jacobi_path = output_dir / "jacobi_tau_only_failure.png"

    plot_prime_spiral(plot_inputs["spiral"], spiral_path)
    plot_dirichlet_collapse(
        plot_inputs["t_values"],
        plot_inputs["resonance"],
        plot_inputs["shifted_prime_zeta"],
        collapse_path,
    )
    plot_jacobi_failure(
        residual_grid=plot_inputs["residual_grid"],
        tau_shift_residual=plot_inputs["tau_shift_residual"],
        unit_shift_residual=plot_inputs["unit_shift_residual"],
        modular_t_residual=plot_inputs["modular_t_residual"],
        modular_s_residual=plot_inputs["modular_s_residual"],
        z_real=plot_inputs["z_real"],
        z_imag=plot_inputs["z_imag"],
        output_path=jacobi_path,
    )

    artifact_paths = {
        "summary_json": summary_path,
        "prime_spiral_projection": spiral_path,
        "dirichlet_resonance_collapse": collapse_path,
        "jacobi_tau_only_failure": jacobi_path,
    }
    payload = dict(summary)
    payload["artifacts"] = {key: str(path) for key, path in artifact_paths.items()}
    summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return artifact_paths


def main(argv: list[str] | None = None) -> int:
    """Run the diagnostic entry point."""
    args = build_parser().parse_args(argv)
    summary, plot_inputs = run_diagnostic(
        prime_limit=args.prime_limit,
        spiral_prime_count=args.spiral_prime_count,
        q_series_limit=args.q_series_limit,
        sigma=args.sigma,
        t_min=args.t_min,
        t_max=args.t_max,
        t_samples=args.t_samples,
        tau_real=args.tau_real,
        tau_imag=args.tau_imag,
        z_real_samples=args.z_real_samples,
        z_imag_samples=args.z_imag_samples,
        z_imag_half_span=args.z_imag_half_span,
    )
    write_artifacts(args.output_dir, summary, plot_inputs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
