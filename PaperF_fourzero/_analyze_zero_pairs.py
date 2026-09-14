#!/usr/bin/env python3
"""Analyze four-zero tail-palindromic primitive polynomials for even n."""
from __future__ import annotations

import json
import math
import time
import urllib.request
from itertools import combinations
from pathlib import Path

import sympy as sp

START = 6
END = 200
CACHE = Path('_factordb_2n_minus_1_cache.json')
OUT = Path('_四零回文本原_零位对_6到200.md')


def load_cache() -> dict[str, list[int]]:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding='utf-8'))
    return {}


def save_cache(cache: dict[str, list[int]]) -> None:
    CACHE.write_text(json.dumps(cache, indent=2), encoding='utf-8')


def factor_db_factors(n: int, cache: dict[str, list[int]]) -> list[int]:
    key = str(n)
    if key in cache:
        return cache[key]
    url = f'https://factordb.com/api?query=2%5E{n}-1'
    req = urllib.request.Request(url, headers={'User-Agent': 'codex-yishu-research/1.0'})
    with urllib.request.urlopen(req, timeout=45) as response:
        data = json.loads(response.read().decode('utf-8'))
    if data.get('status') != 'FF':
        raise RuntimeError(f'FactorDB has no complete factorization for n={n}: {data}')
    factors = []
    for base, exponent in data['factors']:
        factors.append(int(base))
    cache[key] = sorted(set(factors))
    save_cache(cache)
    return cache[key]


def distinct_prime_factors(n: int, cache: dict[str, list[int]]) -> list[int]:
    # For the earlier range, SymPy is fast and reproducible.
    if n <= 100:
        return sorted(sp.factorint((1 << n) - 1))
    return factor_db_factors(n, cache)


def deg(a: int) -> int:
    return a.bit_length() - 1


def polymod(a: int, m: int) -> int:
    dm = deg(m)
    while a and deg(a) >= dm:
        a ^= m << (deg(a) - dm)
    return a


def polymul(a: int, b: int, m: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a and deg(a) >= deg(m):
            a = polymod(a, m)
    return polymod(r, m)


def polypow(a: int, e: int, m: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = polymul(r, a, m)
        a = polymul(a, a, m)
        e >>= 1
    return r


def is_primitive(poly: int, n: int, factors: list[int]) -> bool:
    M = (1 << n) - 1
    if polypow(2, M, poly) != 1:
        return False
    return all(polypow(2, M // q, poly) != 1 for q in factors)


def code_with_zero_pairs(n: int, pairs: tuple[int, int]) -> int:
    bits = [1] * n
    for i in pairs:
        bits[i] = 0
        bits[n - 1 - i] = 0
    w = 0
    for b in bits:
        w = (w << 1) | b
    return w


def main() -> None:
    cache = load_cache()
    rows = []
    for n in range(START, END + 1, 2):
        t0 = time.time()
        factors = distinct_prime_factors(n, cache)
        m = n // 2
        working = []
        for i, j in combinations(range(1, m), 2):
            lower = code_with_zero_pairs(n, (i, j))
            poly = (1 << n) | lower
            if is_primitive(poly, n, factors):
                working.append((i, j))
        first = working[0] if working else None
        pair1 = next((j for i, j in working if i == 1), None)
        rows.append((n, len(working), first, pair1, round(time.time() - t0, 3)))
        print(n, len(working), first, pair1, rows[-1][4], flush=True)

        # Write a partial file after every n so a long run is not lost.
        lines = []
        lines.append('# 四零回文本原：零位对分布（偶数 n=6 到 200）')
        lines.append('')
        lines.append('尾码回文且恰有 4 个 0 时，零位必为两对 \((i,n-1-i)\)、\((j,n-1-j)\)。')
        lines.append('')
        lines.append('候选多项式为')
        lines.append('')
        lines.append('\\[ f_{n,i,j}(x)=\\frac{x^{n+1}+1}{x+1}+x^i+x^{n-1-i}+x^j+x^{n-1-j}. \\]')
        lines.append('')
        lines.append('| \\(n\\) | 工作零位对数 | 字典序最小 \((i,j)\) | 含 \(i=1\) 的最小 \(j\) |')
        lines.append('|---:|---:|---|---:|')
        for n0, count, first0, pair10, _ in rows:
            if first0 is None:
                fs = '无'
            else:
                fs = f'({first0[0]},{first0[1]})'
            ps = '无' if pair10 is None else str(pair10)
            lines.append(f'| {n0} | {count} | {fs} | {ps} |')
        OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('wrote', OUT)


if __name__ == '__main__':
    main()
