# Balanced squares, impossible rectangles, and Bertrand's Postulate — supplementary material

Verification code accompanying the paper *Balanced squares, impossible
rectangles, and Bertrand's Postulate* by Jayanta Manoharmayum and Vamshi
Jandhyala.

The paper proves a sharp elementary strengthening of Bertrand's Postulate
(for every real x ≥ 97 the interval (x/2, x] contains more than √x primes,
the only exceptions being equality at x = 100 and failure on (100, 101)),
and uses it to classify the shapes m × n for which 1, …, mn can be arranged
in an m × n array whose sets of row and column products agree: only squares
of order 1, 3–8, and 10.

## Contents

`verify.py` re-derives every finite computation in the paper from scratch:

| Paper item | Check |
| --- | --- |
| Theorem A | swept for all real 97 ≤ x < 1.6 × 10⁶; equality only at x = 100, failure exactly on (100, 101) |
| Remark 2.4 | the inequality fails exactly on [94, 97) below the threshold |
| Lemma 2.3 | the finite check for 51 ≤ n ≤ 1057, minimum margin at n = 53, endpoint values |
| Remark 2.6 | the crossovers for the routes through Ramanujan's bound (n = 2366) and Erdős's bound (t ≥ 1232.02) |
| Remark 2.7 | R₁ … R₂₀ from Sondow's definition; 4m ln 4m ≤ (m−1)² at m = 21 |
| Figure 1 | the step-function data for π(x) − π(x/2) on [50, 150] |
| Figures 2–4 | the balanced arrays for n = 4, …, 8, 10: entries, balance, matched diagonal, lonely primes |
| Section 3.5 | the censuses: n = 3 (432 arrays, six classes of 72) and n = 4 (2780 classes, 3,202,560 arrays) |

The n = 4 census uses the orthogonal-partition-pair correspondence described
in the paper and is validated against an independent brute-force enumeration
of all 9! arrangements for n = 3.

`verify_rectangles.py` verifies the computational inputs of the rectangular
theorem (no set-balanced m × n array exists for m < n):

| Paper item | Check |
| --- | --- |
| Finite check | every pair 2 ≤ m < n with mn ≤ 99 has ℓ(m,n) ≥ m − 1, and the 22-case table of ℓ values |
| Area boundary | π(100) − π(50) = 10, and every m < n with 100 ≤ mn ≤ 200 has ℓ > m |
| Corroboration | exhaustive enumeration confirms no set-balanced array for 2×3, 2×4, 2×5, 2×6, 3×4, 3×5 |
| Scalar reduction | (ℓ+2)(ℓ+3) > N for every 2 ≤ N ≤ 96; the certificate table of N_max per ℓ; minimum margin 2 attained exactly at N = 10, 28, 40 |

## Running

```
python3 verify.py
python3 verify_rectangles.py
```

Python 3.8 or later, standard library only. Runtime is a few minutes,
dominated by the Theorem A sweep and the n = 4 census. Every check prints
`PASS` or `FAIL`, and the script exits with a non-zero status if any check
fails.
