#!/usr/bin/env python3
"""Supported student scaffold. Saved vectors; no downloads, model calls or keys.

Python 3.11+. inspect/compare/select need numpy; databases also need lancedb.
The live databases belong on a local disk. Plain reports may live on NFS.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import re
import shutil
import sqlite3
import subprocess
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
SPACE_FIELDS=['model_id','revision','dimensions','dtype','normalization','query_prefix','document_input']
CORE=['keyword','bge_small','qwen3','qwen3_256']

def read_csv(p):
    with Path(p).open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))

def write_csv(p,rows):
    with Path(p).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader(); w.writerows(rows)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_json(p): return json.loads(Path(p).read_text())
def save_json(p,obj): Path(p).write_text(json.dumps(obj,indent=2)+'\n')
def text_of(d): return d['title']+'\n'+d['text']
def tokens(s): return set(re.findall(r'[a-z0-9]+',s.lower()))

def dataset(data):
    manifest=load_json(data/'data_manifest.json')
    for name,digest in manifest['files'].items():
        if sha(data/name)!=digest: raise ValueError('Changed input: '+name)
    return read_csv(data/'documents.csv'),read_csv(data/'queries.csv')

def vectors(data,model):
    docs,qs=dataset(data)
    meta=load_json(data/(model+'.json'))
    if meta['document_csv_sha256']!=sha(data/'documents.csv') or meta['query_csv_sha256']!=sha(data/'queries.csv'):
        raise ValueError('Vectors belong to different text files')
    if sha(data/(model+'.npz'))!=meta['vector_sha256']: raise ValueError('Vector file changed')
    with np.load(data/(model+'.npz'),allow_pickle=False) as a:
        d,q=a['documents'],a['queries']
    if meta['document_ids']!=[x['doc_id'] for x in docs] or meta['query_ids']!=[x['query_id'] for x in qs]:
        raise ValueError('Vector row order does not match IDs')
    for arr,n in [(d,len(docs)),(q,len(qs))]:
        if arr.shape!=(n,meta['dimensions']) or arr.dtype!=np.float32: raise ValueError('Wrong vector shape or dtype')
        if not np.isfinite(arr).all() or not np.allclose(np.linalg.norm(arr,axis=1),1,atol=2e-5): raise ValueError('Invalid or unnormalized vector')
    return d,q,meta

def require_same_space(expected,actual):
    different=[k for k in SPACE_FIELDS if expected[k]!=actual[k]]
    if different: raise ValueError('Incompatible embedding settings: '+', '.join(different))

def eligible(d,q): return d['brand']==q['brand'] and d['status']=='current'

def ranking(data,method,filtered=True):
    docs,qs=dataset(data)
    if method=='keyword':
        # Deliberately simple word-overlap baseline. This is not BM25 or SQLite FTS.
        scores=np.array([[len(tokens(q['question']) & tokens(text_of(d))) for d in docs] for q in qs],dtype=float)
    else:
        d,q,_=vectors(data,method)
        scores=q@d.T
    out={}
    for i,q in enumerate(qs):
        candidates=[j for j,d in enumerate(docs) if not filtered or eligible(d,q)]
        order=sorted(candidates,key=lambda j:(-float(scores[i,j]),docs[j]['doc_id']))
        out[q['query_id']]=[{'doc_id':docs[j]['doc_id'],'score':float(scores[i,j])} for j in order]
    return out

def interval(v):
    # Paired query bootstrap for differences vs keyword; individual rates use Wilson (rate_interval).
    v=np.asarray(v,dtype=float)
    draws=np.random.default_rng(6620).integers(0,len(v),size=(2000,len(v)))
    return [float(x) for x in np.quantile(v[draws].mean(axis=1),[.025,.975])]

def rate_interval(v):
    # Wilson interval avoids claiming zero uncertainty when a small set is all correct.
    n=len(v); p=sum(v)/n; z=1.959963984540054
    center=(p+z*z/(2*n))/(1+z*z/n)
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [max(0,center-half),min(1,center+half)]

def compare(data,split,out,selection=None):
    docs,qs=dataset(data)
    methods=CORE.copy()
    if split=='final':
        if selection is None: raise ValueError('Save a selection before final evaluation')
        sel=load_json(selection)
        if sel['documents_sha256']!=sha(data/'documents.csv') or sel['queries_sha256']!=sha(data/'queries.csv'):
            raise ValueError('Selection belongs to different inputs')
        methods=list(dict.fromkeys(['keyword',sel['method']]))
    labels={r['query_id']:r for r in read_csv(data/f'labels_{split}.csv')}
    selected=[q for q in qs if q['split']==split]
    if not selected: raise ValueError('No queries for requested split')
    out.mkdir(parents=True,exist_ok=True)
    rows=[]; per_query=[]; hits={}
    for method in methods:
        ranks=ranking(data,method)
        one=[]; three=[]
        for q in selected:
            gold=labels[q['query_id']]['relevant_id']
            ids=[r['doc_id'] for r in ranks[q['query_id']][:3]]
            one.append(int(gold==ids[0])); three.append(int(gold in ids))
            per_query.append(dict(method=method,query_id=q['query_id'],relevant_id=gold,top1=ids[0],top3='|'.join(ids),hit1=one[-1],hit3=three[-1]))
        hits[method]=np.array(three)
        ci=rate_interval(three); delta=hits[method]-hits['keyword']; dci=interval(delta)
        dims=0 if method=='keyword' else vectors(data,method)[2]['dimensions']
        rows.append(dict(method=method,split=split,n=len(selected),hit1=sum(one),hit3=sum(three),recall1=np.mean(one),recall3=np.mean(three),ci_low=ci[0],ci_high=ci[1],delta_vs_keyword=np.mean(delta),delta_low=dci[0],delta_high=dci[1],dimensions=dims,raw_document_vector_bytes=len(docs)*dims*4))
    write_csv(out/f'{split}_metrics.csv',rows)
    write_csv(out/f'{split}_retrieval.csv',per_query)
    print(json.dumps(rows,indent=2))
    return rows

def local_path(path):
    """Reject recognized network mounts on Linux; other OS paths need user inspection."""
    path=Path(path).resolve()
    ancestor=path
    while not ancestor.exists(): ancestor=ancestor.parent
    if shutil.which('findmnt'):
        r=subprocess.run(['findmnt','-n','-o','FSTYPE','-T',str(ancestor)],text=True,capture_output=True)
        fs=r.stdout.strip().lower()
        if r.returncode or not fs: raise ValueError('Cannot establish filesystem type; inspect mount before proceeding')
        if fs.startswith(('nfs','cifs','smb','fuse','lustre','gpfs')): raise ValueError('Use a local disk for this lab database, not '+fs)
    else: fs='not detected; verify local disk in your operating system'
    return path,fs

def build(data,model,root):
    import lancedb
    import pyarrow as pa
    root,fs=local_path(root)
    if root.exists(): raise ValueError('Choose a NEW database directory; existing work is preserved')
    docs,qs=dataset(data); d,q,meta=vectors(data,model)
    root.mkdir(parents=True)
    schema=pa.schema([pa.field(k,pa.string()) for k in docs[0]]+[pa.field('vector',pa.list_(pa.float32(),meta['dimensions']))])
    records=[dict(row,vector=d[i].tolist()) for i,row in enumerate(docs)]
    db=lancedb.connect(str(root/'lance'))
    db.create_table('policies',data=pa.Table.from_pylist(records,schema=schema))
    with sqlite3.connect(root/'catalog.sqlite') as conn:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('CREATE TABLE documents (doc_id TEXT PRIMARY KEY,brand TEXT,status TEXT,title TEXT,text TEXT,version TEXT)')
        conn.executemany('INSERT INTO documents VALUES (?,?,?,?,?,?)',[tuple(r[k] for k in docs[0]) for r in docs])
        conn.execute('CREATE TABLE embedding_settings (name TEXT PRIMARY KEY,value TEXT)')
        conn.executemany('INSERT INTO embedding_settings VALUES (?,?)',[(k,str(meta[k])) for k in SPACE_FIELDS])
    conn.close()
    save_json(root/'store.json',dict(model=model,embedding=meta,filesystem=fs))
    print('Created',len(docs),'rows;',model,meta['dimensions'],'dimensions;',root)

def search(data,root,qid,filtered=True):
    import lancedb
    root,_=local_path(root)
    state=load_json(root/'store.json')
    docs,qs=dataset(data); d,q,meta=vectors(data,state['model'])
    require_same_space(state['embedding'],meta)
    if state['embedding']['document_csv_sha256']!=sha(data/'documents.csv'): raise ValueError('Rebuild after document edits')
    qi=next(i for i,row in enumerate(qs) if row['query_id']==qid)
    table=lancedb.connect(str(root/'lance')).open_table('policies')
    query=table.search(q[qi]).distance_type('cosine')
    if filtered:
        # Brand values originate in the frozen course input; quote for SQL syntax.
        brand=qs[qi]['brand'].replace("'","''")
        query=query.where("brand = '"+brand+"' AND status = 'current'",prefilter=True)
    return [{k:v for k,v in r.items() if k!='vector'} for r in query.limit(3).to_list()]

def store_check(data,root,out):
    root,_=local_path(root)
    state=load_json(root/'store.json'); docs,qs=dataset(data)
    baseline=ranking(data,state['model'])
    checks=[]
    for query in qs:
        found=search(data,root,query['query_id'])
        expected=baseline[query['query_id']][:3]
        same=[r['doc_id'] for r in found]==[r['doc_id'] for r in expected]
        close=np.allclose([r['_distance'] for r in found],[1-r['score'] for r in expected],atol=2e-5)
        checks.append(dict(query_id=query['query_id'],same_ids=bool(same),same_distances=bool(close)))
    with sqlite3.connect(root/'catalog.sqlite') as conn:
        integrity=conn.execute('PRAGMA integrity_check').fetchone()[0]
        n=conn.execute('SELECT COUNT(*) FROM documents').fetchone()[0]
    conn.close()
    report=dict(queries=len(checks),all_matches=all(x['same_ids'] and x['same_distances'] for x in checks),sqlite_integrity=integrity,sqlite_rows=n,expected_rows=len(docs),details=checks)
    save_json(out,report)
    if not report['all_matches'] or integrity!='ok' or n!=len(docs): raise ValueError('Store check failed; inspect report')
    print('Reopened databases:',len(checks),'queries match exact NumPy search; SQLite integrity',integrity)

def backup(root,out):
    root,_=local_path(root); out,_=local_path(out)
    if out.exists(): raise ValueError('Backup destination exists; choose a new filename')
    src=sqlite3.connect(root/'catalog.sqlite'); dest=sqlite3.connect(out)
    try: src.backup(dest)
    finally: dest.close(); src.close()
    check=sqlite3.connect(out)
    try:
        integrity=check.execute('PRAGMA integrity_check').fetchone()[0]
        n=check.execute('SELECT COUNT(*) FROM documents').fetchone()[0]
    finally: check.close()
    report=dict(backup=out.name,sha256=sha(out),integrity=integrity,rows=n,
                scope='SQLite catalog only. Rebuild LanceDB from documents plus the saved vectors.')
    save_json(out.with_suffix('.receipt.json'),report)
    if integrity!='ok': raise ValueError('Backup integrity failure')
    print(json.dumps(report,indent=2))

def sql_literal(s): return "'"+str(s).replace("'","''")+"'"

def pg_export(data,model,out,qid):
    docs,qs=dataset(data); d,q,meta=vectors(data,model)
    qi=next(i for i,r in enumerate(qs) if r['query_id']==qid)
    # Fresh named schema, no DROP/overwrite; run only in your course sandbox DB.
    schema='practice_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
    statements=['\\set ON_ERROR_STOP on','BEGIN;','CREATE EXTENSION IF NOT EXISTS vector;',
      'CREATE SCHEMA '+schema+';','SET search_path TO '+schema+', public;',
      f'CREATE TABLE policies (doc_id text PRIMARY KEY,brand text,status text,title text,embedding vector({meta["dimensions"]}));',
      f'CREATE TABLE queries (query_id text PRIMARY KEY,embedding vector({meta["dimensions"]}));',
      'CREATE TABLE embedding_settings (model_id text,revision text,dimensions integer);',
      'INSERT INTO embedding_settings VALUES ('+','.join([sql_literal(meta['model_id']),sql_literal(meta['revision']),str(meta['dimensions'])])+');']
    for row,vec in zip(docs,d):
        vals=[row[k] for k in ['doc_id','brand','status','title']]+[json.dumps(vec.tolist())]
        statements.append('INSERT INTO policies VALUES ('+','.join(sql_literal(v) for v in vals)+');')
    statements.extend(['INSERT INTO queries VALUES ('+sql_literal(qid)+','+sql_literal(json.dumps(q[qi].tolist()))+');',
      'COMMIT;', '\\d policies',
      'SELECT doc_id, title, embedding <=> (SELECT embedding FROM queries WHERE query_id = '+sql_literal(qid)+') AS cosine_distance FROM policies WHERE brand = '+sql_literal(qs[qi]['brand'])+" AND status = 'current' ORDER BY cosine_distance, doc_id LIMIT 3;"])
    out.write_text('\n'.join(statements)+'\n')
    print('Wrote',out,'for',qid,'in new schema',schema)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,default=HERE/'data')
    sub=ap.add_subparsers(dest='command',required=True)
    sub.add_parser('inspect')
    c=sub.add_parser('compare'); c.add_argument('--split',choices=['dev','validation','final'],default='validation'); c.add_argument('--out',type=Path,required=True); c.add_argument('--selection',type=Path)
    c=sub.add_parser('select'); c.add_argument('--method',choices=CORE,required=True); c.add_argument('--reason',required=True); c.add_argument('--out',type=Path,required=True)
    c=sub.add_parser('build'); c.add_argument('--model',choices=CORE[1:]+['minilm','bge_m3'],default='bge_small'); c.add_argument('--db-root',type=Path,required=True)
    c=sub.add_parser('search'); c.add_argument('--db-root',type=Path,required=True); c.add_argument('--query-id',required=True); c.add_argument('--unfiltered',action='store_true')
    c=sub.add_parser('store-check'); c.add_argument('--db-root',type=Path,required=True); c.add_argument('--out',type=Path,required=True)
    c=sub.add_parser('backup'); c.add_argument('--db-root',type=Path,required=True); c.add_argument('--out',type=Path,required=True)
    c=sub.add_parser('pg-export'); c.add_argument('--model',choices=CORE[1:],default='bge_small'); c.add_argument('--query-id',required=True); c.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.command=='inspect':
        docs,qs=dataset(a.data)
        print(len(docs),'documents;',len(qs),'queries; sqlite',sqlite3.sqlite_version)
        for p in sorted(a.data.glob('*.npz')):
            d,q,m=vectors(a.data,p.stem)
            print(p.stem, d.shape,q.shape,d.dtype,'document bytes',d.nbytes,'first five coordinates',d[0,:5].tolist())
    elif a.command=='compare': compare(a.data,a.split,a.out,a.selection)
    elif a.command=='select':
        if a.out.exists(): raise ValueError('Selection already exists; preserve it and document any amendment separately')
        save_json(a.out,dict(method=a.method,reason=a.reason,created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),documents_sha256=sha(a.data/'documents.csv'),queries_sha256=sha(a.data/'queries.csv'),filter='brand + current',k=3))
        print('Selection saved. Now run final comparison.')
    elif a.command=='build': build(a.data,a.model,a.db_root)
    elif a.command=='search': print(json.dumps(search(a.data,a.db_root,a.query_id,not a.unfiltered),indent=2))
    elif a.command=='store-check': store_check(a.data,a.db_root,a.out)
    elif a.command=='backup': backup(a.db_root,a.out)
    elif a.command=='pg-export': pg_export(a.data,a.model,a.out,a.query_id)

if __name__=='__main__': main()
