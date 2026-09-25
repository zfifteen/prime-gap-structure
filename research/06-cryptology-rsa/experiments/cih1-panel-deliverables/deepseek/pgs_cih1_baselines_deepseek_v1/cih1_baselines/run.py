"""CLI driver for baselines package."""
import argparse
import sys
import os
import json
from . import official_replay
from . import io_jsonl
from . import fermat
from . import floor_density
from . import contamination
from . import decoy_reciprocal
from . import report

def cmd_official_replay(args):
    out_dir = args.out_dir or 'OUT'
    os.makedirs(out_dir, exist_ok=True)
    results = official_replay.replay_official()
    path = os.path.join(out_dir, 'official_fixture_replay.json')
    io_jsonl.save_json(path, results)
    print(f"Official replay written to {path}")

def cmd_corpus_baselines(args):
    public_path = args.public
    audit_path = args.audit
    out_dir = args.out_dir or 'OUT'
    seed = args.seed
    floor_window = args.floor_window
    floor_stride = args.floor_stride
    decoy_samples = args.decoy_samples

    os.makedirs(out_dir, exist_ok=True)

    # Load
    pub_rows = io_jsonl.load_jsonl(public_path)
    aud_rows = io_jsonl.load_jsonl(audit_path)

    # Join on case_id, integrity check
    pub_dict = {r['case_id']: r for r in pub_rows}
    aud_dict = {r['case_id']: r for r in aud_rows}
    if set(pub_dict.keys()) != set(aud_dict.keys()):
        missing_pub = set(aud_dict.keys()) - set(pub_dict.keys())
        missing_aud = set(pub_dict.keys()) - set(aud_dict.keys())
        msg = "Mismatched case_ids: "
        if missing_pub:
            msg += f"in audit but not public: {missing_pub} "
        if missing_aud:
            msg += f"in public but not audit: {missing_aud}"
        raise ValueError(msg)

    case_ids = sorted(pub_dict.keys())
    contamination_rows = []
    fermat_rows = []
    floor_rows = []
    decoy_rows = []

    for cid in case_ids:
        pub = pub_dict[cid]
        aud = aud_dict[cid]
        N = pub['N']
        p = aud['p']
        q = aud['q']

        # Contamination
        cont = contamination.compute_contamination(pub, aud)
        contamination_rows.append(cont)

        # Fermat baseline
        steps, f1, f2 = fermat.fermat_steps(N)
        fermat_rows.append({
            'case_id': cid,
            'fermat_steps': steps,
            'fermat_factors': (f1, f2),
            'near_square_flag': cont['near_square_flag'],
        })

        # Floor density
        tested, passed, prate = floor_density.floor_density(N, floor_window, floor_stride)
        floor_rows.append({
            'case_id': cid,
            'tested': tested,
            'passed': passed,
            'pass_rate': prate,
        })

        # Decoy reciprocal
        decoys, count_est = decoy_reciprocal.find_decoys(N, p, q, floor_window, decoy_samples)
        decoy_rows.append({
            'case_id': cid,
            'decoy_samples': decoys,
            'decoy_count_available': count_est,
            'decoy_count': len(decoys),
        })

    # Write out files
    io_jsonl.save_json(os.path.join(out_dir, 'contamination_report.json'), contamination_rows)
    io_jsonl.write_jsonl(os.path.join(out_dir, 'fermat_baseline.jsonl'), fermat_rows)
    io_jsonl.write_jsonl(os.path.join(out_dir, 'floor_density.jsonl'), floor_rows)
    io_jsonl.write_jsonl(os.path.join(out_dir, 'decoy_reciprocal_examples.jsonl'), decoy_rows)

    # Official replay ok
    try:
        official_results = official_replay.replay_official()
        # verify expected classification
        exp_class = {40: 'near_square_fermat_class', 50: 'non_near_square', 64: 'near_square_fermat_class'}
        ok = True
        for r in official_results:
            if r['classification'] != exp_class[r['bits']]:
                ok = False
        official_ok = ok
    except Exception:
        official_ok = False

    results_bundle = {
        'contamination_rows': contamination_rows,
        'fermat_rows': fermat_rows,
        'floor_rows': floor_rows,
        'decoy_rows': decoy_rows,
        'official_replay_ok': official_ok,
        'floor_window': floor_window,
        'floor_stride': floor_stride,
        'n_cases': len(case_ids),
    }
    summary = report.build_baseline_summary(results_bundle)
    io_jsonl.save_json(os.path.join(out_dir, 'baseline_summary.json'), summary)
    report.write_markdown_summary(summary, os.path.join(out_dir, 'baseline_summary.md'))

    # run meta
    meta = {
        'public_file': os.path.abspath(public_path),
        'audit_file': os.path.abspath(audit_path),
        'seed': seed,
        'floor_window': floor_window,
        'floor_stride': floor_stride,
        'decoy_samples': decoy_samples,
    }
    io_jsonl.save_json(os.path.join(out_dir, 'run_meta.json'), meta)
    print(f"Corpus baselines written to {out_dir}")

def main():
    parser = argparse.ArgumentParser(prog='cih1_baselines', description='CIH-1 negative controls and baselines')
    sub = parser.add_subparsers(dest='command')

    p_off = sub.add_parser('official-replay')
    p_off.add_argument('--out-dir', default='OUT')

    p_corpus = sub.add_parser('corpus-baselines')
    p_corpus.add_argument('--public', required=True)
    p_corpus.add_argument('--audit', required=True)
    p_corpus.add_argument('--out-dir', default='OUT')
    p_corpus.add_argument('--seed', type=int, default=0)
    p_corpus.add_argument('--floor-window', type=int, default=50000)
    p_corpus.add_argument('--floor-stride', type=int, default=1)
    p_corpus.add_argument('--decoy-samples', type=int, default=20)

    p_all = sub.add_parser('all')
    p_all.add_argument('--public', required=True)
    p_all.add_argument('--audit', required=True)
    p_all.add_argument('--out-dir', default='OUT')
    p_all.add_argument('--seed', type=int, default=0)
    p_all.add_argument('--floor-window', type=int, default=50000)
    p_all.add_argument('--floor-stride', type=int, default=1)
    p_all.add_argument('--decoy-samples', type=int, default=20)

    args = parser.parse_args()
    if args.command == 'official-replay':
        cmd_official_replay(args)
    elif args.command == 'corpus-baselines':
        cmd_corpus_baselines(args)
    elif args.command == 'all':
        cmd_official_replay(args)
        cmd_corpus_baselines(args)
    else:
        parser.print_help()
