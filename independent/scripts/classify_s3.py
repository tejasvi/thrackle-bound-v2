"""Classify the s = 3 walks of runs10.json (union U = Q + edges(W), Q = the 6-cycle 0..5): two-6-cycle / C6-C8 exclusions, then isomorphism classes of the rest and
which of theta(2,3,3), theta(2,3,4), theta(3,3,7) each class contains (subgraph monomorphism) or equals."""
import json, sys
import networkx as nx
from networkx.algorithms import isomorphism as iso

def theta(a, b, c):
    G = nx.Graph(); nv = 2
    for L in (a, b, c):
        vs = [0] + list(range(nv, nv + L - 1)) + [1]; nv += L - 1
        G.add_edges_from((vs[i], vs[i + 1]) for i in range(L))
    return G

d = json.load(open(sys.argv[1]))["3"]
T = {"theta(2,3,3)": theta(2, 3, 3), "theta(2,3,4)": theta(2, 3, 4), "theta(3,3,7)": theta(3, 3, 7)}
print("walks", len(d["walks"]), "excluded_two_c6", d["excluded_two_c6"], "excluded_c6c8", d["excluded_c6c8"],
      "excluded_either", d["excluded_either"])
two = c68 = 0; rest = []
for w in d["walks"]:
    wk = w["walk"]
    G = nx.Graph(); G.add_edges_from((i, (i + 1) % 6) for i in range(6)); G.add_edges_from((wk[i], wk[(i + 1) % len(wk)]) for i in range(len(wk)))
    a, b = w["two_c6_common_vertex"], w["c6_c8_common_edge"]
    if a: two += 1
    if b: c68 += 1
    tag = ("2C6" if a else "") + ("+" if a and b else "") + ("C6C8" if b else "")
    if not (a or b): rest.append((wk, G))
    print(wk, "n", G.number_of_nodes(), "m", G.number_of_edges(), tag or "-")
print("two_c6 flag", two, "c6c8 flag", c68, "both", sum(1 for w in d["walks"] if w["two_c6_common_vertex"] and w["c6_c8_common_edge"]))
classes = []
for wk, G in rest:
    for c in classes:
        if nx.is_isomorphic(c[0][1], G): c.append((wk, G)); break
    else: classes.append([(wk, G)])
print("remaining", len(rest), "classes", len(classes))
for i, c in enumerate(classes):
    G = c[0][1]
    eq = [k for k, H in T.items() if nx.is_isomorphic(G, H)]
    sub = [k for k, H in T.items() if iso.GraphMatcher(G, H).subgraph_is_monomorphic()]
    print("class", i, "size", len(c), "n", G.number_of_nodes(), "m", G.number_of_edges(), "equals", eq, "contains", sub,
          "walks", [x[0] for x in c])
