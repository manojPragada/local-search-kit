"""Bounded local reranker protocol; it may reorder but never create citations."""
import json
import math
import subprocess

def rerank_results(query,results,command,runner=subprocess.run):
    if not isinstance(command,str) or not command:raise ValueError('Reranker must be a local executable path')
    payload={'version':1,'query':query,'candidates':[{'excerpt':r['excerpt'],'lexical_score':r['score']} for r in results]}
    try:completed=runner([command],input=json.dumps(payload),text=True,capture_output=True,timeout=10,check=False)
    except (OSError,subprocess.SubprocessError) as error:raise ValueError(f'Local reranker failed: {error}') from None
    if completed.returncode!=0:raise ValueError('Local reranker returned a non-zero exit status')
    try:scores=json.loads(completed.stdout)
    except json.JSONDecodeError:raise ValueError('Local reranker output must be a JSON score array') from None
    if not isinstance(scores,list) or len(scores)!=len(results) or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in scores):
        raise ValueError('Local reranker must return one finite 0–1 score per candidate')
    enriched=[dict(result,rerank_score=score) for result,score in zip(results,scores)]
    return [item for _,item in sorted(enumerate(enriched),key=lambda pair:(-pair[1]['rerank_score'],pair[0]))]
