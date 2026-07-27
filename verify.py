"""Verification script for "Extending Bertrand's Postulate, and a Puzzle"
by Jayanta Manoharmayum and Vamshi Jandhyala.

Verifies every finite computation in the paper:

  1. Theorem A over 97 <= x < 1,600,000, with equality only at x = 100 and
     failure exactly on (100, 101).  The range covers both finite-check
     routes discussed in Remark 2.6 (x ~ 2116 for the estimate of
     Proposition 2.2, x ~ 1.518e6 for the route through Erdos's bound).
  2. The failure window [94, 97) of Remark 2.4.
  3. The finite check of Lemma 2.3 (51 <= n <= 1057), including the
     minimum margin at n = 53 and the endpoint values.
  4. The Ramanujan primes R_1..R_20 of Remark 2.7, computed from Sondow's
     definition, and the inequality 4m ln(4m) <= (m-1)^2 at m = 21.
  5. The crossovers of Remark 2.6 (Ramanujan's bound: n = 2366; Erdos's
     bound: t >= 1232.02).
  6. The step-function data of Figure 1.
  7. The balanced arrays of Figures 2-4 (n = 4..8 and n = 10), including
     the lonely-prime diagonal for n = 10.
  8. The censuses of Section 3.5: n = 3 (432 balanced arrays, six classes
     of 72, with the six listed row-product multisets) and n = 4 (2780
     classes, 3,202,560 arrays).  The n = 4 count uses the
     orthogonal-partition-pair method described in the paper; the same
     method is validated against the independent n = 3 brute force.

Pure standard library (Python 3.8+), no dependencies.  Each check prints
PASS or FAIL; the script exits non-zero if any check fails.  Total runtime
is a few minutes, dominated by the Theorem A sweep and the n = 4 census.
"""

from __future__ import annotations

import math
import sys
from collections import Counter
from itertools import combinations, permutations

FAILURES: list = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# Prime tables: sieve of Eratosthenes and prefix prime counts up to 1.6e6.
# ---------------------------------------------------------------------------
N = 1_600_000
sieve = bytearray([1]) * (N + 1)
sieve[0] = sieve[1] = 0
for i in range(2, int(N**0.5) + 1):
    if sieve[i]:
        sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
pi = [0] * (N + 1)
acc = 0
for i in range(N + 1):
    acc += sieve[i]
    pi[i] = acc


def count(k: int) -> int:
    """pi(x) - pi(x/2), constant for real x in [k, k+1) (k an integer)."""
    return pi[k] - pi[k // 2]


# ---------------------------------------------------------------------------
# 1-2. Theorem A and the sharpness window of Remark 2.4.
#
# On [k, k+1) the count is constant, so the strict inequality
# count > sqrt(x) throughout [k, k+1) is equivalent to count^2 >= k+1.
# ---------------------------------------------------------------------------
bad = [k for k in range(97, N) if k != 100 and count(k) ** 2 < k + 1]
check("Theorem A on [97, 1.6e6) outside (100,101)", not bad, str(bad[:5]))
check(
    "equality exactly at x = 100",
    count(100) == 10 and [k for k in range(97, N) if count(k) ** 2 == k] == [100],
)
check(
    "failure window is exactly [94, 97)",
    all(count(k) == 9 for k in (94, 95, 96)) and count(93) == 10 == count(97),
)

# ---------------------------------------------------------------------------
# 3. Lemma 2.3: pi(2n) - pi(n) > sqrt(2n+2) for 51 <= n <= 1057.
# ---------------------------------------------------------------------------
margins = [(pi[2 * n] - pi[n] - math.sqrt(2 * n + 2), n) for n in range(51, 1058)]
check("Lemma 2.3 finite check on 51..1057", all(d > 0 for d, _ in margins))
check(
    "minimum margin at n = 53",
    min(margins)[1] == 53,
    f"pi(106)-pi(53) = {pi[106]}-{pi[53]}",
)
check(
    "endpoint values as printed", pi[102] - pi[51] == 11 and pi[2114] - pi[1057] == 142
)

# ---------------------------------------------------------------------------
# 4. Ramanujan primes (Remark 2.7).  R_m is the smallest integer such that
# count >= m for all x >= R_m; since the count changes only at integers,
# R_m = 1 + (largest integer k with count(k) < m).
# ---------------------------------------------------------------------------
R = {m: max(k for k in range(1, 5000) if count(k) < m) + 1 for m in range(1, 21)}
check("Ramanujan's list R_1..R_5", [R[m] for m in range(1, 6)] == [2, 11, 17, 29, 41])
check("R_10 = 97 and R_11 = 101", (R[10], R[11]) == (97, 101))
check(
    "R_12..R_20 as printed",
    [R[m] for m in range(12, 21)] == [107, 127, 149, 151, 167, 179, 181, 227, 229],
)
check("every R_m is prime (m <= 20)", all(sieve[R[m]] for m in R))
check(
    "4m ln(4m) <= (m-1)^2 at m = 21",
    4 * 21 * math.log(84) < 400,
    f"{4 * 21 * math.log(84):.1f} < 400",
)

# ---------------------------------------------------------------------------
# 5. Crossovers of Remark 2.6.
# ---------------------------------------------------------------------------
ram = lambda x: (x / 6 - 3 * math.sqrt(x)) / math.log(x)
check(
    "Ramanujan-bound route: last failure at n = 2365",
    ram(4730) < math.sqrt(4732)
    and ram(4732) > math.sqrt(4734)
    and max(n for n in range(1058, 6000) if ram(2 * n) <= math.sqrt(2 * n + 2)) == 2365,
)
check(
    "Erdos-bound route: crossover t >= 1232.02",
    1232.01 / math.log(1232.01) < 120 / math.log(2) <= 1232.02 / math.log(1232.02),
)

# ---------------------------------------------------------------------------
# 6. Figure 1: change points of the step function on [50, 150].
# ---------------------------------------------------------------------------
FIG1 = [
    (50, 6),
    (53, 7),
    (58, 6),
    (59, 7),
    (61, 8),
    (62, 7),
    (67, 8),
    (71, 9),
    (73, 10),
    (74, 9),
    (79, 10),
    (82, 9),
    (83, 10),
    (86, 9),
    (89, 10),
    (94, 9),
    (97, 10),
    (101, 11),
    (103, 12),
    (106, 11),
    (107, 12),
    (109, 13),
    (113, 14),
    (118, 13),
    (122, 12),
    (127, 13),
    (131, 14),
    (134, 13),
    (137, 14),
    (139, 15),
    (142, 14),
    (146, 13),
    (149, 14),
]
recomputed = [(50, count(50))]
for k in range(51, 151):
    if count(k) != recomputed[-1][1]:
        recomputed.append((k, count(k)))
check("Figure 1 step data", recomputed == FIG1)

# ---------------------------------------------------------------------------
# 7. The balanced arrays of Figures 2-4.
# ---------------------------------------------------------------------------
ARRAYS = {
    4: [[13, 16, 3, 10], [4, 6, 14, 2], [8, 7, 5, 9], [15, 1, 12, 11]],
    5: [
        [17, 2, 7, 15, 20],
        [14, 25, 9, 11, 16],
        [6, 21, 13, 3, 12],
        [10, 22, 18, 23, 1],
        [5, 24, 4, 8, 19],
    ],
    6: [
        [34, 10, 5, 30, 27, 14],
        [25, 19, 36, 11, 7, 2],
        [18, 33, 29, 4, 20, 8],
        [3, 35, 22, 31, 32, 9],
        [15, 12, 16, 21, 17, 26],
        [28, 1, 6, 24, 13, 23],
    ],
    7: [
        [5, 38, 1, 26, 40, 44, 24],
        [19, 29, 22, 28, 6, 20, 35],
        [10, 11, 31, 36, 46, 3, 2],
        [32, 42, 18, 37, 39, 7, 21],
        [13, 25, 23, 9, 41, 34, 48],
        [33, 14, 4, 12, 17, 43, 45],
        [16, 8, 30, 49, 15, 27, 47],
    ],
    8: [
        [37, 8, 5, 63, 24, 18, 31, 30],
        [12, 38, 19, 48, 58, 3, 15, 39],
        [2, 57, 41, 14, 44, 51, 10, 60],
        [7, 6, 45, 43, 40, 9, 49, 22],
        [50, 29, 11, 33, 47, 46, 56, 64],
        [54, 27, 32, 1, 23, 53, 17, 13],
        [62, 20, 34, 21, 28, 4, 59, 35],
        [36, 26, 42, 25, 55, 52, 16, 61],
    ],
    10: [
        [53, 46, 45, 31, 68, 24, 20, 72, 18, 65],
        [78, 89, 64, 69, 33, 75, 57, 14, 8, 49],
        [93, 100, 67, 81, 32, 41, 4, 94, 98, 74],
        [15, 91, 62, 83, 90, 10, 84, 11, 6, 23],
        [34, 66, 21, 26, 79, 86, 12, 13, 36, 60],
        [30, 1, 82, 70, 43, 59, 88, 50, 99, 17],
        [40, 56, 63, 2, 9, 44, 97, 38, 95, 58],
        [16, 76, 47, 25, 52, 77, 87, 71, 48, 3],
        [27, 54, 80, 28, 7, 51, 19, 96, 73, 55],
        [92, 42, 37, 22, 39, 5, 35, 29, 85, 61],
    ],
}


def prod(xs) -> int:
    p = 1
    for x in xs:
        p *= x
    return p


for n, A in ARRAYS.items():
    entries_ok = sorted(x for row in A for x in row) == list(range(1, n * n + 1))
    rows = [prod(r) for r in A]
    cols = [prod(c) for c in zip(*A)]
    check(
        f"Figure array n = {n}: entries 1..n^2, balanced, row_t = col_t",
        entries_ok and rows == cols,
    )
check(
    "n = 10 diagonal is the ten lonely primes",
    sorted(ARRAYS[10][i][i] for i in range(10))
    == [p for p in range(51, 101) if sieve[p]],
)

# ---------------------------------------------------------------------------
# 8a. n = 3 census by brute force over all 9! arrangements.
# ---------------------------------------------------------------------------
balanced3 = []
for p in permutations(range(1, 10)):
    r = (p[0] * p[1] * p[2], p[3] * p[4] * p[5], p[6] * p[7] * p[8])
    c = (p[0] * p[3] * p[6], p[1] * p[4] * p[7], p[2] * p[5] * p[8])
    if sorted(r) == sorted(c):
        balanced3.append(tuple(sorted(r)))
msets = Counter(balanced3)
check(
    "n = 3: 432 arrays in six classes of 72",
    len(balanced3) == 432 and len(msets) == 6 and set(msets.values()) == {72},
)
check(
    "n = 3 row-product multisets as printed",
    sorted(msets)
    == [
        (30, 56, 216),
        (30, 72, 168),
        (40, 42, 216),
        (40, 54, 168),
        (42, 72, 120),
        (54, 56, 120),
    ],
)


# ---------------------------------------------------------------------------
# 8b. Censuses via orthogonal partition pairs (Section 3.5).
#
# A balanced n x n array corresponds to an ordered pair (R, C) of partitions
# of {1..n^2} into n blocks of n (row contents, column contents) that are
# orthogonal (every R-block meets every C-block in exactly one element) and
# share their multiset of block products.  Row and column permutations and
# transposition act so that classes correspond to unordered pairs {R, C};
# each unordered pair yields exactly 2*(n!)^2 distinct arrays forming one
# class.  Blocks are stored as bitmasks; partitions are grouped by their
# sorted product multiset (packed into one integer) so that only partitions
# with matching products are ever tested for orthogonality.
# ---------------------------------------------------------------------------
def census(n: int) -> tuple:
    n2, bs = n * n, n

    def partitions():
        def rec(rem, masks, prods):
            if not rem:
                key = 0
                for q in sorted(prods):
                    key = (key << 20) | q
                yield key, tuple(masks)
                return
            first, rest = rem[0], rem[1:]
            for combo in combinations(rest, bs - 1):
                s = set(combo)
                mask, q = 1 << first, first
                for x in combo:
                    mask |= 1 << x
                    q *= x
                yield from rec(
                    [x for x in rest if x not in s], masks + [mask], prods + [q]
                )

        yield from rec(list(range(1, n2 + 1)), [], [])

    key_counts = Counter(key for key, _ in partitions())
    groups: dict = {}
    for key, blocks in partitions():
        if key_counts[key] >= 2:
            groups.setdefault(key, []).append(blocks)

    pairs = 0
    for parts in groups.values():
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                if all(bin(r & c).count("1") == 1 for r in parts[i] for c in parts[j]):
                    pairs += 1
    return pairs, 2 * math.factorial(n) ** 2 * pairs


check("orthogonal-pair method reproduces the n = 3 census", census(3) == (6, 432))
p4, a4 = census(4)
check(
    "n = 4 census: 2780 classes, 3,202,560 arrays",
    (p4, a4) == (2780, 3202560),
    f"got {(p4, a4)}",
)

print(f"\n{len(FAILURES)} failure(s).")
sys.exit(1 if FAILURES else 0)
