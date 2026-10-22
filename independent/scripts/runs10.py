"""runs10.py OUTDIR: enumeration of the closed 10-walks of the run lemma (Lemma 4.3 of the paper), written from the
text of the lemma only, without reading the code of the first enumeration.

Model.  Q = 0 1 2 3 4 5 (a 6-cycle, the boundary of the 6-face).  A run of s 6-edges is w_i = i for 0 <= i <= s
(for s = 6: w_0..w_6 = 0 1 2 3 4 5 0).  The other entries w_{s+1}..w_9 of the closed walk W = w_0..w_9 (edge w_9 w_0
closes it) are vertices of Q, earlier non-Q vertices of W, or new vertices.  Conditions:
  (a) consecutive entries distinct (G is simple), cyclically;
  (b) no backtracking: w_{i-1} != w_{i+1} for every i, indices mod 10 (G has minimum degree 2);
  (c) maximality: {w_s, w_{s+1}} and {w_9, w_0} are not edges of Q;
  (d) every edge of Q is traversed at most once, every other edge at most twice;
  (e) U = Q + edges(W) has no 3-cycle and no 4-cycle.
Method A: new vertices are numbered 6, 7, ... in order of first use (restricted growth), all conditions are applied to
the finished walk.  Method B: every entry ranges over a fixed alphabet 0 .. 5 + (9 - s) with no growth rule; the walks
that pass are relabelled canonically (non-Q labels renumbered in order of first appearance) and deduplicated.
Both sets must be equal.  For each walk the union U is classified: two distinct 6-cycles with a common vertex (excluded
by the vertex version of the 6-6 lemma), a 6-cycle and an 8-cycle with a common edge (excluded by the 6-8 corollary).
Writes OUTDIR/runs10.json and prints the counts."""
import sys, os, json, itertools
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
EQ = {frozenset((i, (i + 1) % 6)) for i in range(6)}


def run_prefix(s):
    return list(range(s + 1)) if s < 6 else [0, 1, 2, 3, 4, 5, 0]


def ok_walk(W, s):
    n = len(W)
    assert n == 10
    for i in range(n):
        if W[i] == W[(i + 1) % n]: return False                          # (a)
        if W[(i - 1) % n] == W[(i + 1) % n]: return False                # (b)
    if frozenset((W[s], W[(s + 1) % n])) in EQ: return False             # (c)
    if frozenset((W[9], W[0])) in EQ: return False
    cnt = {}
    for i in range(n):
        e = frozenset((W[i], W[(i + 1) % n])); cnt[e] = cnt.get(e, 0) + 1
    for e, c in cnt.items():                                             # (d)
        if c > (1 if e in EQ else 2): return False
    E = set(EQ) | set(cnt)
    adj = {}
    for e in E:
        a, b = tuple(e); adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    for a in adj:                                                        # (e) triangles
        for b in adj[a]:
            if adj[a] & adj[b]: return False
    for a in adj:                                                        # (e) 4-cycles: two common neighbours
        for b in adj:
            if a < b and b not in adj[a] and len(adj[a] & adj[b]) >= 2: return False
    return True


def method_a(s):
    pre = run_prefix(s); nfree = 10 - len(pre); res = []
    def rec(W, nxt):
        if len(W) == 10:
            if ok_walk(W, s): res.append(tuple(W))
            return
        for v in list(range(6)) + list(range(6, nxt + 1)):
            rec(W + [v], nxt + 1 if v == nxt else nxt)
    rec(pre, 6)
    return sorted(set(res)), nfree


def canon(W):
    m = {}; out_ = []
    for v in W:
        if v < 6: out_.append(v)
        else:
            if v not in m: m[v] = 6 + len(m)
            out_.append(m[v])
    return tuple(out_)


def method_b(s):
    pre = run_prefix(s); nfree = 10 - len(pre); alpha = list(range(6 + nfree)); res = set()
    for tail in itertools.product(alpha, repeat=nfree):
        W = pre + list(tail)
        if ok_walk(W, s): res.add(canon(W))
    return sorted(res)


def cycles_of_length(adj, k):
    res = set()
    for start in sorted(adj):
        stack = [(start, [start])]
        while stack:
            v, path = stack.pop()
            if len(path) == k:
                if start in adj[v]:
                    res.add(frozenset(frozenset((path[i], path[(i + 1) % k])) for i in range(k)))
                continue
            for w in adj[v]:
                if w > start and w not in path: stack.append((w, path + [w]))
    return res


def classify(W):
    E = set(EQ) | {frozenset((W[i], W[(i + 1) % 10])) for i in range(10)}
    adj = {}
    for e in E:
        a, b = tuple(e); adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    c6 = list(cycles_of_length(adj, 6)); c8 = list(cycles_of_length(adj, 8))
    v6 = [set(v for e in c for v in e) for c in c6]
    two6 = any(v6[i] & v6[j] for i in range(len(c6)) for j in range(i + 1, len(c6)))
    c68 = any(a & b for a in c6 for b in c8)
    return dict(n=len(adj), m=len(E), n_c6=len(c6), n_c8=len(c8), two_c6_common_vertex=two6, c6_c8_common_edge=c68)


report = {}
for s in (6, 5, 4, 3):
    A, nfree = method_a(s); B = method_b(s)
    cls = [dict(walk=list(W), **classify(W)) for W in A]
    report[s] = dict(free=nfree, method_a=len(A), method_b=len(B), equal=(A == B), walks=cls,
                     excluded_two_c6=sum(1 for c in cls if c['two_c6_common_vertex']),
                     excluded_c6c8=sum(1 for c in cls if c['c6_c8_common_edge']),
                     excluded_either=sum(1 for c in cls if c['two_c6_common_vertex'] or c['c6_c8_common_edge']))
    r = report[s]
    print(f"s={s}: free entries {nfree}; walks A={r['method_a']} B={r['method_b']} equal={r['equal']}; "
          f"two C6 with a common vertex {r['excluded_two_c6']}, C6-C8 common edge {r['excluded_c6c8']}, either {r['excluded_either']}",
          flush=True)
json.dump(report, open(os.path.join(out, 'runs10.json'), 'w'), indent=1)
