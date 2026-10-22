"""Reference planarity test (Demoucron-Malgrange-Pertuiset path embedding on each biconnected block).
Slow and simple; used only to validate the C Left-Right test (lr.c). is_planar(n, edges) -> bool."""
import sys
sys.setrecursionlimit(100000)


def blocks(n, adj):
    """biconnected components as lists of edges (u, v), iterative Hopcroft-Tarjan."""
    disc = [-1] * n; low = [0] * n; t = 0; out = []; estack = []
    for r in range(n):
        if disc[r] >= 0:
            continue
        disc[r] = low[r] = t; t += 1
        stack = [(r, -1, iter(sorted(adj[r])))]
        while stack:
            v, p, it = stack[-1]
            advanced = False
            for w in it:
                if w == p:
                    continue
                if disc[w] < 0:
                    estack.append((v, w))
                    disc[w] = low[w] = t; t += 1
                    stack.append((w, v, iter(sorted(adj[w]))))
                    advanced = True
                    break
                elif disc[w] < disc[v]:
                    estack.append((v, w))
                    low[v] = min(low[v], disc[w])
            if advanced:
                continue
            stack.pop()
            if stack:
                u = stack[-1][0]
                low[u] = min(low[u], low[v])
                if low[v] >= disc[u]:
                    comp = []
                    while True:
                        e = estack.pop(); comp.append(e)
                        if e == (u, v):
                            break
                    out.append(comp)
    return out


def dmp_block(edges):
    adj = {}
    for u, v in edges:
        adj.setdefault(u, set()).add(v); adj.setdefault(v, set()).add(u)
    V = list(adj); E = {frozenset(e) for e in edges}
    if len(E) < 9:
        return True
    if len(V) >= 3 and len(E) > 3 * len(V) - 6:
        return False
    # initial cycle by DFS
    start = V[0]; parent = {start: None}; order = [start]; cyc = None
    stack = [(start, iter(sorted(adj[start])))]
    while stack and cyc is None:
        v, it = stack[-1]
        for w in it:
            if w == parent[v]:
                continue
            if w in parent:
                path = [v]; x = v
                while x != w:
                    x = parent[x]; path.append(x)
                cyc = path
                break
            parent[w] = v; stack.append((w, iter(sorted(adj[w]))))
            break
        else:
            stack.pop()
    HV = set(cyc); HE = {frozenset((cyc[i], cyc[(i + 1) % len(cyc)])) for i in range(len(cyc))}
    faces = [list(cyc), list(cyc)]
    while len(HE) < len(E):
        frags = []
        for e in E:
            if e not in HE:
                u, v = tuple(e)
                if u in HV and v in HV:
                    frags.append(({u, v}, ('chord', u, v)))
        seen = set()
        for s in V:
            if s in HV or s in seen:
                continue
            comp = {s}; q = [s]; att = set()
            while q:
                x = q.pop()
                for y in adj[x]:
                    if y in HV:
                        att.add(y)
                    elif y not in comp:
                        comp.add(y); q.append(y)
            seen |= comp
            frags.append((att, ('comp', comp)))
        best = None
        for att, data in frags:
            adm = [i for i, F in enumerate(faces) if att <= set(F)]
            if not adm:
                return False
            if best is None or len(adm) < len(best[2]):
                best = (att, data, adm)
            if len(adm) == 1:
                break
        att, data, adm = best
        if data[0] == 'chord':
            path = [data[1], data[2]]
        else:
            comp = data[1]
            a = next(iter(att))
            # BFS from a through comp to another attachment
            prev = {a: None}; q = [a]; endv = None
            while q and endv is None:
                x = q.pop(0)
                for y in sorted(adj[x]):
                    if y in prev:
                        continue
                    if x != a and y in HV and y != a:
                        prev[y] = x; endv = y; break
                    if y in comp:
                        prev[y] = x; q.append(y)
            path = [endv]; x = endv
            while x != a:
                x = prev[x]; path.append(x)
            path.reverse()
        a, b = path[0], path[-1]
        F = faces[adm[0]]
        i, j = F.index(a), F.index(b)
        k = len(F)
        side1 = [F[(i + t) % k] for t in range(((j - i) % k) + 1)]
        side2 = [F[(j + t) % k] for t in range(((i - j) % k) + 1)]
        inner = path[1:-1]
        faces[adm[0]] = side1 + inner[::-1]
        faces.append(side2 + inner)
        HV |= set(path)
        for t in range(len(path) - 1):
            HE.add(frozenset((path[t], path[t + 1])))
    return True


def is_planar(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        if u != v:
            adj[u].add(v); adj[v].add(u)
    m = sum(len(a) for a in adj) // 2
    if n >= 3 and m > 3 * n - 6:
        return False
    return all(dmp_block(b) for b in blocks(n, adj))


if __name__ == '__main__':
    data = sys.stdin.read().split(); p = 0
    while p < len(data):
        n, m = int(data[p]), int(data[p + 1]); p += 2
        es = [(int(data[p + 2 * i]), int(data[p + 2 * i + 1])) for i in range(m)]; p += 2 * m
        print(1 if is_planar(n, es) else 0)
