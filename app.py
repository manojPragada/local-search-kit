"""Offline keyword search with line-level source citations."""
import argparse
import hashlib
import sqlite3
import json
from pathlib import Path
import re
import sys
from reporting import markdown_report

def terms(text):return set(re.findall(r'\w+',text.casefold()))

def query_terms(query, limit, match):
    if type(limit) is not int or limit < 1:
        raise ValueError('Limit must be a positive integer')
    if match not in ('any', 'all'):
        raise ValueError('Match mode must be any or all')
    wanted = terms(query)
    if not wanted:
        raise ValueError('Query must contain a word')
    return wanted

def matching_score(wanted, available, match):
    hits = wanted & available
    if not hits or (match == 'all' and hits != wanted):
        return None
    return len(hits) / len(wanted)
def documents(root):
    for path in sorted(root.rglob('*')):
        relative=path.relative_to(root)
        if any(part.startswith('.') for part in relative.parts) or path.is_symlink() or path.suffix.lower() not in {'.txt','.md'}:continue
        # Resolve parent symlinks too; never intentionally index outside the root.
        if not path.resolve().is_relative_to(root) or not path.is_file():continue
        try:
            if path.stat().st_size>1_048_576:continue
            text=path.read_text(encoding='utf-8')
        except (OSError,UnicodeError):continue
        yield relative.as_posix(), text

def search(folder,query,limit=10,match='any'):
    root=Path(folder).resolve()
    if not root.is_dir():raise ValueError('Search root must be a directory')
    wanted=query_terms(query, limit, match)
    results=[]
    for relative, text in documents(root):
        for line,content in enumerate(text.splitlines(),1):
            score = matching_score(wanted, terms(content), match)
            if score is not None:
                results.append({'source':relative,'line':line,'score':score,'excerpt':content[:300]})
    return sorted(results,key=lambda r:(-r['score'],r['source'],r['line']))[:limit]

def sync_index(folder, database):
    root = Path(folder).resolve()
    if not root.is_dir():
        raise ValueError('Search root must be a directory')
    db = sqlite3.connect(database)
    try:
        with db:
            db.execute('CREATE TABLE IF NOT EXISTS lsk_meta (root TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS lsk_docs (path TEXT PRIMARY KEY, digest TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS lsk_lines (path TEXT NOT NULL,line INTEGER NOT NULL,tokens TEXT NOT NULL,excerpt TEXT NOT NULL,PRIMARY KEY(path,line))')
            bound = db.execute('SELECT root FROM lsk_meta').fetchone()
            if bound and bound[0] != str(root):
                raise ValueError('Index belongs to a different folder; choose a new database')
            if not bound:
                db.execute('INSERT INTO lsk_meta VALUES (?)', (str(root),))
            old = dict(db.execute('SELECT path,digest FROM lsk_docs'))
            seen = set()
            stats = {'added':0, 'updated':0, 'removed':0, 'unchanged':0}
            for source, text in documents(root):
                seen.add(source)
                digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
                if old.get(source) == digest:
                    stats['unchanged'] += 1
                    continue
                stats['updated' if source in old else 'added'] += 1
                db.execute('DELETE FROM lsk_lines WHERE path=?', (source,))
                db.executemany('INSERT INTO lsk_lines VALUES (?,?,?,?)',
                    ((source, number, json.dumps(sorted(terms(content))), content[:300])
                     for number, content in enumerate(text.splitlines(), 1)))
                db.execute('INSERT OR REPLACE INTO lsk_docs VALUES (?,?)', (source, digest))
            for source in old.keys() - seen:
                db.execute('DELETE FROM lsk_lines WHERE path=?', (source,))
                db.execute('DELETE FROM lsk_docs WHERE path=?', (source,))
                stats['removed'] += 1
        return stats
    finally:
        db.close()

def indexed_search(folder, query, database, limit=10, match='any'):
    wanted = query_terms(query, limit, match)
    sync_index(folder, database)
    db = sqlite3.connect(database)
    try:
        results = []
        for source, line, tokens, excerpt in db.execute('SELECT path,line,tokens,excerpt FROM lsk_lines'):
            score = matching_score(wanted, set(json.loads(tokens)), match)
            if score is not None:
                results.append({'source':source,'line':line,'score':score,'excerpt':excerpt})
        return sorted(results, key=lambda result:(-result['score'],result['source'],result['line']))[:limit]
    finally:
        db.close()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder');p.add_argument('query');p.add_argument('--limit',type=int,default=10);p.add_argument('--index',metavar='SQLITE_FILE',help='Maintain and query a local incremental index');p.add_argument('--format',choices=['json','markdown'],default='json');p.add_argument('--match',choices=['any','all'],default='any',help='Match any query word (default) or all distinct query words on the same line');a=p.parse_args()
    try:
        results = indexed_search(a.folder,a.query,a.index,a.limit,a.match) if a.index else search(a.folder,a.query,a.limit,a.match)
        print(markdown_report(a.query,results) if a.format=='markdown' else json.dumps(results,indent=2));return 0
    except (OSError,ValueError,sqlite3.Error) as exc:print(str(exc),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())



