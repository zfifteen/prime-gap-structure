"""Minimal emit-all PGS iprime generator."""

from __future__ import annotations

from math import isqrt


DEFAULT_CANDIDATE_BOUND = 128
DEFAULT_CHAIN_LIMIT = 8
DEFAULT_VISIBLE_DIVISOR_BOUND = 10_000
PGS_SOURCE = "PGS"
CHAIN_FALLBACK_SOURCE = "chain_fallback"
FALLBACK_SOURCE = "fallback"
FALLBACK_REQUIRED_SOURCE = "fallback_required"
WHEEL_OPEN_RESIDUES_MOD30 = frozenset({1, 7, 11, 13, 17, 19, 23, 29})


def has_trial_divisor(n: int) -> bool:
    """Return True when trial division finds a concrete divisor."""
    if n < 2:
        return True
    for divisor in range(2, isqrt(n) + 1):
        if n % divisor == 0:
            return True
    return False


def divisor_witness(n: int, max_divisor: int | None = None) -> int | None:
    """Return a concrete divisor, when one is visible."""
    if n < 2:
        return 1
    limit = isqrt(n) if max_divisor is None else min(isqrt(n), int(max_divisor))
    for divisor in range(2, limit + 1):
        if n % divisor == 0:
            return divisor
    return None


def first_prime_in_chamber(p: int, chamber_width: int) -> int | None:
    """Return the first trial-division prime in the current chamber."""
    for candidate in range(int(p) + 1, int(p) + int(chamber_width) + 1):
        if not has_trial_divisor(candidate):
            return candidate
    return None


def next_prime_by_trial_division(
    p: int,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> int:
    """Return the next prime using deterministic chamber expansion."""
    chamber_width = int(candidate_bound)
    if chamber_width < 1:
        raise ValueError("candidate_bound must be positive")
    while True:
        q = first_prime_in_chamber(int(p), chamber_width)
        if q is not None:
            return q
        chamber_width *= 2


def closure_reason(
    p: int,
    offset: int,
    max_divisor: int | None = None,
) -> str | None:
    """Return a PGS-visible reason that p + offset is not a boundary."""
    n = int(p) + int(offset)
    residue = n % 30
    if residue not in WHEEL_OPEN_RESIDUES_MOD30:
        return f"wheel_closed_residue:{residue}"
    witness = divisor_witness(n, max_divisor)
    if witness is not None and witness not in {1, n}:
        return f"divisor_witness:{witness}"
    return None


def admissible_offsets(p: int, candidate_bound: int) -> list[int]:
    """Return wheel-open boundary offsets inside the chamber."""
    return [
        offset
        for offset in range(1, int(candidate_bound) + 1)
        if (int(p) + offset) % 30 in WHEEL_OPEN_RESIDUES_MOD30
    ]


def pgs_chamber_closure_certificate(
    p: int,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
    fallback_q: int | None = None,
    max_divisor: int | None = None,
) -> dict[str, object] | None:
    """Return the first v2 chamber-closure certificate."""
    offsets = admissible_offsets(int(p), int(candidate_bound))
    for gap_offset in offsets:
        q = int(p) + gap_offset
        if closure_reason(int(p), gap_offset, max_divisor) is not None:
            continue
        certificate = pgs_gap_certificate(
            int(p),
            gap_offset,
            int(candidate_bound),
            max_divisor,
        )
        if certificate is None:
            continue
        fallback_agreed = fallback_q is not None and q == int(fallback_q)
        certificate["fallback_agreed"] = fallback_agreed
        if fallback_q is None or fallback_agreed:
            return certificate
    return None


def visible_open_chain_offsets(
    p: int,
    seed_offset: int,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
    chain_limit: int = DEFAULT_CHAIN_LIMIT,
    max_divisor: int | None = None,
) -> list[int]:
    """Return visible-open rightward chain offsets after one seed."""
    offsets = admissible_offsets(int(p), int(candidate_bound))
    chain: list[int] = []
    current = int(seed_offset)
    while len(chain) < int(chain_limit):
        visible = [
            offset
            for offset in offsets
            if offset > current and closure_reason(int(p), offset, max_divisor) is None
        ]
        if not visible:
            break
        current = min(visible)
        chain.append(current)
    return chain


def chain_fallback_result(
    p: int,
    seed_offset: int,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
    chain_limit: int = DEFAULT_CHAIN_LIMIT,
    max_divisor: int | None = DEFAULT_VISIBLE_DIVISOR_BOUND,
) -> tuple[int | None, dict[str, object]]:
    """Return the first exact chain survivor and chain sidecar fields."""
    chain_offsets = visible_open_chain_offsets(
        int(p),
        int(seed_offset),
        int(candidate_bound),
        int(chain_limit),
        max_divisor,
    )
    chain_nodes = [int(p) + offset for offset in chain_offsets]
    checked_nodes: list[int] = []
    selected_position: int | None = None
    selected_q: int | None = None
    for position, candidate in enumerate(chain_nodes, start=1):
        checked_nodes.append(candidate)
        if not has_trial_divisor(candidate):
            selected_position = position
            selected_q = candidate
            break
    return selected_q, {
        "chain_seed": int(p) + int(seed_offset),
        "chain_limit": int(chain_limit),
        "chain_position_selected": selected_position,
        "chain_nodes_checked": checked_nodes,
        "chain_fallback_success": selected_q is not None,
        "full_fallback_used": False,
    }


def pgs_gap_certificate(
    p: int,
    gap_offset: int,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
    max_divisor: int | None = None,
) -> dict[str, object] | None:
    """Return a chamber-closure certificate for one proposed offset."""
    closed_offsets: list[int] = []
    reasons: dict[str, str] = {}
    unclosed_offsets: list[int] = []
    for offset in admissible_offsets(int(p), int(candidate_bound)):
        if offset >= int(gap_offset):
            break
        reason = closure_reason(int(p), offset, max_divisor)
        if reason is None:
            unclosed_offsets.append(offset)
            continue
        closed_offsets.append(offset)
        reasons[str(offset)] = reason
    if unclosed_offsets:
        return None

    return {
        "rule_id": "pgs_chamber_closure_v2",
        "p": int(p),
        "q": int(p) + int(gap_offset),
        "gap_offset": int(gap_offset),
        "candidate_bound": int(candidate_bound),
        "closed_offsets_before_q": closed_offsets,
        "closure_reason_by_offset": reasons,
        "unclosed_offsets_before_q": unclosed_offsets,
        "carrier_w": int(p),
        "carrier_d": 2,
        "used_forbidden_tool": False,
        "fallback_agreed": False,
    }


def pgs_boundary_certificate(
    p: int,
    fallback_q: int,
    boundary_offset: int | None = None,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> dict[str, object] | None:
    """Return the first fallback-guarded PGS v2 certificate."""
    if boundary_offset is not None:
        certificate = pgs_gap_certificate(int(p), int(boundary_offset), candidate_bound)
        if certificate is not None and int(certificate["q"]) == int(fallback_q):
            certificate["fallback_agreed"] = True
            return certificate
        return None
    return pgs_chamber_closure_certificate(
        int(p),
        candidate_bound,
        int(fallback_q),
    )


def pgs_probe_certificate(
    p: int,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
    max_divisor: int | None = None,
) -> dict[str, object] | None:
    """Return a PGS v2 certificate without running fallback."""
    return pgs_chamber_closure_certificate(
        int(p),
        candidate_bound,
        None,
        max_divisor,
    )


def resolve_q(
    p: int,
    boundary_offset: int | None = None,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> tuple[int, str, dict[str, object] | None]:
    """Resolve q and return its source."""
    certificate = (
        pgs_gap_certificate(
            int(p),
            int(boundary_offset),
            candidate_bound,
            DEFAULT_VISIBLE_DIVISOR_BOUND,
        )
        if boundary_offset is not None
        else pgs_chamber_closure_certificate(
            int(p),
            candidate_bound,
            None,
            DEFAULT_VISIBLE_DIVISOR_BOUND,
        )
    )
    if certificate is not None:
        q0 = int(certificate["q"])
        if not has_trial_divisor(q0):
            certificate["fallback_agreed"] = True
            certificate.update(
                {
                    "chain_seed": None,
                    "chain_limit": DEFAULT_CHAIN_LIMIT,
                    "chain_position_selected": None,
                    "chain_nodes_checked": [],
                    "chain_fallback_success": False,
                    "full_fallback_used": False,
                }
            )
            return q0, PGS_SOURCE, certificate

        chain_q, chain_fields = chain_fallback_result(
            int(p),
            int(certificate["gap_offset"]),
            candidate_bound,
            DEFAULT_CHAIN_LIMIT,
            DEFAULT_VISIBLE_DIVISOR_BOUND,
        )
        chain_certificate = dict(certificate)
        chain_certificate["fallback_agreed"] = False
        chain_certificate.update(chain_fields)
        if chain_q is not None:
            return chain_q, CHAIN_FALLBACK_SOURCE, chain_certificate

        fallback_q = next_prime_by_trial_division(int(p), candidate_bound)
        chain_certificate["full_fallback_used"] = True
        return fallback_q, FALLBACK_SOURCE, chain_certificate

    fallback_q = next_prime_by_trial_division(int(p), candidate_bound)
    return fallback_q, FALLBACK_SOURCE, {
        "chain_seed": None,
        "chain_limit": DEFAULT_CHAIN_LIMIT,
        "chain_position_selected": None,
        "chain_nodes_checked": [],
        "chain_fallback_success": False,
        "full_fallback_used": True,
    }


def emit_record(
    p: int,
    boundary_offset: int | None = None,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> dict[str, int]:
    """Emit one minimal accurate iprime record."""
    q, _source, _certificate = resolve_q(int(p), boundary_offset, candidate_bound)
    return {
        "p": int(p),
        "q": q,
    }


def emit_records(
    anchors: list[int],
    boundary_offsets: dict[int, int] | None = None,
    candidate_bound: int = DEFAULT_CANDIDATE_BOUND,
) -> list[dict[str, int]]:
    """Emit one minimal record per anchor."""
    offsets = {} if boundary_offsets is None else boundary_offsets
    return [
        emit_record(anchor, offsets.get(anchor), candidate_bound)
        for anchor in anchors
    ]
