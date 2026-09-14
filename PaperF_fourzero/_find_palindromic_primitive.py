#!/usr/bin/env python3
"""
Search for tail-palindromic primitive polynomials over F_2.

Definition:
    f(x) = x^n + c_{n-1}x^{n-1} + ... + c_1 x + c_0
is tail-palindromic when
    (c_{n-1}, ..., c_0) = (c_0, ..., c_{n-1}).

For n even, primitive implies c_0=1, hence tail-palindromicity forces
c_{n-1}=1.  The remaining free bits are c_{n-2},...,c_{n/2}, so there are
2^(n/2-1) candidates.

Usage examples:
    python find_palindromic_primitive.py --n 40
    python find_palindromic_primitive.py --n 48 --limit 2000000
    python find_palindromic_primitive.py --n 60 --samples 1000000 --random

The primitivity test uses:
  * factorization of 2^n - 1;
  * x^(2^n-1) = 1 mod f;
  * x^((2^n-1)/q) != 1 mod f for every distinct prime q | 2^n - 1.
"""

from __future__ import annotations

import argparse
import random
import sys
import time


def poly_degree(a: int) -> int:
    return a.bit_length() - 1


def poly_mul_mod(a: int, b: int, mod: int, n: int) -> int:
    """Multiply in F_2[x]/(mod), with mod monic of degree n."""
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & (1 << n):
            a ^= mod
    return result


def poly_pow_mod(base: int, exponent: int, mod: int, n: int) -> int:
    result = 1
    while exponent:
        if exponent & 1:
            result = poly_mul_mod(result, base, mod, n)
        base = poly_mul_mod(base, base, mod, n)
        exponent >>= 1
    return result


def reverse_m_bits(value: int, m: int) -> int:
    out = 0
    for _ in range(m):
        out = (out << 1) | (value & 1)
        value >>= 1
    return out


def palindromic_lower_code(n: int, middle: int) -> int:
    """
    n must be even.
    middle has n/2-1 bits and determines c_{n-2},...,c_{n/2}.
    The high half is c_{n-1},...,c_{n/2}; c_{n-1}=1.
    The low half is its reverse.
    """
    m = n // 2
    high_half = (1 << (m - 1)) | middle
    low_half = reverse_m_bits(high_half, m)
    return (high_half << m) | low_half


def poly_text_from_lower(lower: int, n: int) -> str:
    terms = [f"x^{n}"]
    for i in range(n - 1, -1, -1):
        if (lower >> i) & 1:
            if i == 0:
                terms.append("1")
            elif i == 1:
                terms.append("x")
            else:
                terms.append(f"x^{i}")
    return " + ".join(terms)


def distinct_prime_factors(m: int, supplied: str | None, n: int) -> list[int]:
    if supplied:
        return [int(x.strip()) for x in supplied.split(",") if x.strip()]
    try:
        import sympy as sp
    except ImportError as exc:
        raise SystemExit(
            "SymPy is required for automatic factorization. "
            "Install sympy or pass --factors 3,5,..."
        ) from exc
    print(f"Factorizing 2^{n} - 1 ...", flush=True)
    t0 = time.time()
    fac = sp.factorint(m)
    print(f"Factorization: {fac}  ({time.time()-t0:.3f}s)", flush=True)
    return sorted(fac)


def is_primitive(lower: int, n: int, factors: list[int]) -> bool:
    poly = (1 << n) | lower
    M = (1 << n) - 1
    if poly_pow_mod(2, M, poly, n) != 1:
        return False
    for q in factors:
        if poly_pow_mod(2, M // q, poly, n) == 1:
            return False
    return True


def search_scan(n: int, factors: list[int], limit: int | None, find_all: bool = False) -> None:
    m = n // 2
    total = 1 << (m - 1)
    if limit is None or limit > total:
        limit = total
    t0 = time.time()
    tested = 0
    found_count = 0
    for middle in range(limit):
        lower = palindromic_lower_code(n, middle)
        tested += 1
        if is_primitive(lower, n, factors):
            print("\nFOUND")
            print(f"n = {n}")
            print(f"tail code (hex) = 0x{lower:0{(n+3)//4}x}")
            print(f"tail code (bin) = {lower:0{n}b}")
            print(f"lower integer = {lower}")
            print(f"polynomial = {poly_text_from_lower(lower, n)}")
            found_count += 1
            if not find_all:
                return
        if tested % 10000 == 0:
            rate = tested / max(time.time() - t0, 1e-9)
            print(f"tested {tested}/{limit}  rate={rate:.0f}/s", flush=True)
    if find_all:
        print(f"\nFinished scan of {tested} candidates; found {found_count} solutions.")
    else:
        print(f"\nNo solution found in first {tested} candidates.")
    print("This is not a nonexistence proof.")


def search_random(n: int, factors: list[int], samples: int, seed: int, find_all: bool = False) -> None:
    m = n // 2
    rng = random.Random(seed)
    t0 = time.time()
    found_count = 0
    for tested in range(1, samples + 1):
        middle = rng.getrandbits(m - 1)
        lower = palindromic_lower_code(n, middle)
        if is_primitive(lower, n, factors):
            print("\nFOUND")
            print(f"n = {n}")
            print(f"tail code (bin) = {lower:0{n}b}")
            print(f"lower integer = {lower}")
            print(f"polynomial = {poly_text_from_lower(lower, n)}")
            found_count += 1
            if not find_all:
                return
        if tested % 10000 == 0:
            rate = tested / max(time.time() - t0, 1e-9)
            print(f"tested {tested}/{samples}  rate={rate:.0f}/s", flush=True)
    print(f"\nNo solution found in {samples} random samples.")
    print("This is not a nonexistence proof.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=40, help="even polynomial degree")
    parser.add_argument("--limit", type=int, default=200000,
                        help="number of candidates in deterministic scan; 0 means all")
    parser.add_argument("--random", action="store_true",
                        help="use random sampling instead of deterministic scan")
    parser.add_argument("--all", action="store_true",
                        help="in scan mode, list all solutions in the scanned range")
    parser.add_argument("--samples", type=int, default=200000,
                        help="number of random candidates")
    parser.add_argument("--seed", type=int, default=20260912)
    parser.add_argument("--factors", type=str, default=None,
                        help="comma-separated distinct prime factors of 2^n-1")
    args = parser.parse_args()

    n = args.n
    if n < 2 or n % 2:
        raise SystemExit("This script currently supports even n >= 2.")

    M = (1 << n) - 1
    factors = distinct_prime_factors(M, args.factors, n)

    print(f"n = {n}")
    print(f"M = 2^{n} - 1 = {M}")
    print(f"distinct prime factors = {factors}")
    print(f"free candidate bits = {n//2 - 1}")
    print(f"number of palindromic candidates with c0=1 = {1 << (n//2 - 1)}")

    if args.random:
        search_random(n, factors, args.samples, args.seed, args.all)
    else:
        limit = None if args.limit == 0 else args.limit
        search_scan(n, factors, limit, args.all)


if __name__ == "__main__":
    main()



