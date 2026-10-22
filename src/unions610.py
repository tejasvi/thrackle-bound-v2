"""Overlaps of a 6-cycle C = 0..5 with a closed walk W of length 10 (a facial walk of a 10-face) along a run of s
consecutive edges: W = (w0, ..., w9), w_i = i for i = 0..s (s = 3, 4, 5), the run is maximal (the edges (w_s, w_{s+1})
and (w9, w0) are not edges of C), consecutive walk vertices are distinct, the walk never backtracks (no spike: G has minimum degree 2), traverses each edge of C at most once (its other side
is C) and every other edge at most twice, and the union U = C u edges(W) has girth
>= 5 (no triangle, no C4). Each w_{s+1..9} is a new vertex or an existing one. Classes of U up to isomorphism:
  hex      - two distinct 6-cycles with a common vertex (excluded: L3v),
  c6c8     - a 6-cycle and an 8-cycle sharing an edge (excluded: overlap lemma C3),
  other    - needs a thrackleability test.
Writes graphs/u610_<s>_<k>.txt for the 'other' classes."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import Counter
from unions import cycles_of_len, canon

def bfs_dist(adj, a, maxd):
    d = {a: 0}; fr = [a]
    for k in range(maxd):
        nf = []
        for x in fr:
            for y in adj.get(x, ()):
                if y not in d:
                    d[y] = k + 1; nf.append(y)
        fr = nf
    return d

def run(s):
    C = [(i, (i + 1) % 6) for i in range(6)]
    Cset = {frozenset(e) for e in C}
    classes = {}
    count = [0]
    def rec(walk, adj, nv):
        i = len(walk) - 1
        if i == 9:
            a, b = walk[9], walk[0]
            if a == b or frozenset((a, b)) in Cset:
                return
            if walk[8] == b or walk[1] == a:
                return  # no spike (facial walks of a graph with minimum degree 2 never backtrack)
            if b not in adj.get(a, ()):
                d = bfs_dist(adj, a, 3)
                if b in d:
                    return
            adj2 = {k: set(v) for k, v in adj.items()}
            adj2.setdefault(a, set()).add(b); adj2.setdefault(b, set()).add(a)
            finish(walk, adj2, nv)
            return
        a = walk[i]
        cands = list(range(nv)) + [nv]
        for b in cands:
            if b == a or (i >= 1 and b == walk[i - 1]):
                continue
            if i == s and frozenset((a, b)) in Cset:
                continue  # run maximal
            new_edge = b not in adj.get(a, ())
            if new_edge and b < nv:
                d = bfs_dist(adj, a, 3)
                if b in d:
                    continue
            adj2 = {k: set(v) for k, v in adj.items()}
            adj2.setdefault(a, set()).add(b); adj2.setdefault(b, set()).add(a)
            rec(walk + [b], adj2, nv + 1 if b == nv else nv)

    def finish(walk, adj, nv):
        trav = Counter(frozenset((walk[j], walk[(j + 1) % 10])) for j in range(10))
        for e, c in trav.items():
            if c > (1 if e in Cset else 2):
                return
        count[0] += 1
        A = [set() for _ in range(nv)]
        for x, ys in adj.items():
            for y in ys:
                A[x].add(y)
        edges = sorted({(min(x, y), max(x, y)) for x in range(nv) for y in A[x]})
        if cycles_of_len(A, 3) or cycles_of_len(A, 4):
            return
        c6 = list(cycles_of_len(A, 6))
        cls = None
        for p in range(len(c6)):
            vp = set().union(*c6[p])
            for q in range(p + 1, len(c6)):
                if vp & set().union(*c6[q]):
                    cls = 'hex'; break
            if cls: break
        if not cls:
            c8 = list(cycles_of_len(A, 8))
            for x in c6:
                for y in c8:
                    if x & y:
                        cls = 'c6c8'; break
                if cls: break
        if not cls:
            cls = 'other'
        key = canon(nv, edges)
        classes.setdefault(key, (cls, nv, edges, tuple(walk)))

    adj = {}
    for (x, y) in C:
        adj.setdefault(x, set()).add(y); adj.setdefault(y, set()).add(x)
    walk = list(range(s + 1)) if s < 6 else list(range(6)) + [0]
    rec(walk, adj, 6)
    cnt = Counter(v[0] for v in classes.values())
    print(f's={s}: walks {count[0]}, union classes by type: {dict(sorted(cnt.items()))}')
    k = 0
    for key, (cls, nv, edges, walk) in sorted(classes.items(), key=lambda kv: (kv[1][0], kv[1][1], kv[1][2])):
        if cls == 'other':
            with open(f'graphs/u610_{s}_{k}.txt', 'w') as f:
                f.write(f'{nv} {len(edges)}\n')
                for u, v in edges:
                    f.write(f'{u} {v}\n')
            print(f'  u610_{s}_{k}: n={nv} m={len(edges)} walk={walk}')
            k += 1

if __name__ == '__main__':
    for s in [int(x) for x in sys.argv[1:]] or [5, 4, 3]:
        run(s)
