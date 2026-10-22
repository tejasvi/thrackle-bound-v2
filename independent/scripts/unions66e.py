"""unions66e.py OUTDIR: edge-mode variant of unions66.py: unions of two distinct 6-cycles C and D sharing
at least one EDGE.  C = v0 ... v5; by the symmetry of C a shared edge is v0v1, and by relabelling D it is w0w1 = v0v1;
each of w2..w5 is a new vertex or one of v2..v5 (D has distinct vertices); D must differ from C as an edge set.
Classes up to isomorphism (networkx VF2 inside Weisfeiler-Lehman hash buckets).  Each class is tagged, in this
precedence: 'triangle', 'C4', 'DB(6,6,l)' for l = 0, -1, -2, -3 (isomorphic to the dumbbell: two 6-cycles sharing
exactly one vertex (l = 0) or exactly a path of -l edges), 'other'.  Writes OUTDIR/classes.json and, for every class that
is not excluded by a triangle or a C4, a graph file with C's edges first (in cycle order), then D's other edges, and the
two filter subgraphs (C, and D in the file labels)."""
import sys, os, json, itertools
import networkx as nx
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
C = [(i, (i + 1) % 6) for i in range(6)]
Cset = {frozenset(e) for e in C}


def cycles_of_length(G, k):
    """set of k-cycles of G as frozensets of edges (simple graph, small)"""
    res = set()
    for start in sorted(G.nodes()):
        stack = [(start, [start])]
        while stack:
            v, path = stack.pop()
            if len(path) == k:
                if G.has_edge(v, start):
                    res.add(frozenset(frozenset((path[i], path[(i + 1) % k])) for i in range(k)))
                continue
            for w in G.neighbors(v):
                if w > start and w not in path:
                    stack.append((w, path + [w]))
    return res


def db(c1, c2, l):
    """DB(c1, c2, l) for l <= 0: cycles sharing exactly a path of -l edges (l = 0: exactly one vertex)"""
    k = -l
    G = nx.Graph(); G.add_edges_from([(i, i + 1) for i in range(k)]); nv = k + 1
    for L in (c1, c2):
        if k == 0:
            vs = [0] + list(range(nv, nv + L - 1)) + [0]; nv += L - 1
        else:
            vs = [k] + list(range(nv, nv + L - k - 1)) + [0]; nv += L - k - 1
        G.add_edges_from([(vs[i], vs[i + 1]) for i in range(len(vs) - 1)])
    return G


DBS = {f'DB(6,6,{l})': db(6, 6, l) for l in (0, -1, -2, -3)}
for name, D in DBS.items():
    assert all(d == 2 or d == 3 or d == 4 for _, d in D.degree()), name
reps = []; buckets = {}; n_choices = 0
for choice in itertools.product(['new', 2, 3, 4, 5], repeat=4):
    vs = [c for c in choice if c != 'new']
    if len(vs) != len(set(vs)): continue
    nxt = 6; w = [0, 1]
    for c in choice:
        if c == 'new': w.append(nxt); nxt += 1
        else: w.append(c)
    D = [(w[i], w[(i + 1) % 6]) for i in range(6)]
    if {frozenset(e) for e in D} == Cset: continue
    n_choices += 1
    G = nx.Graph(); G.add_edges_from(C); G.add_edges_from(D)
    h = nx.weisfeiler_lehman_graph_hash(G, iterations=4)
    hit = None
    for idx in buckets.get(h, []):
        if nx.is_isomorphic(G, reps[idx][0]): hit = idx; break
    if hit is None:
        buckets.setdefault(h, []).append(len(reps)); reps.append((G, D, choice))
classes = []; cnt = {}
for i, (G, D, choice) in enumerate(reps):
    if cycles_of_length(G, 3): tag = 'triangle'
    elif cycles_of_length(G, 4): tag = 'C4'
    else:
        tag = 'other'
        for name, B in DBS.items():
            if nx.is_isomorphic(G, B): tag = name
    cnt[tag] = cnt.get(tag, 0) + 1
    rec = dict(idx=i, tag=tag, n=G.number_of_nodes(), m=G.number_of_edges(), choice=[str(c) for c in choice], D=D)
    if tag not in ('triangle', 'C4'):
        es = list(C); seen = set(Cset)
        for e in D:
            if frozenset(e) not in seen: es.append(e); seen.add(frozenset(e))
        nodes = sorted(G.nodes()); lab = {v: j for j, v in enumerate(nodes)}
        base = os.path.join(out, f'u66e_{i:03d}_{tag.replace("(", "").replace(")", "").replace(",", "_")}')
        def wr(fn, E):
            with open(fn, 'w') as f:
                f.write(f'{len(nodes)} {len(E)}\n' + ''.join(f'{lab[u]} {lab[v]}\n' for u, v in E))
        wr(base + '.txt', es); wr(base + '_C.txt', C); wr(base + '_D.txt', D)
        rec['file'] = os.path.basename(base) + '.txt'
    classes.append(rec)
json.dump(dict(choices=n_choices, classes=classes, counts=cnt), open(os.path.join(out, 'classes.json'), 'w'), indent=1)
print('choices', n_choices, 'classes', len(reps), cnt)
