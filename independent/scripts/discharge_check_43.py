"""discharge_check_43.py: the discharging of Section 4 at c = 4/3 in exact arithmetic: the charges of the
2-connected lemma (r = 8/3, x = 1/9, final face charges), the triangle lemma (Case 2), the proof of Theorem 1.1
(Case 3), and the count that runs of at most two 6-edges on a 10-face give at most six 6-edges."""
from fractions import Fraction as Fr
import itertools
c = Fr(4, 3); r = 2 * c; x = 1 - r / 3
assert r == Fr(8, 3) and x == Fr(1, 9)
t = lambda d: (r - 2) / 2 * d - r
assert t(6) + 6 * x == 0                         # 6-face receives x across each of its six edges
assert t(8) == 0                                 # 8-face: no 6-edges (C3), final charge 0 >= 0
assert t(10) - 6 * x == 0 and t(10) - 7 * x < 0  # 10-face with h10 <= 6
for d in range(12, 4001, 2):
    assert t(d) - d * x == Fr(2 * d - 24, 9) and t(d) - d * x >= 0
# 2-connected lemma: total charge -kr, faces end >= 0 => 2m - rn <= -kr => m <= c(n - k): needs only final face charges >= 0
assert 6 <= 5 * c and c > 1                      # C6 itself; leaf and cut-vertex induction (trianglefree)
# triangle lemma (Case 2): g(bridge) = c - 1, g(C6) = 5c - 6, 2-connected non-C6 block g >= c
assert c - 1 == Fr(1, 3) and 5 * c - 6 == Fr(2, 3)
low = (5 * c - 6) + (c - 1) - c                  # a C6 block plus the cheapest further block, minus c
assert low == Fr(-1, 3)
for n in range(4, 4000):
    mmax = c * (n + 3 - 2) - low - 3             # M <= c(N - 2) - low, N = n + 3, M = m + 3
    assert mmax == c * (n - 1)                   # m <= 4/3 (n - 1): equality allowed, the theorem is non-strict
# main proof (Case 3): C3 component excess 3 - 2c, and t * excess <= c (j - 1) for t <= j, j >= 2
assert 3 - 2 * c == Fr(1, 3)
for j in range(2, 4000):
    assert Fr(1, 3) * j <= c * (j - 1)
# counting: maximal cyclic runs of 6-edges of length <= 2 on a 10-face (not all ten) => at most 6
best = 0
for bits in itertools.product((0, 1), repeat=10):
    if all(bits): continue
    k = bits.index(0); rot = bits[k:] + bits[:k]
    runs = [len(s) for s in ''.join(map(str, rot)).split('0') if s]
    if all(L <= 2 for L in runs): best = max(best, sum(bits))
assert best == 6
print('c = 4/3: r = 8/3, x = 1/9; faces 0/0/0/(2d-24)/9; Case 2 floor -1/3 gives m <= 4/3 (n-1); Case 3 ok; h10 <= 6')
print('ALL 4/3 DISCHARGING CHECKS PASS (exact)')
