"""Offline evaluation harness for local reranker executables."""
import argparse,json,sys
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
    result={'cases':len(cases),'mean_reciprocal_rank':sum(reciprocal)/len(reciprocal),'top_1_accuracy':top1/len(cases)}
    if include_cases:result['case_ranks']=ranks
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('cases');parser.add_argument('reranker');args=parser.parse_args()
    try:
        cases=json.loads(Path(args.cases).read_text(encoding='utf-8'));print(json.dumps(evaluate(cases,args.reranker,include_cases=True),indent=2));return 0
    except (OSError,ValueError,json.JSONDecodeError) as error:print(str(error),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
