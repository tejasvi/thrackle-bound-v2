"""Enumerate unions of an 8-cycle F = v0..v7 and a 6-cycle C = w0..w5 sharing the edge v0v1 = w0w1 (as abstract simple
graphs). Each of w2..w5 is a new vertex or one of v2..v7 (injective). Classify every union:
  triangle  - contains C3 (cannot occur in the triangle-free case),
  C4        - contains a 4-cycle (C4 is not thrackleable),
  2C6       - contains two distinct 6-cycles sharing a vertex (FP19: impossible in a thrackleable graph),
  DB(6,8,-j)- the union is the dumbbell itself (C and F meet exactly in a path of j edges),
  other     - needs its own thrackleability test.
Writes graphs/union_<k>.txt for the 'other' class (one representative per isomorphism class)."""
import itertools, sys


def cycles_of_len(adj, L):
    """set of frozenset-edge-sets of simple cycles of length L."""
    out = set(); n = len(adj)
    for s in range(n):
        stack = [(s, [s])]
        while stack:
            v, path = stack.pop()
            if len(path) == L:
                if s in adj[v]:
                    es = frozenset(frozenset((path[i], path[(i + 1) % L])) for i in range(L))
                    out.add(es)
                continue
            for w in adj[v]:
                if w > s and w not in path:
                    stack.append((w, path + [w]))
    return out


def canon(n, edges):
    """canonical form by brute force over refinements (small graphs): sorted adjacency under the lexicographically
    smallest relabelling among degree-respecting orders found by backtracking."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    best = None
    deg = [len(a) for a in adj]
    verts = sorted(range(n), key=lambda x: -deg[x])
    # backtracking: build order; at each step choose next vertex among those with max (degree, connections to placed)
    def rec(order, pos):
        nonlocal best
        if len(order) == n:
            code = tuple(sorted((min(pos[u], pos[v]), max(pos[u], pos[v])) for u, v in edges))
            if best is None or code < best:
                best = code
            return
        placed = set(order)
        cand = [x for x in range(n) if x not in placed]
        key = lambda x: (-sum(1 for y in adj[x] if y in placed), -deg[x])
        k0 = min(key(x) for x in cand)
        for x in cand:
            if key(x) == k0:
                pos[x] = len(order); order.append(x)
                rec(order, pos)
                order.pop(); del pos[x]
    rec([], {})
    return (n, best)


def main():
    F = [(i, (i + 1) % 8) for i in range(8)]
    classes = {}
    for assign in itertools.product(['new', 2, 3, 4, 5, 6, 7], repeat=4):
        vs = [a for a in assign if a != 'new']
        if len(vs) != len(set(vs)):
            continue
        w = [0, 1]; nv = 8
        for a in assign:
            if a == 'new':
                w.append(nv); nv += 1
            else:
                w.append(a)
        C = [(w[i], w[(i + 1) % 6]) for i in range(6)]
        E = {frozenset(e) for e in F} | {frozenset(e) for e in C}
        if any(len(e) < 2 for e in E):
            continue
        edges = sorted(tuple(sorted(e)) for e in E)
        adj = [set() for _ in range(nv)]
        for u, v in edges:
            adj[u].add(v); adj[v].add(u)
        shared_edges = {frozenset(e) for e in F} & {frozenset(e) for e in C}
        shared_vertices = set(range(8)) & set(w)
        if cycles_of_len(adj, 3):
            cls = 'triangle'
        elif cycles_of_len(adj, 4):
            cls = 'C4'
        else:
            c6 = cycles_of_len(adj, 6)
            two = False
            c6l = list(c6)
            for i in range(len(c6l)):
                for j in range(i + 1, len(c6l)):
                    vi = set().union(*c6l[i]); vj = set().union(*c6l[j])
                    if vi & vj:
                        two = True
            if two:
                cls = '2C6'
            else:
                # dumbbell test: C and F meet exactly in a path of j edges (shared vertices = j + 1, consecutive)
                j = len(shared_edges)
                if len(shared_vertices) == j + 1 and nv == 8 + 6 - (j + 1):
                    cls = f'DB(6,8,-{j})'
                else:
                    cls = 'other'
        key = canon(nv, edges)
        classes.setdefault(key, (cls, nv, edges, assign))
    from collections import Counter
    cnt = Counter(v[0] for v in classes.values())
    print('isomorphism classes by type:', dict(cnt))
    k = 0
    for key, (cls, nv, edges, assign) in sorted(classes.items(), key=lambda kv: kv[1][0]):
        if cls == 'other' or cls == '2C6' or cls.startswith('DB'):
            tag = {'other': 'union', '2C6': 'u2c6'}.get(cls, 'udb')
            with open(f'graphs/{tag}_{k}.txt', 'w') as f:
                f.write(f'{nv} {len(edges)}\n')
                for u, v in edges:
                    f.write(f'{u} {v}\n')
            print(f'{tag}_{k} [{cls}]: n={nv} m={len(edges)} assign={assign} edges={edges}')
            k += 1


if __name__ == '__main__':
    main()
