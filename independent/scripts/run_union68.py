"""run_union68.py UNIONDIR THR: decide thrackleability of every union class file (two-C6, other, DB) with thr_indep, using as
filters the complete planar systems of the class's 6-cycle C (first 6 edges) and of its 8-cycle F, each computed by
thr_indep --dumpall on that subgraph (same vertex ids and orientations).  Appends one line per class to UNIONDIR/decide.txt."""
import sys, os, json, subprocess, time
ud, thr = sys.argv[1], sys.argv[2]
cl = json.load(open(os.path.join(ud, 'classes.json')))
F8 = [(i, (i + 1) % 8) for i in range(8)]
out = open(os.path.join(ud, 'decide.txt'), 'a')
for rec in cl['classes']:
    if 'file' not in rec: continue
    fn = os.path.join(ud, rec['file'])
    lines = open(fn).read().split('\n'); n, m = map(int, lines[0].split())
    E = [tuple(map(int, l.split())) for l in lines[1:1 + m]]
    # relabelling used in the file: sorted original node ids -> 0..n-1; recover F's edges in file labels
    nodes = sorted({v for e in rec['C'] for v in e} | set(range(8)))
    lab = {v: j for j, v in enumerate(nodes)}
    Fset = {frozenset((lab[u], lab[v])) for u, v in F8}
    Fe = [e for e in E if frozenset(e) in Fset]
    assert len(Fe) == 8, rec['file']
    base = fn[:-4]
    for name, es in (('C6', E[:6]), ('C8', Fe)):
        with open(f'{base}_{name}.txt', 'w') as f:
            f.write(f'{n} {len(es)}\n' + ''.join(f'{u} {v}\n' for u, v in es))
        if not os.path.exists(f'{base}_{name}_sys.txt'):
            subprocess.run([thr, f'{base}_{name}.txt', '--dumpall', f'{base}_{name}_sys.txt'], check=True, capture_output=True)
    t0 = time.time()
    r = subprocess.run([thr, fn, '--decide', '--filter', f'{base}_C6.txt', f'{base}_C6_sys.txt',
                        '--filter', f'{base}_C8.txt', f'{base}_C8_sys.txt'], capture_output=True, text=True)
    res = [l for l in r.stdout.splitlines() if l.startswith('RESULT')]
    line = f"{rec['file']} {rec['tag']} n={n} m={m} :: {res[-1] if res else 'NO RESULT ' + r.stderr[-200:]} ({time.time() - t0:.1f}s)"
    print(line, flush=True); out.write(line + '\n'); out.flush()
