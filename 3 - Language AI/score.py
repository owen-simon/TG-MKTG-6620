#!/usr/bin/env python3
"""Case 3 scorer: checks your rankings and scores them against Wayfair's relevance labels.

A rankings file is a CSV with the columns query_id, method, rank, product_id (extra columns are
ignored). Each method gives exactly ten products per query, ranks 1 to 10, no product twice.
The keyword baseline (data/keyword_rankings.csv) is always included; "keyword" is reserved for it.

    python score.py check  --rankings my_rankings.csv
    python score.py score  --split validation --rankings my_rankings.csv
    python score.py select --method bge_small --reason "your reason"
    python score.py score  --split test --selection selection.json --rankings my_rankings.csv
    python score.py show   --query-id 1 --rankings my_rankings.csv
    python score.py score  --split validation --rankings my_rankings.csv my_change.csv --baseline bge_small --out outputs_q4

What it reports for each method, averaged over the split's queries:
  ndcg10    Normalized discounted cumulative gain of the top 10. A result earns 1 if labelled Exact,
            0.5 if Partial, and 0 if Irrelevant or never labelled ("unjudged"). The result at rank r
            counts 1 / log2(r + 1), so rank 1 counts fully and rank 10 about 0.29. The total is divided
            by the best total possible from that query's labels, so 1.0 is a perfect top 10.
  exact1    Share of queries whose first result is labelled Exact, with a Wilson 95% interval.
  judged10  Share of the top-10 results that have any label. Unjudged results score 0 in ndcg10
            even when they would suit the shopper, so a low judged10 means ndcg10 may understate.
  diff      ndcg10 minus the baseline's on the same queries, with a paired 95% interval from 2,000
            resamples of the queries (seed 6620), and how many queries the method beat or lost to the
            baseline. The baseline is keyword unless --baseline names another method (validation and dev only).

Needs only NumPy.
"""
import argparse
import csv
import datetime
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data'
GAIN = {'Exact': 1.0, 'Partial': 0.5, 'Irrelevant': 0.0}
SPLITS = ('dev', 'validation', 'test')
TOP = 10


def fail(msg):
    sys.exit('Error: ' + msg)


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_csv(p):
    """Rows as dicts. Accepts a UTF-8 byte-order mark (Excel's "CSV UTF-8") and spaces around header names."""
    try:
        with open(p, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames: reader.fieldnames = [h.strip() for h in reader.fieldnames]
            return list(reader)
    except UnicodeDecodeError:
        fail('%s is not UTF-8 text; save it as a UTF-8 CSV' % p)


def load_data():
    manifest = json.loads((DATA / 'data_manifest.json').read_text())
    for name, digest in manifest['files'].items():
        if sha(DATA / name) != digest: fail('data/%s has changed since release. Restore it from the ZIP.' % name)
    queries = {q['query_id']: q for q in read_csv(DATA / 'queries.csv')}
    names = {p['product_id']: p['product_name'] + ' | ' + (p['product_class'] or '-') for p in read_csv(DATA / 'products.csv')}
    return queries, names


def load_labels(split):
    labels = {}
    for r in read_csv(DATA / ('labels_%s.csv' % split)):
        labels.setdefault(r['query_id'], {})[r['product_id']] = r['label']
    return labels


def load_rankings(files, names):
    """Return {method: {query_id: [product_id x 10]}}, refusing anything malformed."""
    out = {'keyword': {}}
    sources = [(DATA / 'keyword_rankings.csv', True)] + [(Path(f), False) for f in files]
    for path, baseline in sources:
        if not path.exists(): fail('no such file: %s' % path)
        rows = read_csv(path)
        if not rows: fail('%s has no rows' % path)
        missing = {'query_id', 'method', 'rank', 'product_id'} - set(rows[0])
        if missing: fail('%s lacks the column(s) %s; its header is: %s' % (path, ', '.join(sorted(missing)), ','.join(h for h in rows[0] if h is not None)))
        seen = {}
        for i, r in enumerate(rows, 2):
            if any(r[k] is None for k in ('query_id', 'method', 'rank', 'product_id')): fail('%s line %d has fewer fields than its header' % (path, i))
            m = r['method'].strip()
            if not re.fullmatch(r'[A-Za-z0-9_.-]+', m): fail('%s line %d: method names use letters, digits, _ . - only' % (path, i))
            if m == 'keyword' and not baseline: fail('%s line %d: "keyword" is reserved for the supplied baseline' % (path, i))
            try:
                rank, qid, pid = int(r['rank']), str(int(r['query_id'])), str(int(r['product_id']))
            except ValueError:
                fail('%s line %d: query_id, rank, and product_id must be whole numbers' % (path, i))
            if not 1 <= rank <= TOP: fail('%s line %d: rank must be 1 to %d' % (path, i, TOP))
            if pid not in names: fail('%s line %d: product_id %s is not in data/products.csv' % (path, i, pid))
            slot = seen.setdefault((m, qid), {})
            if rank in slot: fail('%s: method %s, query %s has rank %d twice' % (path, m, qid, rank))
            slot[rank] = pid
        for (m, qid), slot in seen.items():
            if m in out and qid in out[m] and not baseline: fail('method %s, query %s appears in more than one file' % (m, qid))
            if sorted(slot) != list(range(1, TOP + 1)): fail('method %s, query %s needs ranks 1 to %d exactly once' % (m, qid, TOP))
            ranked = [slot[k] for k in range(1, TOP + 1)]
            if len(set(ranked)) != TOP: fail('method %s, query %s lists a product twice' % (m, qid))
            out.setdefault(m, {})[qid] = ranked
    return out


def ndcg(ranked, judged):
    dcg = sum(GAIN.get(judged.get(p), 0.0) / math.log2(r + 2) for r, p in enumerate(ranked))
    best = sorted((GAIN[v] for v in judged.values()), reverse=True)[:TOP]
    ideal = sum(g / math.log2(r + 2) for r, g in enumerate(best))
    return dcg / ideal


def wilson(k, n, z=1.959963984540054):
    p = k / n
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, center - half), min(1.0, center + half)


def paired_interval(diff):
    v = np.asarray(diff, dtype=float)
    draws = np.random.default_rng(6620).integers(0, len(v), size=(2000, len(v)))
    lo, hi = np.quantile(v[draws].mean(axis=1), [0.025, 0.975])
    return float(lo), float(hi)


def score(split, rankings, queries, methods, out, baseline='keyword'):
    labels = load_labels(split)
    qids = sorted((q for q, v in queries.items() if v['split'] == split), key=int)
    per, rows = [], []
    for m in methods:
        absent = [q for q in qids if q not in rankings[m]]
        if absent: fail('method %s has no ranking for %d %s queries (first: %s)' % (m, len(absent), split, absent[0]))
    base = [ndcg(rankings[baseline][q], labels[q]) for q in qids]
    for m in methods:
        nd, ex, jd = [], [], []
        for q in qids:
            ranked, judged = rankings[m][q], labels[q]
            nd.append(ndcg(ranked, judged))
            ex.append(int(judged.get(ranked[0]) == 'Exact'))
            jd.append(sum(p in judged for p in ranked) / TOP)
            per.append([m, q, queries[q]['query'], '%.6f' % nd[-1], ex[-1], '%.1f' % jd[-1]])
        n, k = len(qids), sum(ex)
        lo, hi = wilson(k, n)
        diff = [a - b for a, b in zip(nd, base)]
        dlo, dhi = (0.0, 0.0) if m == baseline else paired_interval(diff)
        rows.append({'method': m, 'split': split, 'n': n, 'ndcg10': '%.4f' % np.mean(nd), 'exact1_hits': k,
                     'exact1': '%.4f' % (k / n), 'exact1_low': '%.4f' % lo, 'exact1_high': '%.4f' % hi,
                     'judged10': '%.4f' % np.mean(jd), 'baseline': baseline, 'ndcg10_diff': '%.4f' % np.mean(diff),
                     'diff_low': '%.4f' % dlo, 'diff_high': '%.4f' % dhi,
                     'beats_baseline': sum(d > 1e-12 for d in diff), 'loses_to_baseline': sum(d < -1e-12 for d in diff)})
    out.mkdir(parents=True, exist_ok=True)
    try:
        with open(out / ('%s_metrics.csv' % split), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
            w.writeheader()
            w.writerows(rows)
        with open(out / ('%s_per_query.csv' % split), 'w', newline='') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerow(['method', 'query_id', 'query', 'ndcg10', 'exact1', 'judged10'])
            w.writerows(per)
    except PermissionError as e:
        fail("can't write %s. If it is open in Excel or another program, close it and run again." % e.filename)
    print('%s, %d queries' % (split, len(qids)))
    print('%-16s %7s %16s %9s %26s' % ('method', 'ndcg10', 'exact1 (95%)', 'judged10', 'diff vs %s (95%%)' % baseline))
    for r in rows:
        d = '' if r['method'] == baseline else '%+.3f (%+.3f to %+.3f)' % (float(r['ndcg10_diff']), float(r['diff_low']), float(r['diff_high']))
        print('%-16s %7.3f %5.3f (%.2f-%.2f) %9.3f %26s' % (r['method'], float(r['ndcg10']), float(r['exact1']), float(r['exact1_low']),
                                                           float(r['exact1_high']), float(r['judged10']), d))
    print('Wrote %s and %s' % (out / ('%s_metrics.csv' % split), out / ('%s_per_query.csv' % split)))


def main():
    for stream in (sys.stdout, sys.stderr):  # a Windows pipe can't encode every product name; print ? instead of crashing
        if hasattr(stream, 'reconfigure'): stream.reconfigure(errors='replace')
    ap = argparse.ArgumentParser(description='Check and score Case 3 rankings.')
    sub = ap.add_subparsers(dest='command', required=True)
    c = sub.add_parser('check'); c.add_argument('--rankings', nargs='*', default=[])
    s = sub.add_parser('score'); s.add_argument('--split', choices=SPLITS, required=True); s.add_argument('--rankings', nargs='*', default=[])
    s.add_argument('--selection', type=Path); s.add_argument('--out', type=Path, default=Path('outputs'))
    s.add_argument('--baseline', default='keyword')
    e = sub.add_parser('select'); e.add_argument('--method', required=True); e.add_argument('--reason', required=True)
    e.add_argument('--out', type=Path, default=Path('selection.json'))
    w = sub.add_parser('show'); w.add_argument('--query-id', type=int, required=True); w.add_argument('--rankings', nargs='*', default=[])
    w.add_argument('--selection', type=Path, default=Path('selection.json'))
    a = ap.parse_args()
    if a.command == 'select':
        if a.out.exists(): fail('%s already exists; your first choice stays on record' % a.out)
        seen = Path('outputs/validation_metrics.csv')
        if a.method != 'keyword':
            if not seen.exists(): fail('%s not found; score the validation set first, then select' % seen)
            scored = sorted({r.get('method') for r in read_csv(seen)} - {None, ''} | {'keyword'})
            if a.method not in scored: fail('%s is not a method in %s; choose one of: %s' % (a.method, seen, ', '.join(scored)))
        record = {'method': a.method, 'reason': a.reason, 'saved_at_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
        record['validation_metrics_sha256'] = sha(seen) if seen.exists() else None
        a.out.write_text(json.dumps(record, indent=2) + '\n')
        print('Saved', a.out, json.dumps(record))
        return
    queries, names = load_data()
    if a.command == 'show':
        q = str(a.query_id)
        if q not in queries: fail('no query %s' % q)
        split = queries[q]['split']
        if split == 'test' and not a.selection.exists(): fail('test queries stay closed until selection.json exists')
        rankings = load_rankings(a.rankings, names)
        judged = load_labels(split).get(q, {})
        print('Query %s (%s): "%s"   labelled products: %d (%d Exact, %d Partial)' % (
            q, split, queries[q]['query'], len(judged), sum(v == 'Exact' for v in judged.values()), sum(v == 'Partial' for v in judged.values())))
        for m in sorted(rankings, key=lambda x: (x != 'keyword', x)):
            if q not in rankings[m]: continue
            print('\n%s   ndcg10 %.3f' % (m, ndcg(rankings[m][q], judged)))
            for r, p in enumerate(rankings[m][q], 1):
                print('%3d  %-10s %6s  %s' % (r, judged.get(p, 'unjudged'), p, names[p][:110]))
        return
    rankings = load_rankings(a.rankings, names)
    if a.command == 'check':
        for m in sorted(rankings):
            have = {s: sum(1 for q in rankings[m] if queries.get(q, {}).get('split') == s) for s in SPLITS}
            extra = [q for q in rankings[m] if q not in queries]
            if extra: fail('method %s ranks query %s, which is not in data/queries.csv' % (m, extra[0]))
            need = {s: sum(1 for v in queries.values() if v['split'] == s) for s in SPLITS}
            print('%-16s ' % m + '  '.join('%s %d/%d' % (s, have[s], need[s]) for s in SPLITS))
        print('Format OK.')
        return
    if a.split == 'test':
        if not a.selection or not a.selection.exists(): fail('scoring the test set needs --selection selection.json; save your choice first')
        try:
            chosen = json.loads(a.selection.read_text())['method']
        except (ValueError, KeyError, TypeError):
            chosen = None
        if not isinstance(chosen, str): fail('%s was not written by score.py select; save your choice with select' % a.selection)
        if chosen not in rankings: fail('your selection.json names %s, which is not in the rankings files given' % chosen)
        methods = ['keyword'] + ([chosen] if chosen != 'keyword' else [])
        if a.baseline != 'keyword': fail('the test set is compared with keyword only')
    else:
        if a.baseline not in rankings: fail('--baseline %s is not in the rankings files given' % a.baseline)
        methods = sorted(rankings, key=lambda x: (x != a.baseline, x != 'keyword', x))
    score(a.split, rankings, queries, methods, a.out, a.baseline)


if __name__ == '__main__':
    main()
