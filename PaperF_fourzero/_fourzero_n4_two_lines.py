#!/usr/bin/env python3
"""Exact n -> n+4 recursion on two residue lines.

State at level n is the full set of gaps (x,y,z), not only primitive nodes.
Each step applies the six increments of total size two, deduplicates, then
re-tests primitivity of every target polynomial.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
import sympy as sp
import _analyze_zero_pairs as az

INCREMENTS = [(1,1,0),(1,0,1),(0,1,1),(2,0,0),(0,2,0),(0,0,2)]

def compositions(t):
    for x in range(t+1):
        for y in range(t-x+1):
            z=t-x-y
            yield (x,y,z)

def code_from_gaps(n,q):
    x,y,z=q
    assert 2*(x+y+z+3)==n
    i=x+1; j=x+y+2
    bits=['1']*n
    for a in (i,j):
        bits[a]='0'; bits[n-1-a]='0'
    return ''.join(bits)

def factors(n,cache):
    if str(n) in cache:
        return cache[str(n)]
    return sorted(sp.factorint((1<<n)-1))

def label_level(n, nodes, cache):
    fac=factors(n,cache)
    out={}
    for q in nodes:
        s=code_from_gaps(n,q)
        out[q]=az.is_primitive((1<<n)|int(s,2),n,fac)
    return out

def step(n,nodes):
    nxt=set()
    for x,y,z in nodes:
        for a,b,c in INCREMENTS:
            nxt.add((x+a,y+b,z+c))
    t=(n+4-6)//2
    expected=set(compositions(t))
    assert nxt==expected, (n,len(nxt),len(expected))
    return nxt

def run_line(start,end,cache):
    assert start%4 in (0,2) and start%2==0
    t=(start-6)//2
    nodes=set(compositions(t))
    rows=[]
    n=start
    while n<=end:
        labels=label_level(n,nodes,cache)
        primitive=sorted(q for q,v in labels.items() if v)
        rows.append({'n':n,'nodes':len(nodes),'primitive_count':len(primitive),'primitive':primitive})
        if n==end: break
        nodes=step(n,nodes)
        n+=4
    return rows

def main():
    start=int(sys.argv[1]) if len(sys.argv)>1 else 6
    end=int(sys.argv[2]) if len(sys.argv)>2 else 60
    out=Path(sys.argv[3]) if len(sys.argv)>3 else Path(f'_四零_n4递推_{start}_{end}.json')
    cache=json.loads(Path('_factordb_2n_minus_1_cache.json').read_text(encoding='utf-8'))
    rows=run_line(start,end,cache)
    # Cross-check against the known full count table.
    known={r['n']:r['primitive'] for r in json.loads(Path('_四零回文本原计数_6到200.json').read_text(encoding='utf-8'))}
    for r in rows:
        if r['n'] in known:
            assert r['primitive_count']==known[r['n']], (r['n'],r['primitive_count'],known[r['n']])
    out.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print(out)
    for r in rows:
        print(r['n'],r['nodes'],r['primitive_count'],r['primitive'])

if __name__=='__main__':
    main()
