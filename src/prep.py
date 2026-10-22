"""prep.py GRAPH OUTPREFIX [maxcyc]: reorder and reorient the edges of GRAPH for the thrackle search and prepare cycle
filters. Edge order: a shortest cycle first (in cycle order), then greedily the unplaced edge that closes the shortest
cycle with the placed edges (ties: touches placed vertices). Each edge is oriented away from an already placed vertex.
Writes OUTPREFIX.txt (graph) and OUTPREFIX.filters (lines "subgraph_edge_list" for every simple cycle of length
5..maxcyc, in cycle order). Systems are dumped by run_union.sh."""
import sys
from collections import deque

L = open(sys.argv[1]).read().split()
n, m = int(L[0]), int(L[1])
E = [(int(L[2 + 2 * i]), int(L[3 + 2 * i])) for i in range(m)]
maxcyc = int(sys.argv[3]) if len(sys.argv) > 3 else 8
adj = [set() for _ in range(n)]
for i, (u, v) in enumerate(E):
    adj[u].add((v, i)); adj[v].add((u, i))


def shortest_cycle_through(ei, allowed):
    """shortest cycle using edge ei and edges in allowed (set of edge ids); returns list of edge ids or None"""
    u, v = E[ei]
    prev = {u: None}; q = deque([u])
    while q:
        x = q.popleft()
        for y, j in adj[x]:
            if j == ei or j not in allowed or y in prev:
                continue
            prev[y] = (x, j); q.append(y)
    if v not in prev:
        return None
    path = []; x = v
    while prev[x] is not None:
        x0, j = prev[x]; path.append(j); x = x0
    return [ei] + path[::-1]


# all simple cycles (edge sets) up to maxcyc
def all_cycles():
    out = {}
    for s in range(n):
        stack = [(s, [s], [])]
        while stack:
            x, pv, pe = stack.pop()
            for y, j in adj[x]:
                if y == s and len(pe) >= 2 and j not in pe:
                    cyc = pe + [j]
                    if 5 <= len(cyc) <= maxcyc:
                        out.setdefault(frozenset(cyc), (pv, cyc))
                elif y > s and y not in pv and len(pe) < maxcyc - 1:
                    stack.append((y, pv + [y], pe + [j]))
    return list(out.values())


cycles = all_cycles()
cycles.sort(key=lambda c: len(c[1]))
order = []
placed_v = set()
if cycles:
    pv, cyc = cycles[0]
    order = list(cyc)
remaining = [i for i in range(m) if i not in order]
while remaining:
    best = None
    pl = set(order)
    for i in remaining:
        c = shortest_cycle_through(i, pl | {i})
        clen = len(c) if c else 10 ** 6
        touch = sum(1 for x in E[i] if any(x in E[j] for j in order))
        key = (clen, -touch, i)
        if best is None or key < best[0]:
            best = (key, i)
    order.append(best[1]); remaining.remove(best[1])
# orientation: walk the order, orient away from a placed vertex
pv = set(); NE = []
for k, i in enumerate(order):
    u, v = E[i]
    if k == 0:
        NE.append((u, v))
    elif u in pv or v not in pv:
        NE.append((u, v))
    else:
        NE.append((v, u))
    pv |= {u, v}
newidx = {i: k for k, i in enumerate(order)}
with open(sys.argv[2] + '.txt', 'w') as f:
    f.write(f'{n} {m}\n')
    for u, v in NE:
        f.write(f'{u} {v}\n')
with open(sys.argv[2] + '.filters', 'w') as f:
    for pvv, cyc in cycles:
        f.write(','.join(str(newidx[j]) for j in cyc) + '\n')
print(f'order {order}; {len(cycles)} cycles of length 5..{maxcyc}: ' + ' '.join(str(len(c[1])) for c in cycles))
