"""CLI runner for CIH-1."""
from __future__ import annotations
import argparse, hashlib, json, random, statistics, sys
from pathlib import Path
from .io_jsonl import read_jsonl, write_jsonl
from .validate_inputs import validate_public, validate_audit, validate_carrier, join_inputs
from .exclude import exclusion_info
from .controls import sample_uniform_distances, summarize_control
from .metrics import score_case
from .stats_tests import directional_p_value
from . import __version__

REQUIRED_FREEZE = (
    ("primary_metric",),
    ("control","samples_per_case"),
    ("exclusion","min_abs_dist_to_sqrt"),
    ("exclusion","min_rel_dist_to_sqrt"),
    ("statistics","alpha"),
    ("statistics","minimum_cases"),
    ("statistics","decision_rule"),
)

def deep_get(d, path):
    cur = d
    for k in path:
        if k not in cur: return None
        cur = cur[k]
    return cur

def load_freeze(path):
    if path is None:
        path = Path(__file__).resolve().parent.parent / "freeze_fallback_cih1.json"
        source = "fallback"
    else:
        path = Path(path)
        source = str(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [".".join(p) for p in REQUIRED_FREEZE if deep_get(data,p) is None]
    if missing:
        raise ValueError("freeze missing required field(s): " + ", ".join(missing))
    return data, source

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def main(argv=None):
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    run=sub.add_parser("run")
    run.add_argument("--public",required=True)
    run.add_argument("--audit",required=True)
    run.add_argument("--carrier",required=True)
    run.add_argument("--freeze")
    run.add_argument("--out-dir",required=True)
    run.add_argument("--seed",type=int,default=20260808)
    args=ap.parse_args(argv)
    if args.cmd != "run": return 2

    freeze, freeze_source = load_freeze(args.freeze)
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    public=validate_public(list(read_jsonl(args.public)))
    audit=validate_audit(list(read_jsonl(args.audit)))
    carrier=validate_carrier(list(read_jsonl(args.carrier)))
    rows=join_inputs(public,audit,carrier)

    k=int(freeze["control"]["samples_per_case"])
    abs_thr=int(freeze["exclusion"]["min_abs_dist_to_sqrt"])
    rel_thr=float(freeze["exclusion"]["min_rel_dist_to_sqrt"])
    rng=random.Random(args.seed)
    scores=[]; excluded=[]
    for row in rows:
        ex=exclusion_info(row,abs_thr,rel_thr)
        rec={k:v for k,v in row.items() if k not in ("band_note",)}
        rec.update(ex)
        rec.update({"D_c":None,"control_median_D_u":None,"control_mean_D_u":None,
                    "R":None,"carrier_beats_control_median":False,
                    "control_samples":0,"seed":args.seed})
        if ex["excluded"]:
            excluded.append({"case_id":row["case_id"],"reason":ex["exclude_reason"]})
            scores.append(rec); continue
        lo,hi=row["search_band_lo"],row["search_band_hi"]
        controls=sample_uniform_distances(lo,hi,row["p"],row["q"],k,rng)
        rec.update(score_case(row,controls))
        rec["control_samples"]=k
        scores.append(rec)

    included=[r for r in scores if not r["excluded"]]
    if not included:
        median_R=None; mean_R=None; fbeat=0.0; pval=1.0; decision="aborted_insufficient_n"
        abort=True; abort_reason="insufficient_included_cases"
    else:
        median_R=statistics.median(r["R"] for r in included)
        mean_R=statistics.fmean(r["R"] for r in included)
        fbeat=sum(r["carrier_beats_control_median"] for r in included)/len(included)
        deltas=[r["control_median_D_u"]-r["D_c"] for r in included]
        pval, p_two, pos, neg=directional_p_value(deltas)
        min_cases=int(freeze["statistics"]["minimum_cases"])
        abort=len(included)<min_cases
        abort_reason="insufficient_included_cases" if abort else None
        rule=freeze["statistics"]["decision_rule"]
        # The fallback rule is explicit; custom freezes may select the same
        # named policy with thresholds in decision_rule.
        if abort:
            decision="aborted_insufficient_n"
        elif median_R <= float(rule["carrier_median_R_max"]) and \
             fbeat >= float(rule["carrier_fbeat_min"]) and \
             pval < float(freeze["statistics"]["alpha"]):
            decision="carrier_better"
        elif median_R >= float(rule["control_median_R_min"]) and \
             p_two < float(rule["two_sided_alpha"]):
            decision="control_better"
        else:
            decision="no_difference"

    if decision=="carrier_better":
        sentence="Measured on hold-out corpus: carrier distance is better than the frozen uniform-band control; this is hypothesis support, not a factorization or validation claim."
    elif decision=="control_better":
        sentence="Measured on hold-out corpus: the uniform-band control outperformed the carrier under the frozen metric; this does not establish a negative general theorem."
    elif decision=="aborted_insufficient_n":
        sentence="Measured on hold-out corpus: experiment aborted for insufficient included cases."
    else:
        sentence="Measured on hold-out corpus: the frozen test did not establish a carrier/control difference."
    summary={
        "experiment_id":"CIH-1",
        "freeze_source":freeze_source,
        "n_total":len(scores),"n_included":len(included),"n_excluded":len(excluded),
        "median_R":median_R,"mean_R":mean_R,"f_beat":fbeat,"p_value":pval,
        "decision":decision,"allowed_claim_sentence":sentence,
        "aborted":abort,"abort_reason":abort_reason,"seed":args.seed,
        "package_version":__version__,
    }
    write_jsonl(out/"case_scores.jsonl",scores)
    write_jsonl(out/"exclusions.jsonl",excluded)
    (out/"experiment_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    meta={"timestamp_utc":__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
          "package_version":__version__,"seed":args.seed,"argv":sys.argv,
          "input_sha256":{k:sha256_file(v) for k,v in {"public":args.public,"audit":args.audit,"carrier":args.carrier,**({"freeze":args.freeze} if args.freeze else {})}.items()}}
    (out/"run_meta.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
