"""account_split_run.py RUNS: accounting of the split DB(6,8,-1) run.  Every chunk runs/m1/chunks/cNNNNN must be decided
NOT_THRACKLEABLE either by its own run (runs/m1/out/cNNNNN.out: one RESULT line, NOT_THRACKLEABLE, complete_planar=0,
resumed = lines of the chunk) or by the split run (runs/m1s/: the level-10 dump of the chunk resumed every chunk line,
filtered none at resume (or counts them), found no complete system, dumped K states; and each of the K slices
runs/m1s/cNNNNN.s<i>.out decided NOT_THRACKLEABLE with resumed = 1).  Prints a JSON summary."""
import os, re, json, sys
base = sys.argv[1]
chunks = sorted(os.listdir(os.path.join(base, 'm1', 'chunks')))
pat = re.compile(r'^RESULT graph=(\S+) m=(\d+) complete_planar=(\d+) (\S+) tests=(\d+) planar_tests=(\d+) dumped=(\d+) '
                 r'resumed=(\d+) filtered_at_resume=(\d+) secs=([0-9.]+)$')
def res(path):
    if not os.path.exists(path): return None
    rs = [pat.match(l.strip()) for l in open(path) if l.startswith('RESULT')]
    rs = [r for r in rs if r]
    if not rs: return None                     # still running (no RESULT line yet)
    return rs[-1] if len(rs) == 1 else ('BAD', len(rs))
S = dict(chunks=len(chunks), states=0, by_orig=0, by_split=0, by_both=0, undecided=[], bad=[], thrackleable=[],
         orig_tests=0, orig_secs=0.0, split_tasks=0, split_tests=0, split_secs=0.0, filtered_at_resume=0)
for c in chunks:
    nl = sum(1 for l in open(os.path.join(base, 'm1', 'chunks', c)) if l.strip())
    S['states'] += nl
    ok_o = ok_s = False
    r = res(os.path.join(base, 'm1', 'out', c + '.out'))
    if isinstance(r, tuple): S['bad'].append((c, 'orig', r))
    elif r is not None:
        if r.group(4) != 'NOT_THRACKLEABLE' or r.group(3) != '0': S['thrackleable'].append((c, 'orig', r.group(0)))
        elif int(r.group(8)) != nl: S['bad'].append((c, 'orig resumed', r.group(8), nl))
        else:
            ok_o = True; S['orig_tests'] += int(r.group(5)); S['orig_secs'] += float(r.group(10))
            S['filtered_at_resume'] += int(r.group(9))
    d = res(os.path.join(base, 'm1s', c + '.dump.out'))
    if d is not None and not isinstance(d, tuple):
        K = int(d.group(7)); good = d.group(3) == '0' and int(d.group(8)) == nl
        L10 = os.path.join(base, 'm1s', c + '.L10')
        if not os.path.exists(L10) or sum(1 for l in open(L10) if l.strip()) != K: good = False
        tests = int(d.group(5)); secs = float(d.group(10)); done = 0
        for i in range(K):
            s = res(os.path.join(base, 'm1s', f'{c}.s{i}.out'))
            if s is None or isinstance(s, tuple): break
            if s.group(4) != 'NOT_THRACKLEABLE' or s.group(3) != '0': S['thrackleable'].append((c, f'split {i}', s.group(0))); break
            if int(s.group(8)) != 1: good = False; break
            done += 1; tests += int(s.group(5)); secs += float(s.group(10))
        if good and done == K:
            ok_s = True; S['split_tasks'] += K; S['split_tests'] += tests; S['split_secs'] += secs
    if ok_o and ok_s: S['by_both'] += 1
    elif ok_o: S['by_orig'] += 1
    elif ok_s: S['by_split'] += 1
    else: S['undecided'].append(c)
S['n_undecided'] = len(S['undecided']); S['undecided'] = S['undecided'][:50]
S['verdict'] = ('ALL %d CHUNKS (%d level-9 states) NOT_THRACKLEABLE' % (len(chunks), S['states'])
                if not S['undecided'] and not S['bad'] and not S['thrackleable'] else 'INCOMPLETE OR PROBLEM')
print(json.dumps(S, indent=1))
