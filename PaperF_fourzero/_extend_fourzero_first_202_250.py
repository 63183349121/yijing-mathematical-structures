#!/usr/bin/env python3
from __future__ import annotations
import json,time,urllib.request
from pathlib import Path
import sympy as sp
CACHE=Path('_factordb_2n_minus_1_cache.json');OUT=Path('_四零首解_202到250.json')
cache=json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
def save():CACHE.write_text(json.dumps(cache,indent=2),encoding='utf-8')
def factors(n):
    k=str(n)
    if k in cache:return cache[k]
    if n<=100:
        fs=sorted(sp.factorint((1<<n)-1));cache[k]=fs;save();return fs
    u=f'https://factordb.com/api?query=2%5E{n}-1'
    req=urllib.request.Request(u,headers={'User-Agent':'codex-yishu-research/1.0'})
    with urllib.request.urlopen(req,timeout=45) as r:data=json.loads(r.read().decode())
    if data.get('status')!='FF':raise RuntimeError((n,data))
    fs=sorted({int(b) for b,e in data['factors']});cache[k]=fs;save();return fs
def deg(a):return a.bit_length()-1
def polymod(a,m):
    dm=deg(m)
    while a and deg(a)>=dm:a^=m<<(deg(a)-dm)
    return a
def polymul(a,b,m):
    r=0
    while b:
        if b&1:r^=a
        b>>=1;a<<=1
        if a and deg(a)>=deg(m):a=polymod(a,m)
    return polymod(r,m)
def polypow(a,e,m):
    r=1
    while e:
        if e&1:r=polymul(r,a,m)
        a=polymul(a,a,m);e>>=1
    return r
def isprim(poly,n,fs):
    M=(1<<n)-1
    return polypow(2,M,poly)==1 and all(polypow(2,M//q,poly)!=1 for q in fs)
def code(n,i,j):
    bits=[1]*n
    for t in (i,j):bits[t]=0;bits[n-1-t]=0
    w=0
    for b in bits:w=(w<<1)|b
    return w
rows=[];done=set()
if OUT.exists():rows=json.loads(OUT.read_text(encoding='utf-8'));done={r['n'] for r in rows}
for n in range(202,251,2):
    if n in done:continue
    t=time.time();fs=factors(n);found=None;tested=0
    for i in range(1,n//2):
        for j in range(i+1,n//2):
            tested+=1
            if isprim((1<<n)|code(n,i,j),n,fs):found=[i,j];break
        if found:break
    row={'n':n,'found':found,'tested':tested,'seconds':round(time.time()-t,3)}
    rows.append(row);rows.sort(key=lambda x:x['n']);OUT.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print(n,found,'tested',tested,'sec',row['seconds'],flush=True)
print('done')
