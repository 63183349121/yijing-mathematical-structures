#!/usr/bin/env python3
"""Finite-population pair-association statistics for the n=2p family.

The input is the deterministic four-zero candidate set and the exact count
table produced by _analyze_zero_pairs.py.  For N = C(p-1,2) and N4 = N_4(2p),
define

    mu    = N4 / N,
    kappa = C(N4,2) / C(N,2) - mu^2.

Thus kappa is the difference between the probability that both members of a
uniformly chosen unordered pair of candidates are primitive and the square of
the candidate-level primitive frequency.  It is a finite-population
association statistic, not a variance of N4.
"""
from __future__ import annotations

from math import comb
import json
from pathlib import Path

COUNT_FILE = Path('_四零回文本原计数_6到200.json')
OUT_JSON = Path('_四零回文_2p_有限配对关联.json')
OUT_MD = Path('_四零回文_2p_有限配对关联.md')
MAX_P = 97


def primes_up_to(limit: int) -> list[int]:
    return [n for n in range(3, limit + 1, 2)
            if all(n % d for d in range(3, int(n ** 0.5) + 1, 2))]


def main() -> None:
    counts = {int(row['n']): int(row['primitive'])
              for row in json.loads(COUNT_FILE.read_text(encoding='utf-8'))}
    rows: list[dict[str, int | float | None]] = []

    for p in primes_up_to(MAX_P):
        n = 2 * p
        if n not in counts:
            continue
        N = comb(p - 1, 2)
        N4 = counts[n]
        if N < 2:
            mu = None
            kappa = None
        else:
            mu = N4 / N
            kappa = comb(N4, 2) / comb(N, 2) - mu * mu
        rows.append({'p': p, 'n': n, 'N': N, 'N4': N4,
                     'mu': mu, 'kappa': kappa})

    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n',
                        encoding='utf-8')

    lines = [
        '# Finite-population pair association for n=2p',
        '',
        'For the deterministic candidate set indexed by 1 <= i < j <= p-1:',
        '',
        '    mu = N4/N,',
        '    kappa = C(N4,2)/C(N,2) - mu^2.',
        '',
        'This is a finite-population association statistic, not a variance of N4.',
        '',
        '| p | n | N | N4 | mu | kappa |',
        '|---:|---:|---:|---:|---:|---:|',
    ]
    for row in rows:
        if row['kappa'] is None:
            lines.append(f"| {row['p']} | {row['n']} | {row['N']} | {row['N4']} | - | - |")
        else:
            lines.append(
                f"| {row['p']} | {row['n']} | {row['N']} | {row['N4']} | "
                f"{row['mu']:.6f} | {row['kappa']:.6e} |"
            )
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    for row in rows:
        print(row)
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')


if __name__ == '__main__':
    main()
