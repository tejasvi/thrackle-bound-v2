"""discharge_check.py: exact check (Fractions) of every number in the proof section of the paper (Lemmas 4.4-4.6
and the proof of Theorem 1.1) for its three variants c = 15/11, 27/20,
51/38, and of the counting steps of lem:ten (runs <= 6 => h10 <= 8) and lem:runs (runs <= 3 => h10 <= 7)."""
from fractions import Fraction as Fr
import itertools


def max_ones(run_cap):
    """largest number of 6-edges on a 10-face whose maximal cyclic runs have length <= run_cap (not all ten)"""
    best = 0
    for bits in itertools.product((0, 1), repeat=10):
        if all(bits): continue
        k = bits.index(0); rot = bits[k:] + bits[:k]
        runs = [len(t) for t in ''.join(map(str, rot)).split('0') if t]
        if all(L <= run_cap for L in runs): best = max(best, sum(bits))
    return best


H10 = {6: max_ones(6), 3: max_ones(3)}
assert H10 == {6: 8, 3: 7}, H10
variants = {
    # c: (face charge numerator/denominator as in the text, x, h10 bound used, text values)
    Fr(15, 11): dict(face=lambda d: Fr(4 * d - 30, 11), x=Fr(1, 11), h10=None, bridge=Fr(4, 11), c6=Fr(9, 11),
                     low=Fr(-2, 11), mform=lambda n: Fr(15 * n - 16, 11), c3=Fr(3, 11), case3=lambda j: 3 * j <= 15 * (j - 1)),
    Fr(27, 20): dict(face=lambda d: Fr(7 * d - 54, 20), x=Fr(1, 10), h10=8, bridge=Fr(7, 20), c6=Fr(3, 4),
                     low=Fr(-1, 4), mform=lambda n: Fr(27 * n - 28, 20), c3=Fr(3, 10), case3=lambda j: 6 * j <= 27 * (j - 1)),
    Fr(51, 38): dict(face=lambda d: Fr(13 * d - 102, 38), x=Fr(2, 19), h10=7, bridge=Fr(13, 38), c6=Fr(27, 38),
                     low=Fr(-11, 38), mform=lambda n: Fr(51 * n - 52, 38), c3=Fr(6, 19), case3=lambda j: 12 * j <= 51 * (j - 1)),
}
for c, V in variants.items():
    r = 2 * c
    t = lambda d: (r - 2) / 2 * d - r
    for d in range(6, 400, 2):
        assert t(d) == V['face'](d), (c, d)                       # the face charge as printed
    assert V['x'] == 1 - r / 3
    assert t(6) + 6 * V['x'] == 0                                  # 6-face ends at 0
    assert t(8) > 0                                                # 8-face sends nothing (no 6-edges)
    if V['h10'] is None:                                           # 15/11: faces of size >= 10 send at most d x
        for d in range(10, 400, 2): assert t(d) - d * V['x'] >= 0
    else:
        assert t(10) - V['h10'] * V['x'] == 0                      # 10-face, exactly 0 at the bound
        for d in range(12, 400, 2): assert t(d) - d * V['x'] > 0   # d >= 12, all traversals 6-edges
    # Euler: total charge = 2m - rn + (r - 2)m - rf = -r(n - m + f) = -kr
    assert 6 <= 5 * c and c > 1                                    # C6 and the leaf/cut-vertex induction
    assert c - 1 == V['bridge'] and 5 * c - 6 == V['c6']               # g(bridge), g(C6) as printed
    assert V['c6'] + V['bridge'] - c == V['low']                   # C6 block + cheapest further block - c
    assert min(V['bridge'], V['c6'], c) == V['bridge']
    for n in range(4, 2000):
        mmax = c * (n + 3 - 2) + (-V['low']) - 3                   # M <= c(N - 2) - low, N = n + 3, M = m + 3
        assert mmax == V['mform'](n) and mmax < c * (n - 1)
    assert 3 - 2 * c == V['c3']
    for j in range(2, 2000):
        assert V['case3'](j) and V['c3'] * j <= c * (j - 1)
    print(f'c = {c}: all printed values check (x = {V["x"]}, low = {V["low"]})')
print('h10 bounds from the run caps:', H10)
print('ALL DISCHARGING VALUES PASS (exact)')
