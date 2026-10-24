"""Verification script for the rectangular case of Theorem B in "Balanced
squares, impossible rectangles, and Bertrand's Postulate": no balanced
m x n array exists for m < n (arrangements of 1..mn whose sets of distinct
row and column products are equal).

Checks the computational inputs of the proof, plus independent
corroboration:

  1. A direct check against Lemma 8: for every pair 2 <= m < n with
     mn <= 99, the lonely prime count ell(m,n) = pi(mn) - pi(mn/2)
     satisfies ell >= m-1, so Lemma 8 rules out every such shape.
  2. The area boundary of Proposition 6: pi(100) - pi(50) = 10, and
     mn >= 100 with m < n forces ell > m for every divisor pair (checked
     directly for all such pairs with mn up to 200; beyond that the paper's
     Theorem A applies).
  3. Corroboration: exhaustive enumeration over pairs of orthogonal block
     partitions confirms that no balanced array exists for the six
     smallest shapes 2x3, 2x4, 2x5, 2x6, 3x4, 3x5.
  4. The scalar reduction of Proposition 9: (ell+2)(ell+3) > N for every
     2 <= N <= 96, the certificate table of N_max per ell, and the minimum
     margin 2 at N = 10, 28, 40.

Pure standard library (Python 3.8+).  Each check prints PASS or FAIL; the
script exits non-zero if any check fails.
"""

from __future__ import annotations

import sys
from itertools import combinations

FAILURES: list = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILURES.append(name)


# -- primes up to 200 --------------------------------------------------------
N = 200
sieve = bytearray([1]) * (N + 1)
sieve[0] = sieve[1] = 0
for i in range(2, 15):
    if sieve[i]:
        sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
pi = [0] * (N + 1)
acc = 0
for i in range(N + 1):
    acc += sieve[i]
    pi[i] = acc


def ell(m: int, n: int) -> int:
    return pi[m * n] - pi[m * n // 2]


# -- 1. direct check against Lemma 8 ----------------------------------------
low = [
    (m, n, ell(m, n))
    for m in range(2, 10)
    for n in range(m + 1, 51)
    if m * n <= 99 and ell(m, n) <= m - 2
]
check("no pair 2<=m<n, mn<=99 has ell <= m-2", not low, str(low))

# -- 2. the area boundary of Proposition 6 ----------------------------------
check("pi(100) - pi(50) = 10", pi[100] - pi[50] == 10)
big = [
    (m, n)
    for a in range(100, 201)
    for m in range(2, 15)
    if a % m == 0
    for n in [a // m]
    if m < n and ell(m, n) <= m
]
check("every m<n with 100 <= mn <= 200 has ell > m", not big, str(big[:5]))


# -- 3. corroborating enumeration -------------------------------------------
def prod(t) -> int:
    p = 1
    for x in t:
        p *= x
    return p


def partitions(nblocks: int, bsize: int, total: int):
    def rec(rem, acc):
        if not rem:
            yield tuple(acc)
            return
        first, rest = rem[0], rem[1:]
        for combo in combinations(rest, bsize - 1):
            s = set(combo)
            acc.append((first,) + combo)
            yield from rec(tuple(x for x in rest if x not in s), acc)
            acc.pop()

    yield from rec(tuple(range(1, total + 1)), [])


def count_set_balanced(m: int, n: int) -> int:
    """Count orthogonal pairs (rows: m blocks of n, columns: n blocks of m)
    with equal SETS of distinct block products; each such pair corresponds to
    a family of balanced arrays and vice versa."""
    cols_by_key: dict = {}
    for cp in partitions(n, m, m * n):
        key = frozenset(prod(b) for b in cp)
        cols_by_key.setdefault(key, []).append(
            tuple(sum(1 << x for x in b) for b in cp)
        )
    found = 0
    for rp in partitions(m, n, m * n):
        key = frozenset(prod(b) for b in rp)
        rmasks = [sum(1 << x for x in b) for b in rp]
        for cmasks in cols_by_key.get(key, []):
            if all(bin(r & c).count("1") == 1 for r in rmasks for c in cmasks):
                found += 1
    return found


for m, n in [(2, 3), (2, 4), (2, 5), (2, 6), (3, 4), (3, 5)]:
    check(
        f"exhaustive enumeration: no balanced {m}x{n} array",
        count_set_balanced(m, n) == 0,
    )

# -- 4. the scalar reduction of Proposition 9 --------------------------------
# (ell+2)(ell+3) > N for every N <= 96, certified in the paper by the table
# of the largest N attaining each value of ell, with minimum margin 2.
ell_all = {N: pi[N] - pi[N // 2] for N in range(2, 97)}
check(
    "(ell+2)(ell+3) > N for every N <= 96",
    all((e + 2) * (e + 3) > N for N, e in ell_all.items()),
)

CERTIFICATE = {1: 10, 2: 16, 3: 28, 4: 40, 5: 46, 6: 58, 7: 66, 8: 70, 9: 96, 10: 93}
nmax: dict = {}
for N, e in ell_all.items():
    nmax[e] = max(nmax.get(e, 0), N)
check(
    "certificate table: N_max for each ell occurring on 2 <= N <= 96",
    nmax == CERTIFICATE,
    str(sorted(nmax.items())),
)

margins = {N: (e + 2) * (e + 3) - N for N, e in ell_all.items()}
check(
    "minimum margin is 2, attained exactly at N = 10, 28, 40",
    min(margins.values()) == 2
    and {N for N, m in margins.items() if m == 2} == {10, 28, 40},
)

print(f"\n{len(FAILURES)} failure(s).")
sys.exit(1 if FAILURES else 0)
