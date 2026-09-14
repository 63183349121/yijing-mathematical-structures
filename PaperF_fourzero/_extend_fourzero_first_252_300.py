#!/usr/bin/env python3
from __future__ import annotations
import json,time,urllib.request
from pathlib import Path
import sympy as sp
CACHE=Path('_factordb_2n_minus_1_cache.json');OUT=Path('_四零首解_252到300.json')
cache=json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
def save():CACHE.write_text(json.dumps(cache,indent=2),encoding='utf-8')
def get_factors(n):
    key=str(n)
    if key in cache:return cache[key],None
    if n<=100:
        fs=sorted(sp.factorint((1<<n)-1));cache[key]=fs;save();return fs,None
    u=f'https://factordb.com/api?query=2%5E{n}-1'
    req=urllib.request.Request(u,headers={'User-Agent':'codex-yishu-research/1.0'})
    try:
        with urllib.request.urlopen(req,timeout=60) as r:data=json.loads(r.read().decode())
    except Exception as e:
        return None,repr(e)
    if data.get('status')!='FF':return None,'status '+str(data.get('status'))
    fs=sorted({int(b) for b,e in data['factors']});cache[key]=fs;save();return fs,None
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
if OUT.exists():
    rows=json.loads(OUT.read_text(encoding='utf-8'));done={r['n'] for r in rows}
for n in range(252,301,2):
    if n in done:continue
    t=time.time();fs,err=get_factors(n)
    if fs is None:
        row={'n':n,'found':None,'tested':0,'seconds':round(time.time()-t,3),'error':err}
    else:
        found=None;tested=0
        for i in range(1,n//2):
            for j in range(i+1,n//2):
                tested+=1
                if isprim((1<<n)|code(n,i,j),n,fs):found=[i,j];break
            if found:break
        row={'n':n,'found':found,'tested':tested,'seconds':round(time.time()-t,3),'error':None}
    rows.append(row);rows.sort(key=lambda x:x['n']);OUT.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print(n,'found=',row['found'],'tested=',row['tested'],'sec=',row['seconds'],'err=',row['error'],flush=True)
print('done')
