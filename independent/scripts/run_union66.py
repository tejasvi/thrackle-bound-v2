"""run_union66.py UNIONDIR THR: decide thrackleability of every graph file listed in UNIONDIR/classes.json (unions66.py output)
with thr_indep, using as filters the complete planar systems of the two 6-cycles C and D, each computed by thr_indep --dumpall on
that subgraph.  The filter subgraphs take their edges from the class file itself (same vertex ids and orientations; thr_indep
rejects a filter edge whose orientation differs).  Appends one line per class to UNIONDIR/decide.txt.  Optional third
argument: process only that class file."""
import sys, os, json, subprocess, time
ud, thr = sys.argv[1], sys.argv[2]
cl = json.load(open(os.path.join(ud, 'classes.json')))
out = open(os.path.join(ud, 'decide.txt'), 'a')
for rec in cl['classes']:
    if 'file' not in rec or (len(sys.argv) > 3 and rec['file'] != sys.argv[3]): continue
    fn = os.path.join(ud, rec['file'])
    lines = open(fn).read().split('\n'); n, m = map(int, lines[0].split())
    E = [tuple(map(int, l.split())) for l in lines[1:1 + m]]
    base = fn[:-4]
    sub = {}
    for name in ('C', 'D'):
        hl = open(f'{base}_{name}.txt').read().split('\n'); hm = int(hl[0].split()[1])
        want = {frozenset(map(int, l.split())) for l in hl[1:1 + hm]}
        es = [e for e in E if frozenset(e) in want]
        assert len(es) == 6, (rec['file'], name, len(es))
        hf = f'{base}_{name}f.txt'; sf = f'{base}_{name}f_sys.txt'
        with open(hf, 'w') as f:
            f.write(f'{n} 6\n' + ''.join(f'{u} {v}\n' for u, v in es))
        if not os.path.exists(sf):
            subprocess.run([thr, hf, '--dumpall', sf], check=True, capture_output=True)
        sub[name] = (hf, sf)
    t0 = time.time()
    r = subprocess.run([thr, fn, '--decide', '--filter', *sub['C'], '--filter', *sub['D']], capture_output=True, text=True)
    res = [l for l in r.stdout.splitlines() if l.startswith('RESULT')]
    nsys = [sum(1 for l in open(sub[k][1]) if l.strip() and not l.startswith('#')) for k in ('C', 'D')]
    line = (f"{rec['file']} {rec['tag']} n={n} m={m} filters C:{nsys[0]} D:{nsys[1]} :: "
            f"{res[-1] if res else 'NO RESULT ' + r.stderr[-200:]} ({time.time() - t0:.1f}s)")
    print(line, flush=True); out.write(line + '\n'); out.flush()
