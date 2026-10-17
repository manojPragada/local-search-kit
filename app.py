"""Offline keyword search with line-level source citations."""
import argparse
import json
from pathlib import Path
import re
import sys

def terms(text):return set(re.findall(r'\w+',text.casefold()))
def search(folder,query,limit=10):
    root=Path(folder).resolve()
    if not root.is_dir():raise ValueError('Search root must be a directory')
    wanted=terms(query)
    if not wanted:raise ValueError('Query must contain a word')
    if limit<1:raise ValueError('Limit must be positive')
    results=[]
    for path in sorted(root.rglob('*')):
        relative=path.relative_to(root)
        if any(part.startswith('.') for part in relative.parts) or path.is_symlink() or path.suffix.lower() not in {'.txt','.md'}:continue
        # Resolve parent symlinks too; never intentionally index outside the root.
        if not path.resolve().is_relative_to(root) or not path.is_file():continue
        try:
            if path.stat().st_size>1_048_576:continue
            text=path.read_text(encoding='utf-8')
        except (OSError,UnicodeError):continue
        for line,content in enumerate(text.splitlines(),1):
            hits=wanted & terms(content)
            if hits:
                results.append({'source':relative.as_posix(),'line':line,'score':len(hits)/len(wanted),'excerpt':content[:300]})
    return sorted(results,key=lambda r:(-r['score'],r['source'],r['line']))[:limit]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder');p.add_argument('query');p.add_argument('--limit',type=int,default=10);a=p.parse_args()
    try:print(json.dumps(search(a.folder,a.query,a.limit),indent=2));return 0
    except (OSError,ValueError) as exc:print(str(exc),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
