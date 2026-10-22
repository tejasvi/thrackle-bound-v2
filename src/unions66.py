"""Unions of two DISTINCT 6-cycles C = v0..v5 and D = w0..w5 sharing at least one vertex (mode 'vertex': w0 = v0, each
of w1..w5 a new vertex or a distinct one of v1..v5) or at least one edge (mode 'edge': w0w1 = v0v1, each of w2..w5 new
or a distinct one of v2..v5), up to isomorphism. Classes:
  same      - D has the same edge set as C (not distinct; skipped),
  triangle  - contains C3,
  C4        - contains C4,
  DB(6,6,l) - C and D meet exactly in a path of -l edges (l = -1, -2, -3) or exactly in one vertex (l = 0)
              (Fulek-Pach 2011, Lemma 6 and LPS 1997 Thm 5.1),
  other     - needs its own thrackleability test.
Writes graphs/u66_<k>.txt for the 'other' and DB classes."""
import itertools, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import Counter
from unions import cycles_of_len, canon

mode = sys.argv[1] if len(sys.argv) > 1 else 'vertex'
C = [(i, (i + 1) % 6) for i in range(6)]
classes = {}
if mode == 'vertex':
    free = 5; choices = ['new', 1, 2, 3, 4, 5]; fixed = [0]
else:
    free = 4; choices = ['new', 2, 3, 4, 5]; fixed = [0, 1]
for assign in itertools.product(choices, repeat=free):
    vs = [a for a in assign if a != 'new']
    if len(vs) != len(set(vs)):
        continue
    w = list(fixed); nv = 6
    for a in assign:
        if a == 'new':
            w.append(nv); nv += 1
        else:
            w.append(a)
    D = [(w[i], w[(i + 1) % 6]) for i in range(6)]
    Ce = {frozenset(e) for e in C}; De = {frozenset(e) for e in D}
    if Ce == De:
        continue  # same cycle
    E = Ce | De
    edges = sorted(tuple(sorted(e)) for e in E)
    adj = [set() for _ in range(nv)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    shared_e = Ce & De
    shared_v = set(range(6)) & set(w)
    if cycles_of_len(adj, 3):
        cls = 'triangle'
    elif cycles_of_len(adj, 4):
        cls = 'C4'
    else:
        j = len(shared_e)
        if j >= 1 and len(shared_v) == j + 1 and nv == 12 - (j + 1):
            cls = f'DB(6,6,-{j})'
        elif j == 0 and len(shared_v) == 1:
            cls = 'DB(6,6,0)'
        else:
            cls = 'other'
    key = canon(nv, edges)
    classes.setdefault(key, (cls, nv, edges, assign))
cnt = Counter(v[0] for v in classes.values())
print(f'mode {mode}: isomorphism classes by type:', dict(sorted(cnt.items())))
k = 0
for key, (cls, nv, edges, assign) in sorted(classes.items(), key=lambda kv: (kv[1][0], kv[1][1], kv[1][2])):
    if cls == 'other' or cls.startswith('DB'):
        with open(f'graphs/u66{mode[0]}_{k}.txt', 'w') as f:
            f.write(f'{nv} {len(edges)}\n')
            for u, v in edges:
                f.write(f'{u} {v}\n')
        print(f'u66{mode[0]}_{k} [{cls}]: n={nv} m={len(edges)} assign={assign} edges={edges}')
        k += 1
