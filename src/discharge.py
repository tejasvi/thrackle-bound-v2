"""Xu-type discharging (Xu 2021, Scoppetto 2026): charges t(v) = d(v) - r, t(F) = (r-2)/2 d(F) - r, r = 2c; 6-faces only
touch 8+-faces, every 8+-face sends x through each half-edge, x = 1 - r/3 (6-face final charge 0). A d-face with at most
h_d half-edges needs (r-2)/2 d - r - h_d x >= 0, i.e. r >= 6(d + h_d)/(3d - 6 + 2 h_d). Bound c = max over d of r/2."""
from fractions import Fraction as Fr
def r_needed(d, h):
    return Fr(6 * (d + h), 3 * d - 6 + 2 * h)
def bound(h8, h10=10, h12=12, dmax=40):
    rs = [r_needed(8, h8), r_needed(10, h10), r_needed(12, h12)] + [r_needed(d, d) for d in range(14, dmax + 1, 2)]
    r = max(rs)
    return r / 2, [str(x / 2) for x in rs[:3]]
for h8 in range(6, -1, -1):
    c, parts = bound(h8)
    print(f"h8 <= {h8}: c = {c} = {float(c):.6f}   (8-face {parts[0]}, 10-face {parts[1]}, 12-face {parts[2]})")
print("with h8 <= 0 and h10 <= k:")
for h10 in range(10, -1, -2):
    c, parts = bound(0, h10)
    print(f"  h10 <= {h10}: c = {c} = {float(c):.6f}")
