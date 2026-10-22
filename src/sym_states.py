"""sym_states.py GRAPH STATES SIGMA OUT: keep the states whose restriction to the edges fixed setwise by the graph
automorphism sigma (vertex map) is lexicographically <= its sigma image. sigma maps the restriction's edge set to itself.
Correct: sigma maps complete planar systems to complete planar systems, so every orbit has a member with canonical
restriction (if the restriction is sigma-invariant, both are kept)."""
import sys
L = open(sys.argv[1]).read().split(); n, m = int(L[0]), int(L[1])
E = [(int(L[2 + 2 * i]), int(L[3 + 2 * i])) for i in range(m)]
sig = [int(x) for x in sys.argv[3].split(',')]
emap = {}; flip = {}
idx = {frozenset(e): i for i, e in enumerate(E)}
for i, (u, v) in enumerate(E):
    j = idx[frozenset((sig[u], sig[v]))]
    emap[i] = j; flip[i] = (E[j] != (sig[u], sig[v]))
lines = open(sys.argv[2]).read().splitlines()
h = int(lines[0].split()[1]); hdr = lines[:1 + h]; st = lines[1 + h:]
# restriction edge set: edges e < h with emap[e] < h and closed under emap
R = [e for e in range(h) if all(emap[x] < h for x in [e])]
R = [e for e in R if emap[e] in R]
print('restriction edges', R, 'images', [emap[e] for e in R], 'flips', [int(flip[e]) for e in R])
def parse(s):
    return [[int(x) for x in part.split()] for part in s.split('|')]
def restr(rows):
    Rs = set(R)
    return tuple(tuple(x for x in rows[e] if x in Rs) for e in R)
def image(rows):
    Rs = set(R); out = {}
    for e in R:
        rr = [emap[x] for x in rows[e] if x in Rs]
        if flip[e]: rr = rr[::-1]
        out[emap[e]] = tuple(rr)
    return tuple(out[e] for e in R)
keep = []; cores = {}
for s in st:
    rows = parse(s)
    r = restr(rows); im = image(rows)
    cores.setdefault(r, im)
    if r <= im: keep.append(s)
print('distinct restrictions', len(cores), 'canonical', sum(1 for r, im in cores.items() if r <= im), 'invariant', sum(1 for r, im in cores.items() if r == im))
print('states kept', len(keep), 'of', len(st))
open(sys.argv[4], 'w').write('\n'.join(hdr + keep) + '\n')
