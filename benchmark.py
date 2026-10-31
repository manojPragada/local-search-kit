"""Offline evaluation harness for local reranker executables."""
import argparse,hashlib,json,sys
from pathlib import Path
from reranker import rerank_results

def evaluate(cases,command,runner=None,include_cases=False):
    if not isinstance(cases,list) or not 1<=len(cases)<=100:raise ValueError('Benchmark must contain 1–100 cases')
    reciprocal=[];top1=0;ranks=[]
    for number,case in enumerate(cases,1):
        if not isinstance(case,dict) or not isinstance(case.get('query'),str) or not case['query'].strip():raise ValueError(f'Case {number} requires a query')
        candidates=case.get('candidates');relevant=case.get('relevant')
        if not isinstance(candidates,list) or not 1<=len(candidates)<=100 or not all(isinstance(value,str) and len(value)<=1000 for value in candidates):raise ValueError(f'Case {number} requires 1–100 bounded candidate strings')
        if type(relevant) is not int or not 0<=relevant<len(candidates):raise ValueError(f'Case {number} relevant index is invalid')
        results=[{'source':str(i),'line':1,'score':1,'excerpt':text} for i,text in enumerate(candidates)]
        kwargs={'runner':runner} if runner else {}
        ranked=rerank_results(case['query'],results,command,**kwargs);rank=next(i for i,item in enumerate(ranked,1) if int(item['source'])==relevant)
        reciprocal.append(1/rank);top1+=rank==1;ranks.append({'case':number,'rank':rank,'candidates':len(candidates)})
    encoded=json.dumps(cases,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    result={'cases':len(cases),'case_set_sha256':hashlib.sha256(encoded).hexdigest(),'mean_reciprocal_rank':sum(reciprocal)/len(reciprocal),'top_1_accuracy':top1/len(cases)}
    if include_cases:result['case_ranks']=ranks
    return result
def compare_metrics(baseline,candidate):
    for result in (baseline,candidate):
        if not isinstance(result,dict) or not all(type(result.get(key)) in (int,float) for key in ('mean_reciprocal_rank','top_1_accuracy')):raise ValueError('Both benchmark results require numeric MRR and top-1 accuracy')
    return {'mean_reciprocal_rank_delta':candidate['mean_reciprocal_rank']-baseline['mean_reciprocal_rank'],'top_1_accuracy_delta':candidate['top_1_accuracy']-baseline['top_1_accuracy']}
def compare_case_ranks(baseline,candidate):
    old,new=baseline.get('case_ranks'),candidate.get('case_ranks')
    if not isinstance(old,list) or not isinstance(new,list) or len(old)!=len(new) or not old:raise ValueError('Both benchmark results require aligned non-empty case ranks')
    deltas=[]
    for before,after in zip(old,new):
        if not all(isinstance(item,dict) for item in (before,after)) or before.get('case')!=after.get('case') or before.get('candidates')!=after.get('candidates') or type(before.get('rank')) is not int or type(after.get('rank')) is not int:raise ValueError('Case-rank diagnostics must align by case and candidate count')
        deltas.append(after['rank']-before['rank'])
    return {'improved_cases':sum(delta<0 for delta in deltas),'unchanged_cases':sum(delta==0 for delta in deltas),'regressed_cases':sum(delta>0 for delta in deltas),'worst_rank_regression':max(0,max(deltas))}
def promotion_gate(baseline,candidate,minimum_cases=20,minimum_mrr_delta=.02):
    """Conservatively decide whether an optional reranker merits documentation."""
    for result in (baseline,candidate):
        if type(result.get('cases')) is not int or result['cases']<1:raise ValueError('Both benchmark results require a positive case count')
        fingerprint=result.get('case_set_sha256')
        if not isinstance(fingerprint,str) or len(fingerprint)!=64 or any(ch not in '0123456789abcdef' for ch in fingerprint):raise ValueError('Both benchmark results require a valid case-set fingerprint')
    if baseline['cases']!=candidate['cases']:raise ValueError('Benchmark results must use the same cases')
    if baseline['case_set_sha256']!=candidate['case_set_sha256']:raise ValueError('Benchmark results must use the same fingerprinted case set')
    deltas=compare_metrics(baseline,candidate)
    reasons=[]
    if candidate['cases']<minimum_cases:reasons.append(f'requires at least {minimum_cases} labelled cases')
    if deltas['mean_reciprocal_rank_delta']<minimum_mrr_delta:reasons.append(f'MRR delta below {minimum_mrr_delta:g}')
    if deltas['top_1_accuracy_delta']<0:reasons.append('top-1 accuracy regressed')
    diagnostics={}
    if 'case_ranks' in baseline or 'case_ranks' in candidate:
        diagnostics=compare_case_ranks(baseline,candidate)
        if diagnostics['regressed_cases']:reasons.append(f"{diagnostics['regressed_cases']} individual case ranks regressed")
    return {'promote':not reasons,'reasons':reasons,**deltas,**diagnostics}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('cases');parser.add_argument('reranker');args=parser.parse_args()
    try:
        cases=json.loads(Path(args.cases).read_text(encoding='utf-8'));print(json.dumps(evaluate(cases,args.reranker,include_cases=True),indent=2));return 0
    except (OSError,ValueError,json.JSONDecodeError) as error:print(str(error),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
