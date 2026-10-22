"""Independent re-check of unions610.py (shares no code with it or with unions.py).
Brute force: every closed walk W = (w0..w9) with w_i = i (i <= s) along the 6-cycle C = 0..5 (for s = 6: 0..5, 0), the
other entries from {0..5} or new labels in order of first use; all constraints are tested on the finished walk:
consecutive entries distinct, no backtracking (cyclically), the run is maximal ({w_s, w_s+1} and {w9, w0} not edges of
C), every C-edge traversed at most once and every other edge at most twice, and U = C + edges(W) has girth >= 5.
U is classified by its own cycle search: 'hex' (two distinct 6-cycles with a common vertex), 'c6c8' (a 6-cycle and an
8-cycle with a common edge), else 'other'. Every 'other' union is matched by a backtracking isomorphism test against
graphs/u610_<s>_<k>.txt, and each of those is tested for containing DB(5,6,-2) = theta(2,3,4) as a subgraph."""
import sys, os, itertools
from collections import Counter

CE = {frozenset((i, (i + 1) % 6)) for i in range(6)}


def walks(s):
    start = list(range(s + 1)) if s < 6 else [0, 1, 2, 3, 4, 5, 0]   # w0..ws
    def gen(prefix, nxt):
        if len(prefix) == 10:
            yield tuple(prefix); return
        for b in list(range(nxt)) + [nxt]:
            yield from gen(prefix + [b], nxt + 1 if b == nxt else nxt)
    yield from gen(start, 6)


def valid(w, s):
    L = 10
    for i in range(L):
        if w[i] == w[(i + 1) % L]: return False
        if w[(i - 1) % L] == w[(i + 1) % L]: return False
    if frozenset((w[s], w[(s + 1) % L])) in CE: return False
    if frozenset((w[9], w[0])) in CE: return False
    for i in range(s):
        if frozenset((w[i], w[i + 1])) not in CE: return False
    t = Counter(frozenset((w[i], w[(i + 1) % L])) for i in range(L))
    for e, c in t.items():
        if c > (1 if e in CE else 2): return False
    return True


def union(w):
    E = set(CE) | {frozenset((w[i], w[(i + 1) % 10])) for i in range(10)}
    V = sorted(set().union(*E))
    return V, E


def girth_ok(V, E):
    adj = {v: set() for v in V}
    for e in E:
        a, b = tuple(e); adj[a].add(b); adj[b].add(a)
    for e in E:
        a, b = tuple(e)
        dist = {a: 0}; fr = [a]
        while fr:
            nf = []
            for x in fr:
                for y in adj[x]:
                    if {x, y} == {a, b} or y in dist: continue
                    dist[y] = dist[x] + 1; nf.append(y)
            fr = nf
        if b in dist and dist[b] + 1 <= 4: return False
    return True


def cycles(V, E, L):
    """simple cycles of length L as frozensets of edges (DFS from the smallest vertex)"""
    adj = {v: set() for v in V}
    for e in E:
        a, b = tuple(e); adj[a].add(b); adj[b].add(a)
    out = set()
    def dfs(path, start):
        x = path[-1]
        if len(path) == L:
            if start in adj[x]:
                out.add(frozenset(frozenset((path[i], path[(i + 1) % L])) for i in range(L)))
            return
        for y in adj[x]:
            if y > start and y not in path: dfs(path + [y], start)
    for v in V: dfs([v], v)
    return out


def classify(V, E):
    c6 = list(cycles(V, E, 6))
    for i in range(len(c6)):
        vi = set().union(*c6[i])
        for j in range(i + 1, len(c6)):
            if vi & set().union(*c6[j]): return 'hex'
    c8 = cycles(V, E, 8)
    for x in c6:
        for y in c8:
            if x & y: return 'c6c8'
    return 'other'


def adjmap(V, E):
    adj = {v: set() for v in V}
    for e in E:
        a, b = tuple(e); adj[a].add(b); adj[b].add(a)
    return adj


def embed(VA, EA, VB, EB, induced_count=False):
    """injective map of graph A into graph B preserving edges (subgraph, not necessarily induced); returns a map or None"""
    A, B = adjmap(VA, EA), adjmap(VB, EB)
    order = sorted(VA, key=lambda v: -len(A[v]))
    # order by BFS for connectivity of partial maps
    seen = []; rest = list(order)
    while rest:
        r = rest.pop(0); q = [r]; seen.append(r)
        while q:
            x = q.pop(0)
            for y in sorted(A[x], key=lambda v: -len(A[v])):
                if y not in seen: seen.append(y); q.append(y); rest.remove(y)
    order = seen
    mp = {}
    used = set()
    def bt(i):
        if i == len(order): return True
        v = order[i]
        for u in VB:
            if u in used or len(B[u]) < len(A[v]): continue
            if all((mp[x] in B[u]) for x in A[v] if x in mp):
                mp[v] = u; used.add(u)
                if bt(i + 1): return True
                del mp[v]; used.discard(u)
        return False
    return dict(mp) if bt(0) else None


def isomorphic(VA, EA, VB, EB):
    if len(VA) != len(VB) or len(EA) != len(EB): return False
    return embed(VA, EA, VB, EB) is not None


def read_graph(path):
    t = open(path).read().split()
    n, m = int(t[0]), int(t[1])
    E = {frozenset((int(t[2 + 2 * i]), int(t[3 + 2 * i]))) for i in range(m)}
    return list(range(n)), E


def theta(a, b, c):
    """theta graph: poles 0 and 1 joined by internally disjoint paths of lengths a, b, c"""
    E = set(); nv = 2
    for L in (a, b, c):
        prev = 0
        for j in range(L - 1):
            E.add(frozenset((prev, nv))); prev = nv; nv += 1
        E.add(frozenset((prev, 1)))
    return list(range(nv)), E


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    th = theta(2, 3, 4)
    for s in [int(x) for x in sys.argv[1:]] or [6, 5, 4, 3]:
        nw = 0; cls = Counter(); others = []
        for w in walks(s):
            if not valid(w, s): continue
            V, E = union(w)
            if not girth_ok(V, E): continue
            nw += 1
            c = classify(V, E); cls[c] += 1
            if c == 'other': others.append((w, V, E))
        reps = []
        k = 0
        while os.path.exists(os.path.join(here, f'graphs/u610_{s}_{k}.txt')):
            reps.append(read_graph(os.path.join(here, f'graphs/u610_{s}_{k}.txt'))); k += 1
        match = Counter(); unmatched = 0
        for w, V, E in others:
            hit = [i for i, (VR, ER) in enumerate(reps) if isomorphic(V, E, VR, ER)]
            if len(hit) != 1: unmatched += 1
            else: match[hit[0]] += 1
        print(f's={s}: valid walks {nw}; walks by class {dict(sorted(cls.items()))}; other walks matched to reps '
              f'{dict(sorted(match.items()))}, unmatched {unmatched}; reps {len(reps)}')
        for i, (VR, ER) in enumerate(reps):
            emb = embed(th[0], th[1], VR, ER)
            print(f'  u610_{s}_{i}: n={len(VR)} m={len(ER)} class={classify(VR, ER)} contains theta(2,3,4)='
                  f'{"yes" if emb else "no"}' + (f' via poles {emb[0]},{emb[1]}' if emb else ''))


if __name__ == '__main__':
    main()
