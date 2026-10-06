#!/usr/bin/env python3
"""Two-tool teaching harness: manual model decisions or an explicitly scripted replay.

No model endpoint is invoked. An interactive user can relay each observation to
their usual agent and paste its next JSON action. --plan replays a prepared list.
Both paths enforce the same scope and four-tool-call budget.
"""
import argparse
import json
from pathlib import Path
import search_lab as lab

def run(data,root,qid,actions,mode,method=None):
    docs,qs=lab.dataset(data)
    question=next(q for q in qs if q['query_id']==qid)
    by_id={d['doc_id']:d for d in docs}
    allowed=set(); read=set(); trace=[]; calls=0
    state=lab.load_json(root/'store.json')
    chosen=method or state['model']
    if chosen!='keyword' and chosen!=state['model']: raise ValueError('Rebuild database for the selected model')
    for step in range(5):
        action=next(actions,None)
        if action is None: break
        observation={}
        try:
            if not isinstance(action,dict) or set(action)!={'tool','arguments'} or not isinstance(action['arguments'],dict):
                raise ValueError('Action needs only tool and arguments')
            tool=action['tool']; args=action['arguments']
            if tool=='finish':
                if set(args)!={'status','answer','citations'} or args['status'] not in ['answer','abstain']:
                    raise ValueError('Invalid terminal fields')
                if not isinstance(args['answer'],str) or not isinstance(args['citations'],list): raise ValueError('Invalid terminal types')
                if args['status']=='answer' and (not args['answer'].strip() or not args['citations']): raise ValueError('Answer needs text and a citation')
                if args['status']=='abstain' and args['citations']: raise ValueError('Abstention has no supporting citations')
                for cite in args['citations']:
                    if not isinstance(cite,dict) or set(cite)!={'doc_id','quote'}: raise ValueError('Citation needs doc_id and quote')
                    if cite['doc_id'] not in read or not isinstance(cite['quote'],str) or not cite['quote'].strip() or cite['quote'] not in by_id[cite['doc_id']]['text']:
                        raise ValueError('Citation must quote an eligible passage already read')
                trace.append(dict(step=step+1,action=action,observation={'terminal_schema':'accepted; human support audit still required'}))
                return dict(mode=mode,query_id=qid,method=chosen,tool_calls=calls,status=args['status'],answer=args['answer'],citations=args['citations'],trace=trace)
            if calls>=4:
                trace.append(dict(step=step+1,action=action,observation={'error':'tool budget exhausted'}))
                break
            calls+=1
            if tool=='search':
                if set(args)!={'query_id'} or args['query_id']!=qid: raise ValueError('Search must use the fixed request ID')
                if chosen=='keyword':
                    hits=[by_id[r['doc_id']] for r in lab.ranking(data,'keyword')[qid][:3]]
                else: hits=lab.search(data,root,qid)
                allowed.update(r['doc_id'] for r in hits)
                observation={'hits':[{k:r[k] for k in ['doc_id','title','brand','status']} for r in hits]}
            elif tool=='read_policy':
                if set(args)!={'doc_id'} or args['doc_id'] not in allowed: raise ValueError('Read requires an ID returned by search')
                doc=by_id[args['doc_id']]
                if not lab.eligible(doc,question): raise ValueError('Policy outside request scope')
                read.add(doc['doc_id']); observation={'document':doc}
            else: raise ValueError('Unknown tool')
        except (ValueError,TypeError,KeyError) as e:
            observation={'error':str(e)}
        trace.append(dict(step=step+1,action=action,observation=observation))
        if mode=='interactive relay': print(json.dumps(observation),flush=True)
    return dict(mode=mode,query_id=qid,method=chosen,tool_calls=calls,status='abstain',answer='No valid supported answer completed within the action budget.',citations=[],trace=trace)

def interactive():
    while True:
        try: line=input('Next JSON action: ')
        except EOFError: return
        try: yield json.loads(line)
        except json.JSONDecodeError: yield {'invalid_json':line}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,default=Path(__file__).resolve().parent/'data')
    ap.add_argument('--db-root',type=Path,required=True)
    ap.add_argument('--query-id',required=True)
    ap.add_argument('--selection',type=Path)
    ap.add_argument('--plan',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    method=lab.load_json(a.selection)['method'] if a.selection else None
    mode='scripted replay; no model inference' if a.plan else 'interactive relay'
    actions=iter(lab.load_json(a.plan)) if a.plan else interactive()
    result=run(a.data,a.db_root,a.query_id,actions,mode,method)
    lab.save_json(a.out,result)
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
