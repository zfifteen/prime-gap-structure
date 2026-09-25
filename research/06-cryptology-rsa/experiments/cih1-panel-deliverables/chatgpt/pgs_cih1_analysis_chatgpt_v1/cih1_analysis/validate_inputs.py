"""Strict validation and public/audit/carrier joining."""
from __future__ import annotations
from typing import Any

def _int(v: Any, name: str) -> int:
    try:
        return int(v)
    except (TypeError, ValueError) as e:
        raise ValueError(f"{name} must be an integer-compatible value") from e

def validate_public(rows):
    out = {}
    for r in rows:
        for k in ("case_id", "bits", "N"):
            if k not in r:
                raise ValueError(f"public row missing {k}")
        cid = str(r["case_id"])
        if cid in out:
            raise ValueError(f"duplicate public case_id: {cid}")
        n = _int(r["N"], "N")
        if n <= 0:
            raise ValueError(f"{cid}: N must be positive")
        out[cid] = {"case_id": cid, "bits": _int(r["bits"], "bits"), "N": n}
    return out

def validate_audit(rows):
    out = {}
    for r in rows:
        for k in ("case_id", "N", "p", "q"):
            if k not in r:
                raise ValueError(f"audit row missing {k}")
        cid = str(r["case_id"])
        if cid in out:
            raise ValueError(f"duplicate audit case_id: {cid}")
        n, p, q = (_int(r[k], k) for k in ("N", "p", "q"))
        if p <= 1 or q <= 1 or p * q != n:
            raise ValueError(f"{cid}: audit factors do not multiply to N")
        out[cid] = {"case_id": cid, "N": n, "p": p, "q": q,
                    **{k: _int(r[k], k) for k in ("isqrt_N", "min_dist_to_sqrt") if k in r}}
        if "rel_dist" in r:
            out[cid]["rel_dist"] = float(r["rel_dist"])
    return out

def validate_carrier(rows):
    out = {}
    for r in rows:
        for k in ("case_id", "carrier_w", "search_band_lo", "search_band_hi"):
            if k not in r:
                raise ValueError(f"carrier row missing {k}")
        cid = str(r["case_id"])
        if cid in out:
            raise ValueError(f"duplicate carrier case_id: {cid}")
        lo, hi = _int(r["search_band_lo"], "search_band_lo"), _int(r["search_band_hi"], "search_band_hi")
        if lo > hi:
            raise ValueError(f"{cid}: invalid search band lo > hi")
        out[cid] = {"case_id": cid, "carrier_w": _int(r["carrier_w"], "carrier_w"),
                    "search_band_lo": lo, "search_band_hi": hi}
        if "band_note" in r:
            out[cid]["band_note"] = str(r["band_note"])
    return out

def join_inputs(public, audit, carrier):
    missing = set(public) - set(audit)
    if missing:
        raise ValueError("public/audit missing case_id(s): " + ", ".join(sorted(missing)))
    missing = set(public) - set(carrier)
    if missing:
        raise ValueError("missing carrier row(s): " + ", ".join(sorted(missing)))
    extra = (set(audit) | set(carrier)) - set(public)
    if extra:
        raise ValueError("audit/carrier contain case_id(s) absent from public: " + ", ".join(sorted(extra)))
    joined = []
    for cid, p in public.items():
        a, c = audit[cid], carrier[cid]
        if p["N"] != a["N"]:
            raise ValueError(f"{cid}: public N != audit N")
        joined.append({**p, **a, **c})
    return joined
