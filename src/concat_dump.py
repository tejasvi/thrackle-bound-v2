"""concat_dump.py STATES OUT SLICE_DUMP...: merge the --dump files of a split run (--states STATES --slice i/N) into one
dump in the order a single unsplit run would write: systems grouped by the prefix state they extend (state order of
STATES), slice output order kept within a group. A system extends state t iff, for every prefix edge e < L, its row of e
restricted to partners < L equals t's row of e. Checks: equal headers, every system extends exactly one state, no
duplicate systems. Prints the counts."""
import sys


def rows_of(line):
    return [[int(x) for x in r.split()] for r in line.rstrip('\n').split('|')]


def read_dump(path):
    with open(path) as f:
        head = f.readline()
        _, h, nv = head.split()
        h = int(h)
        edges = [f.readline() for _ in range(h)]
        body = [l for l in f if l.strip()]
    return head, edges, body


def main():
    states_path, out_path, slices = sys.argv[1], sys.argv[2], sys.argv[3:]
    sh, se, sbody = read_dump(states_path)
    L = int(sh.split()[1])
    key_index = {}
    for i, l in enumerate(sbody):
        key = tuple(tuple(r) for r in rows_of(l))
        assert len(key) == L and key not in key_index
        key_index[key] = i
    head = edges = None
    groups = [[] for _ in sbody]
    total = 0
    for p in slices:
        h2, e2, body = read_dump(p)
        if head is None:
            head, edges = h2, e2
        assert h2 == head and e2 == edges, f'header mismatch in {p}'
        assert [x.split() for x in se] == [x.split() for x in edges[:L]], 'prefix edges differ'
        for l in body:
            r = rows_of(l)
            key = tuple(tuple(x for x in r[e] if x < L) for e in range(L))
            groups[key_index[key]].append(l if l.endswith('\n') else l + '\n')
            total += 1
    seen = set()
    with open(out_path, 'w') as f:
        f.write(head)
        f.writelines(edges)
        for g in groups:
            for l in g:
                assert l not in seen, 'duplicate system'
                seen.add(l)
                f.write(l)
    print(f'merged {len(slices)} slice dumps: {total} systems, {sum(1 for g in groups if g)} of {len(groups)} states '
          f'with systems, written {out_path}')


if __name__ == '__main__':
    main()
