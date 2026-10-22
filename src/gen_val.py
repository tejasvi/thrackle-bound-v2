"""random test graphs for planarity validation: stacked triangulations +- random edges, G(n,m), subdivided K5/K33."""
import random, sys
rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
count = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
def stacked(n):
    E = {(0, 1), (0, 2), (1, 2)}; faces = [(0, 1, 2)]
    for v in range(3, n):
        f = faces.pop(rng.randrange(len(faces))); a, b, c = f
        E |= {(a, v), (b, v), (c, v)}; faces += [(a, b, v), (a, c, v), (b, c, v)]
    return E
def out(n, E):
    E = {(min(u, v), max(u, v)) for u, v in E if u != v}
    perm = list(range(n)); rng.shuffle(perm)
    E = [(perm[u], perm[v]) for u, v in E]; rng.shuffle(E)
    print(n, len(E))
    for u, v in E: print(u, v)
for t in range(count):
    kind = t % 4; n = rng.randint(5, int(sys.argv[3]) if len(sys.argv) > 3 else 60)
    if kind == 0:
        E = stacked(n); E = {e for e in E if rng.random() > rng.random() * 0.5}; out(n, E)
    elif kind == 1:
        E = stacked(n); E = {e for e in E if rng.random() > 0.3}
        for _ in range(rng.randint(1, 3)):
            u, v = rng.sample(range(n), 2); E.add((u, v))
        out(n, E)
    elif kind == 2:
        m = rng.randint(n, min(3 * n - 6, n * (n - 1) // 2)); E = set()
        while len(E) < m:
            u, v = rng.sample(range(n), 2); E.add((min(u, v), max(u, v)))
        out(n, E)
    else:
        base = [(i, j) for i in range(5) for j in range(i + 1, 5)] if rng.random() < 0.5 else \
               [(i, j) for i in range(3) for j in range(3, 6)]
        nv = 6; E = set()
        for u, v in base:
            k = rng.randint(0, 3); prev = u
            for _ in range(k):
                E.add((prev, nv)); prev = nv; nv += 1
            E.add((prev, v))
        if rng.random() < 0.5:   # delete one edge -> planar
            E.discard(rng.choice(sorted(E)))
        extra = rng.randint(0, 20)
        for _ in range(extra):
            u = rng.randrange(nv + 1); E.add((u, nv)); nv += 1
        out(nv, E)
