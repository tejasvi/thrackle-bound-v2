"""mk_theta.py A B C OUT: the theta graph theta(A,B,C): poles 0 and 1 joined by three internally disjoint paths with
A, B, C edges; edges listed path by path, each oriented from pole 0 towards pole 1 (file order = search order)."""
import sys
a, b, c, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
edges = []; nv = 2
for L in (a, b, c):
    vs = [0] + list(range(nv, nv + L - 1)) + [1]; nv += L - 1
    edges += [(vs[i], vs[i + 1]) for i in range(L)]
open(out, 'w').write(f'{nv} {len(edges)}\n' + ''.join(f'{u} {v}\n' for u, v in edges))
print(out, nv, len(edges))
