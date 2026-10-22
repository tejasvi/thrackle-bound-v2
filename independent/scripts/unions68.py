"""unions68.py OUTDIR: enumeration of the unions of an 8-cycle F and a 6-cycle C sharing at least one edge.
F = v0 v1 ... v7; by the symmetry of F a shared edge is v0 v1, and by relabelling C it is w0 w1 with w0 = v0, w1 = v1;
each of w2..w5 is a new vertex or one of v2..v7 (C has distinct vertices).  Classes up to isomorphism (networkx VF2
inside Weisfeiler-Lehman hash buckets).  Each class is tagged, in this precedence: 'triangle' (contains a 3-cycle),
'C4' (contains a 4-cycle), 'DB(6,8,-k)' for k = 1, 2, 3 (isomorphic to the dumbbell), 'two-C6' (two distinct 6-cycles
sharing a vertex), 'other'.  Writes OUTDIR/classes.json and a graph file per class that is not excluded by a triangle,
a C4 or by being one of the three dumbbells (for the search), with C's and F's edges listed first."""
import sys, os, json, itertools
import networkx as nx
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
F = [(i, (i + 1) % 8) for i in range(8)]
reps = []          # (graph, cycles C edges, F edges, choice)
buckets = {}
def cycles_of_length(G, k):
    """set of k-cycles of G as frozensets of edges (simple graph, small)"""
    res = set()
    nodes = sorted(G.nodes())
    for start in nodes:
        stack = [(start, [start])]
        while stack:
            v, path = stack.pop()
            if len(path) == k:
                if G.has_edge(v, start):
                    cyc = path
                    es = frozenset(frozenset((cyc[i], cyc[(i + 1) % k])) for i in range(k))
                    res.add(es)
                continue
            for w in G.neighbors(v):
                if w > start and w not in path:
                    stack.append((w, path + [w]))
    return res
n_choices = 0
for choice in itertools.product(['new', 2, 3, 4, 5, 6, 7], repeat=4):
    vs = [c for c in choice if c != 'new']
    if len(vs) != len(set(vs)): continue
    n_choices += 1
    nxt = 8; w = [0, 1]
    for c in choice:
        if c == 'new': w.append(nxt); nxt += 1
        else: w.append(c)
    C = [(w[i], w[(i + 1) % 6]) for i in range(6)]
    G = nx.Graph(); G.add_edges_from(F); G.add_edges_from(C)
    h = nx.weisfeiler_lehman_graph_hash(G, iterations=4)
    hit = None
    for idx in buckets.get(h, []):
        if nx.is_isomorphic(G, reps[idx][0]): hit = idx; break
    if hit is None:
        buckets.setdefault(h, []).append(len(reps)); reps.append((G, C, F, choice))
def db(c1, c2, k):
    G = nx.Graph(); G.add_edges_from([(i, i + 1) for i in range(k)]); nv = k + 1
    for L in (c1 - k, c2 - k):
        vs = [k] + list(range(nv, nv + L - 1)) + [0]; nv += L - 1
        G.add_edges_from([(vs[i], vs[i + 1]) for i in range(L)])
    return G
DBS = {f'DB(6,8,-{k})': db(6, 8, k) for k in (1, 2, 3)}
classes = []; cnt = {}
for i, (G, C, Fe, choice) in enumerate(reps):
    if cycles_of_length(G, 3): tag = 'triangle'
    elif cycles_of_length(G, 4): tag = 'C4'
    else:
        tag = None
        for name, D in DBS.items():
            if nx.is_isomorphic(G, D): tag = name
        if tag is None:
            c6 = list(cycles_of_length(G, 6))
            two = any(set().union(*a) & set().union(*b) for a, b in itertools.combinations([[set(e) for e in c] for c in c6], 2)
                      if True) if False else False
            verts = [set(v for e in c for v in e) for c in c6]
            two = any(verts[a] & verts[b] for a in range(len(c6)) for b in range(a + 1, len(c6)))
            tag = 'two-C6' if two else 'other'
    cnt[tag] = cnt.get(tag, 0) + 1
    rec = dict(idx=i, tag=tag, n=G.number_of_nodes(), m=G.number_of_edges(), choice=[str(c) for c in choice], C=C)
    if tag in ('two-C6', 'other') or tag.startswith('DB'):
        # graph file: C's edges in cycle order, then F's edges not in C (each oriented along its cycle)
        es = list(C); seen = set(frozenset(e) for e in C)
        for e in Fe:
            if frozenset(e) not in seen: es.append(e); seen.add(frozenset(e))
        nodes = sorted(G.nodes()); lab = {v: j for j, v in enumerate(nodes)}
        fn = os.path.join(out, f'class{i:03d}_{tag.replace("(", "").replace(")", "").replace(",", "_")}.txt')
        with open(fn, 'w') as f:
            f.write(f'{len(nodes)} {len(es)}\n')
            for u, v in es: f.write(f'{lab[u]} {lab[v]}\n')
        rec['file'] = os.path.basename(fn)
    classes.append(rec)
json.dump(dict(choices=n_choices, classes=classes, counts=cnt), open(os.path.join(out, 'classes.json'), 'w'), indent=1)
print('choices', n_choices, 'classes', len(reps), cnt)
