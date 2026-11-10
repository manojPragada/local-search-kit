"""Offline evaluation harness for local reranker executables."""
import argparse,hashlib,json,math,statistics,sys
from pathlib import Path
from reranker import rerank_results

def evaluate(cases,command,runner=None,include_cases=False):
    if not isinstance(cases,list) or not 1<=len(cases)<=100:raise ValueError('Benchmark must contain 1–100 cases')
    reciprocal=[];top1=0;top3=0;top5=0;ranks=[]
    for number,case in enumerate(cases,1):
        if not isinstance(case,dict) or not isinstance(case.get('query'),str) or not case['query'].strip():raise ValueError(f'Case {number} requires a query')
        candidates=case.get('candidates');relevant=case.get('relevant')
        if not isinstance(candidates,list) or not 1<=len(candidates)<=100 or not all(isinstance(value,str) and len(value)<=1000 for value in candidates):raise ValueError(f'Case {number} requires 1–100 bounded candidate strings')
        if type(relevant) is not int or not 0<=relevant<len(candidates):raise ValueError(f'Case {number} relevant index is invalid')
        results=[{'source':str(i),'line':1,'score':1,'excerpt':text} for i,text in enumerate(candidates)]
        kwargs={'runner':runner} if runner else {}
        ranked=rerank_results(case['query'],results,command,**kwargs);rank=next(i for i,item in enumerate(ranked,1) if int(item['source'])==relevant)
        reciprocal.append(1/rank);top1+=rank==1;top3+=rank<=3;top5+=rank<=5;ranks.append({'case':number,'rank':rank,'candidates':len(candidates)})
    encoded=json.dumps(cases,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    result={'cases':len(cases),'case_set_sha256':hashlib.sha256(encoded).hexdigest(),'mean_reciprocal_rank':sum(reciprocal)/len(reciprocal),'top_1_accuracy':top1/len(cases),'top_3_accuracy':top3/len(cases),'top_5_accuracy':top5/len(cases),'median_rank':statistics.median(item['rank'] for item in ranks),'worst_rank':max(item['rank'] for item in ranks)}
    if include_cases:result['case_ranks']=ranks
    return result
def compare_metrics(baseline,candidate):
    def unit_interval(result,key):
        value=result.get(key)
        return type(value) in (int,float) and math.isfinite(value) and 0<=value<=1
    for result in (baseline,candidate):
        if not isinstance(result,dict) or not all(unit_interval(result,key) for key in ('mean_reciprocal_rank','top_1_accuracy')):raise ValueError('Both benchmark results require finite MRR and top-1 accuracy between 0 and 1')
    deltas={'mean_reciprocal_rank_delta':candidate['mean_reciprocal_rank']-baseline['mean_reciprocal_rank'],'top_1_accuracy_delta':candidate['top_1_accuracy']-baseline['top_1_accuracy']}
    if 'top_3_accuracy' in baseline or 'top_3_accuracy' in candidate:
        if not all(unit_interval(result,'top_3_accuracy') for result in (baseline,candidate)):raise ValueError('Both benchmark results require finite top-3 accuracy between 0 and 1 when either supplies it')
        deltas['top_3_accuracy_delta']=candidate['top_3_accuracy']-baseline['top_3_accuracy']
    if 'top_5_accuracy' in baseline or 'top_5_accuracy' in candidate:
        if not all(unit_interval(result,'top_5_accuracy') for result in (baseline,candidate)):raise ValueError('Both benchmark results require finite top-5 accuracy between 0 and 1 when either supplies it')
        deltas['top_5_accuracy_delta']=candidate['top_5_accuracy']-baseline['top_5_accuracy']
    if 'median_rank' in baseline or 'median_rank' in candidate:
        if not all(type(result.get('median_rank')) in (int,float) and math.isfinite(result['median_rank']) and result['median_rank']>=1 for result in (baseline,candidate)):raise ValueError('Both benchmark results require finite positive median rank when either supplies it')
        deltas['median_rank_delta']=candidate['median_rank']-baseline['median_rank']
    if 'worst_rank' in baseline or 'worst_rank' in candidate:
        if not all(type(result.get('worst_rank')) is int and result['worst_rank']>=1 for result in (baseline,candidate)):raise ValueError('Both benchmark results require positive integer worst rank when either supplies it')
        deltas['worst_rank_delta']=candidate['worst_rank']-baseline['worst_rank']
    return deltas
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
    if type(minimum_cases) is not int or minimum_cases<1:raise ValueError('minimum_cases must be a positive integer')
    if type(minimum_mrr_delta) not in (int,float) or not math.isfinite(minimum_mrr_delta) or minimum_mrr_delta<0:raise ValueError('minimum_mrr_delta must be a finite non-negative number')
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
    if deltas.get('top_3_accuracy_delta',0)<0:reasons.append('top-3 accuracy regressed')
    if deltas.get('top_5_accuracy_delta',0)<0:reasons.append('top-5 accuracy regressed')
    if deltas.get('median_rank_delta',0)>0:reasons.append('median relevant-result rank regressed')
    if deltas.get('worst_rank_delta',0)>0:reasons.append('worst relevant-result rank regressed')
    diagnostics={}
    if 'case_ranks' in baseline or 'case_ranks' in candidate:
        diagnostics=compare_case_ranks(baseline,candidate)
        if diagnostics['regressed_cases']:reasons.append(f"{diagnostics['regressed_cases']} individual case ranks regressed")
    return {'promote':not reasons,'reasons':reasons,**deltas,**diagnostics}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('cases');parser.add_argument('reranker');parser.add_argument('--baseline-result',help='Compare with a previously saved benchmark JSON result');parser.add_argument('--minimum-cases',type=int,default=20);parser.add_argument('--minimum-mrr-delta',type=float,default=.02);parser.add_argument('--require-promotion',action='store_true',help='Exit 1 when the supplied baseline does not pass the promotion gate');args=parser.parse_args()
    try:
        if args.require_promotion and not args.baseline_result:raise ValueError('--require-promotion requires --baseline-result')
        cases=json.loads(Path(args.cases).read_text(encoding='utf-8'));evaluation=evaluate(cases,args.reranker,include_cases=True)
        if not args.baseline_result:
            print(json.dumps(evaluation,indent=2));return 0
        baseline=json.loads(Path(args.baseline_result).read_text(encoding='utf-8'))
        gate=promotion_gate(baseline,evaluation,args.minimum_cases,args.minimum_mrr_delta)
        print(json.dumps({'evaluation':evaluation,'promotion_gate':gate},indent=2))
        return int(args.require_promotion and not gate['promote'])
    except (OSError,ValueError,json.JSONDecodeError) as error:print(str(error),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
