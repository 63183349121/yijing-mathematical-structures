#!/usr/bin/env python3
"""Independent certificate for the even-characteristic case k = 1..29.

For each k this checks, using only deterministic integer/polynomial arithmetic:

  * MODULI[k] is an irreducible degree-k polynomial over F_2;
  * A_VALUES[k] is an element a of F_{2^k} with absolute trace 1,
    so x^2 + x + a is irreducible over F_{2^k};
  * a root t of x^2 + x + a in F_{2^{2k}} has exact order 2^{2k} - 1.

The factorizations of 2^{2k}-1 and the chosen a-values are embedded in the
script, so rerunning it does not require SymPy or network access.
"""

MODULI = {
    1: 0x3,
    2: 0x7,
    3: 0xB,
    4: 0x13,
    5: 0x25,
    6: 0x43,
    7: 0x83,
    8: 0x11B,
    9: 0x203,
    10: 0x409,
    11: 0x805,
    12: 0x1009,
    13: 0x201B,
    14: 0x4021,
    15: 0x8003,
    16: 0x1002B,
    17: 0x20009,
    18: 0x40009,
    19: 0x80027,
    20: 0x100009,
    21: 0x200005,
    22: 0x400003,
    23: 0x800021,
    24: 0x100001B,
    25: 0x2000009,
    26: 0x400001B,
    27: 0x8000027,
    28: 0x10000003,
    29: 0x20000005,
}

# Complete prime-power factorizations of 2^(2k)-1.
FACTORS = {
    1: [(3, 1)],
    2: [(3, 1), (5, 1)],
    3: [(3, 2), (7, 1)],
    4: [(3, 1), (5, 1), (17, 1)],
    5: [(3, 1), (11, 1), (31, 1)],
    6: [(3, 2), (5, 1), (7, 1), (13, 1)],
    7: [(3, 1), (43, 1), (127, 1)],
    8: [(3, 1), (5, 1), (17, 1), (257, 1)],
    9: [(3, 3), (7, 1), (19, 1), (73, 1)],
    10: [(3, 1), (5, 2), (11, 1), (31, 1), (41, 1)],
    11: [(3, 1), (23, 1), (89, 1), (683, 1)],
    12: [(3, 2), (5, 1), (7, 1), (13, 1), (17, 1), (241, 1)],
    13: [(3, 1), (2731, 1), (8191, 1)],
    14: [(3, 1), (5, 1), (29, 1), (43, 1), (113, 1), (127, 1)],
    15: [(3, 2), (7, 1), (11, 1), (31, 1), (151, 1), (331, 1)],
    16: [(3, 1), (5, 1), (17, 1), (257, 1), (65537, 1)],
    17: [(3, 1), (43691, 1), (131071, 1)],
    18: [(3, 3), (5, 1), (7, 1), (13, 1), (19, 1), (37, 1), (73, 1), (109, 1)],
    19: [(3, 1), (174763, 1), (524287, 1)],
    20: [(3, 1), (5, 2), (11, 1), (17, 1), (31, 1), (41, 1), (61681, 1)],
    21: [(3, 2), (7, 2), (43, 1), (127, 1), (337, 1), (5419, 1)],
    22: [(3, 1), (5, 1), (23, 1), (89, 1), (397, 1), (683, 1), (2113, 1)],
    23: [(3, 1), (47, 1), (178481, 1), (2796203, 1)],
    24: [(3, 2), (5, 1), (7, 1), (13, 1), (17, 1), (97, 1), (241, 1), (257, 1), (673, 1)],
    25: [(3, 1), (11, 1), (31, 1), (251, 1), (601, 1), (1801, 1), (4051, 1)],
    26: [(3, 1), (5, 1), (53, 1), (157, 1), (1613, 1), (2731, 1), (8191, 1)],
    27: [(3, 4), (7, 1), (19, 1), (73, 1), (87211, 1), (262657, 1)],
    28: [(3, 1), (5, 1), (17, 1), (29, 1), (43, 1), (113, 1), (127, 1), (15790321, 1)],
    29: [(3, 1), (59, 1), (233, 1), (1103, 1), (2089, 1), (3033169, 1)],
}

A_VALUES = {
    1: 1,
    2: 3,
    3: 5,
    4: 13,
    5: 19,
    6: 52,
    7: 71,
    8: 200,
    9: 43,
    10: 203,
    11: 1317,
    12: 926,
    13: 7876,
    14: 14103,
    15: 25279,
    16: 7790,
    17: 71003,
    18: 192132,
    19: 47535,
    20: 437986,
    21: 1406219,
    22: 2400592,
    23: 7115513,
    24: 3710660,
    25: 6816173,
    26: 40926510,
    27: 115976990,
    28: 262962386,
    29: 208254302,
}


def poly_degree(a: int) -> int:
    return a.bit_length() - 1


def poly_divmod(a: int, b: int) -> tuple[int, int]:
    if b == 0:
        raise ZeroDivisionError("polynomial division by zero")
    q = 0
    db = poly_degree(b)
    while a and poly_degree(a) >= db:
        shift = poly_degree(a) - db
        q ^= 1 << shift
        a ^= b << shift
    return q, a


def poly_gcd(a: int, b: int) -> int:
    while b:
        _, r = poly_divmod(a, b)
        a, b = b, r
    return a


def distinct_prime_divisors(n: int) -> list[int]:
    out = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        out.append(n)
    return out


def gf_mul(a: int, b: int, mod: int, k: int) -> int:
    """Multiply in F_2[x]/(mod), represented as degree < k bit integers."""
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a & (1 << k):
            a ^= mod
    return r


def gf_pow(a: int, e: int, mod: int, k: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = gf_mul(r, a, mod, k)
        a = gf_mul(a, a, mod, k)
        e >>= 1
    return r


def absolute_trace(a: int, mod: int, k: int) -> int:
    """Tr_{F_{2^k}/F_2}(a) = a + a^2 + ... + a^(2^(k-1))."""
    result = 0
    term = a
    for _ in range(k):
        result ^= term
        term = gf_mul(term, term, mod, k)
    return result


def is_irreducible(mod: int, k: int) -> bool:
    """Rabin irreducibility test over F_2 for a degree-k polynomial."""
    x = 2
    x_mod = gf_mul(1, x, mod, k)
    if gf_pow(x, 1 << k, mod, k) != x_mod:
        return False
    for r in distinct_prime_divisors(k):
        if poly_gcd(mod, gf_pow(x, 1 << (k // r), mod, k) ^ x_mod) != 1:
            return False
    return True


def ext_mul(left: tuple[int, int], right: tuple[int, int], a: int, mod: int, k: int) -> tuple[int, int]:
    """Multiply u+v*t in F_{2^k}[t]/(t^2+t+a)."""
    u, v = left
    U, V = right
    uu = gf_mul(u, U, mod, k)
    vv = gf_mul(v, V, mod, k)
    return (
        uu ^ gf_mul(a, vv, mod, k),
        gf_mul(u, V, mod, k) ^ gf_mul(U, v, mod, k) ^ vv,
    )


def ext_pow(base: tuple[int, int], e: int, a: int, mod: int, k: int) -> tuple[int, int]:
    result = (1, 0)
    while e:
        if e & 1:
            result = ext_mul(result, base, a, mod, k)
        base = ext_mul(base, base, a, mod, k)
        e >>= 1
    return result


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    # Deterministic for all n < 2^64.
    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def verify_one(k: int) -> tuple[int, int, int]:
    mod = MODULI[k]
    a = A_VALUES[k]
    factors = FACTORS[k]
    assert is_irreducible(mod, k), (k, "field modulus is reducible")
    product = 1
    for p, e in factors:
        assert is_prime(p), (k, "non-prime factor", p)
        product *= p ** e
    M = (1 << (2 * k)) - 1
    assert product == M, (k, "factorization product mismatch")
    assert absolute_trace(a, mod, k) == 1, (k, "absolute trace is not 1")

    t = (0, 1)
    assert ext_mul(t, t, a, mod, k) == (a, 1), (k, "t^2 != t+a")
    assert ext_pow(t, 1 << k, a, mod, k) == (1, 1), (k, "Frobenius trace is not 1")
    assert ext_pow(t, M, a, mod, k) == (1, 0), (k, "root does not have order dividing M")
    for p, _ in factors:
        assert ext_pow(t, M // p, a, mod, k) != (1, 0), (k, "root order fails at prime", p)
    return mod, a, len(factors)


def main() -> None:
    print("k  field_modulus  a_value  distinct_primes  M_bits  status")
    for k in range(1, 30):
        mod, a, omega = verify_one(k)
        print(f"{k:2d}  0x{mod:08x}  0x{a:08x}  {omega:2d}  {(2*k):2d}  OK")
    print("All certificates verified.")


if __name__ == "__main__":
    main()


