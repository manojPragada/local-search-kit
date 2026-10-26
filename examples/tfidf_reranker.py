#!/usr/bin/env python3
"""Tiny offline TF-IDF protocol example; a baseline, not semantic search."""
import json,math,re,sys

def words(text):return re.findall(r'\w+',text.casefold())
def main():
    value=json.load(sys.stdin);query=words(value.get('query',''));candidates=value.get('candidates',[])
    if value.get('version')!=1 or not query or not isinstance(candidates,list) or len(candidates)>100:raise ValueError('Expected reranker protocol version 1 with a query and at most 100 candidates')
    docs=[words(item.get('excerpt','')) for item in candidates];terms=set(query)
    idf={term:math.log((1+len(docs))/(1+sum(term in doc for doc in docs)))+1 for term in terms}
    q={term:query.count(term)*idf[term] for term in terms};qnorm=math.sqrt(sum(v*v for v in q.values())) or 1
    scores=[]
    for doc in docs:
        vector={term:doc.count(term)*idf[term] for term in terms};norm=math.sqrt(sum(v*v for v in vector.values()))
        scores.append(sum(q[t]*vector[t] for t in terms)/(qnorm*norm) if norm else 0)
    print(json.dumps(scores));return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,TypeError,json.JSONDecodeError) as error:print(str(error),file=sys.stderr);sys.exit(2)
