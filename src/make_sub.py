"""make_sub.py GRAPH i0,i1,... > SUBGRAPH : the subgraph on the listed G-edges (in that order, same orientations),
vertices renumbered in order of appearance."""
import sys
lines = open(sys.argv[1]).read().split()
n, m = int(lines[0]), int(lines[1])
E = [(int(lines[2 + 2 * i]), int(lines[3 + 2 * i])) for i in range(m)]
idx = [int(x) for x in sys.argv[2].split(',')]
vm = {}
def v(x):
    if x not in vm: vm[x] = len(vm)
    return vm[x]
sub = [(v(E[i][0]), v(E[i][1])) for i in idx]
print(len(vm), len(sub))
for a, b in sub: print(a, b)
