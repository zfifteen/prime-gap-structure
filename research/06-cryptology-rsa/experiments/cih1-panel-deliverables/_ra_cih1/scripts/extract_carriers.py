#!/usr/bin/env python3
"""Extract CIH-1 lower-chamber GWR carriers from public moduli only.

Definition (Gemini freeze PROTOCOL §4–5):
  - center = isqrt(N)
  - lower chamber = immediate public chamber preceding center
  - lower_anchor = previous public endpoint before center
  - carrier_w = GWR leftmost min-divisor maximizer on that chamber (PGS cert)
  - search_band = closed [anchor, reset_endpoint]

No factors, gcd, primality, or product-closure gates.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import gmpy2

ROOT = Path(__file__).resolve().parents[6]  # prime-gap-structure
V2 = ROOT / "research/06-cryptology-rsa/experiments/live-solver/rsa-v2"
SRC = ROOT / "src/python"
for p in (str(SRC), str(V2)):
    if p not in sys.path:
        sys.path.insert(0, p)

import run_experiment as v2  # noqa: E402


def extract_one(
    case_id: str,
    n: int,
    *,
    cert_cache: dict,
    prev_cache: dict,
    seg_cache: dict,
    diag: dict,
) -> dict:
    N = gmpy2.mpz(n)
    center = gmpy2.isqrt(N)
    anchor = v2.previous_endpoint_at(center, prev_cache, seg_cache, diag)
    if anchor is None:
        return {
            "case_id": case_id,
            "status": "unresolved_missing_lower_endpoint",
            "carrier_w": None,
            "search_band_lo": None,
            "search_band_hi": None,
            "center": int(center),
        }
    cert = v2.certificate_at(anchor, cert_cache, diag)
    if cert is None or cert.carrier_w is None:
        return {
            "case_id": case_id,
            "status": "unresolved_missing_lower_certificate",
            "carrier_w": None,
            "search_band_lo": int(anchor),
            "search_band_hi": None,
            "center": int(center),
        }
    lo = int(cert.anchor)
    hi = int(cert.reset_endpoint)
    w = int(cert.carrier_w)
    if not (lo <= w <= hi):
        status = "unresolved_carrier_outside_chamber"
    elif hi < lo:
        status = "unresolved_empty_band"
    else:
        status = "ok"
    return {
        "case_id": case_id,
        "status": status,
        "carrier_w": w,
        "search_band_lo": lo,
        "search_band_hi": hi,
        "center": int(center),
        "gap_offset": int(cert.gap_offset),
        "carrier_d": int(cert.carrier_d) if cert.carrier_d is not None else None,
        "lock_carrier_offset": (
            int(cert.lock_carrier_offset) if cert.lock_carrier_offset is not None else None
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="CIH-1 public carrier extraction")
    ap.add_argument("--public", type=Path, required=True)
    ap.add_argument("--out-carrier", type=Path, required=True)
    ap.add_argument("--out-detail", type=Path, required=True)
    args = ap.parse_args()

    rows = [
        json.loads(line)
        for line in args.public.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    cert_cache: dict = {}
    prev_cache: dict = {}
    seg_cache: dict = {}
    diag = v2.make_diagnostics()

    t0 = time.time()
    details = []
    carriers = []
    for row in rows:
        case_id = str(row["case_id"])
        n = int(row["N"])
        det = extract_one(
            case_id, n, cert_cache=cert_cache, prev_cache=prev_cache, seg_cache=seg_cache, diag=diag
        )
        details.append(det)
        if det["status"] == "ok":
            carriers.append(
                {
                    "case_id": case_id,
                    "carrier_w": det["carrier_w"],
                    "search_band_lo": det["search_band_lo"],
                    "search_band_hi": det["search_band_hi"],
                }
            )

    args.out_carrier.parent.mkdir(parents=True, exist_ok=True)
    with args.out_carrier.open("w", encoding="utf-8", newline="\n") as f:
        for r in carriers:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with args.out_detail.open("w", encoding="utf-8", newline="\n") as f:
        for r in details:
            f.write(json.dumps(r, sort_keys=True) + "\n")

    n_ok = sum(1 for d in details if d["status"] == "ok")
    summary = {
        "n_public": len(rows),
        "n_carrier_ok": n_ok,
        "n_unresolved": len(rows) - n_ok,
        "elapsed_s": round(time.time() - t0, 3),
        "diagnostics": diag,
        "definition": "immediate lower chamber before isqrt(N); band=[anchor,reset_endpoint]",
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
