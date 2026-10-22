"""mk_dumbbell.py C1 C2 K OUT [--second-first]: dumbbell DB(C1, C2, -K) (two cycles sharing a path of K edges), own labelling:
shared path 0 -> 1 -> ... -> K; cycle A closes with a path K -> a_1 -> ... -> 0 (C1 - K edges), cycle B with a path
K -> b_1 -> ... -> 0 (C2 - K edges).  Edge order: shared path, then cycle A's path, then cycle B's path (with
--second-first: shared path, B's path, A's path).  Prints the edge list summary."""
import sys
c1, c2, k, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
second_first = '--second-first' in sys.argv
edges = [(i, i + 1) for i in range(k)]
nv = k + 1
def closing(length):
    global nv
    vs = [k] + [nv + i for i in range(length - 1)] + [0]
    nv += length - 1
    return [(vs[i], vs[i + 1]) for i in range(length)]
A = closing(c1 - k); B = closing(c2 - k)
edges += (B + A) if second_first else (A + B)
with open(out, 'w') as f:
    f.write(f'{nv} {len(edges)}\n')
    for u, v in edges: f.write(f'{u} {v}\n')
print(out, nv, 'vertices', len(edges), 'edges:', edges)
