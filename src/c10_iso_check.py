"""c10_iso_check.py PLAIN TEMPLATE: checks that two complete-system lists of 10-cycles describe the same set of drawings.
PLAIN is the dump of graphs/C10.txt (edge i = i -> i+1 mod 10); TEMPLATE the dump of graphs/sub_T337s_C10A.txt
(edges 0->1, 1->2, 2->3, 0->4, 4->5, 5->6, 6->7, 7->8, 8->9, 9->3). The cycle isomorphism maps plain vertex v to
template vertex (0,1,2,3,9,8,7,6,5,4)[v]; plain edge i goes to template edge tau[i] = (0,1,2,9,8,7,6,5,4,3)[i], reversed
for i >= 3. A plain system maps to a template system by renaming partners with tau and reversing the rows of reversed
edges. Prints both counts and whether the mapped plain set equals the template set; exit 0 iff equal."""
import sys

TAU = (0, 1, 2, 9, 8, 7, 6, 5, 4, 3)
PV = (0, 1, 2, 3, 9, 8, 7, 6, 5, 4)


def edges(lines):
    h = int(lines[0].split()[1])
    return h, [tuple(map(int, l.split())) for l in lines[1:1 + h]]


def body(path):
    with open(path) as f:
        lines = f.read().split('\n')
    h, E = edges(lines)
    return E, [l for l in lines[1 + h:] if l]


def main():
    Ep, P = body(sys.argv[1])
    Et, T = body(sys.argv[2])
    assert Ep == [(i, (i + 1) % 10) for i in range(10)], 'plain listing'
    flip = []
    for i, (u, v) in enumerate(Ep):
        a, b = PV[u], PV[v]
        tu, tv = Et[TAU[i]]
        assert {a, b} == {tu, tv}, 'edge map'
        flip.append((a, b) != (tu, tv))
    assert flip == [False] * 3 + [True] * 7
    mapped = set()
    for l in P:
        rows = [[int(x) for x in r.split()] for r in l.split('|')]
        out = [None] * 10
        for i in range(10):
            r = [TAU[x] for x in rows[i]]
            out[TAU[i]] = r[::-1] if flip[i] else r
        mapped.add('|'.join(' '.join(map(str, r)) for r in out))
    tset = set(T)
    print(f'plain systems {len(P)} (distinct {len(mapped)}), template systems {len(T)} (distinct {len(tset)})')
    eq = mapped == tset
    print('mapped plain set == template set:', eq)
    if not eq:
        print('only in mapped plain:', len(mapped - tset), ' only in template:', len(tset - mapped))
    sys.exit(0 if eq else 1)


if __name__ == '__main__':
    main()
