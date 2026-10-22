"""dumbbell DB(c1, c2, l) edge list; edge order: cycle 1 (shared path first), then cycle 2's private part.
l < 0: cycles share a path of -l edges; l = 0: share one vertex; l > 0: joined by a path of l edges."""
import sys
c1, c2, l = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
E = []; nv = 0
def newv():
    global nv; nv += 1; return nv - 1
if l < 0:
    s = -l
    P = [newv() for _ in range(s + 1)]
    for i in range(s): E.append((P[i], P[i + 1]))
    Q1 = [newv() for _ in range(c1 - s - 1)]
    path = [P[-1]] + Q1 + [P[0]]
    for i in range(len(path) - 1): E.append((path[i], path[i + 1]))
    Q2 = [newv() for _ in range(c2 - s - 1)]
    path = [P[-1]] + Q2 + [P[0]]
    for i in range(len(path) - 1): E.append((path[i], path[i + 1]))
elif l == 0:
    C1 = [newv() for _ in range(c1)]
    for i in range(c1): E.append((C1[i], C1[(i + 1) % c1]))
    C2 = [C1[0]] + [newv() for _ in range(c2 - 1)]
    for i in range(c2): E.append((C2[i], C2[(i + 1) % c2]))
else:
    C1 = [newv() for _ in range(c1)]
    for i in range(c1): E.append((C1[i], C1[(i + 1) % c1]))
    path = [C1[0]] + [newv() for _ in range(l)]
    for i in range(l): E.append((path[i], path[i + 1]))
    C2 = [path[-1]] + [newv() for _ in range(c2 - 1)]
    for i in range(c2): E.append((C2[i], C2[(i + 1) % c2]))
print(nv, len(E))
for u, v in E: print(u, v)
