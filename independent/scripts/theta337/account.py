"""account.py RUNDIR: checks the three stages of the theta(3,3,7) run in RUNDIR and prints a JSON summary.

Stage A: part i of 4096 resumed the 8-edge states of t337_AC.txt (AC_L8.states) with index = i mod 4096 and listed
         all complete planar systems (out_A/i.out, out_A/i.sys); C10H.sys is the concatenation of out_A/0.sys, ...,
         out_A/4095.sys in this order.
Stage B: part i of 1024 resumed the 9-edge states of theta_337.txt (T_L9.states) with index = i mod 1024 and wrote
         the 10-edge states (out_B/i.out, out_B/i.states); T_L10.states is their concatenation in part order.
Stage C: part i of 4096 resumed the 9-edge states (T_L9.states) with index = i mod 4096, with --decide
         (out_C/i.out).  (Stage B is the listing of the 10-edge states, for comparison with the first program; the
         search itself resumes at nine edges.)
For every stage: every part has exactly one RESULT line, and its resumed= count equals the number of indices
congruent to i, so that the parts cover every state exactly once.  Stage A: the systems add up to the lines of
C10H.sys.  Stage B: the dumped states add up to the lines of T_L10.states.  Stage C: every part reports
NOT_THRACKLEABLE and complete_planar=0."""
import json, os, sys

D = sys.argv[1]


def lines(path):
    n = 0
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 24), b''):
            n += block.count(b'\n')
    return n


def parse(path):
    res = [l for l in open(path) if l.startswith('RESULT ')]
    if len(res) != 1:
        return None
    kv = {}
    for tok in res[0].split()[1:]:
        if '=' in tok:
            k, v = tok.split('=', 1); kv[k] = v
        else:
            kv['verdict'] = tok
    return kv


def stage(name, nparts, states_file, extra):
    L = lines(os.path.join(D, states_file))
    out = dict(parts=nparts, states=L, missing=[], bad_resumed=[], tests=0, planar_tests=0, cpu_seconds=0.0,
               longest_part_seconds=0.0, complete_planar=0, dumped=0, filtered_at_resume=0, verdicts={})
    resumed = 0
    for i in range(nparts):
        kv = parse(os.path.join(D, f'out_{name}', f'{i}.out')) if os.path.exists(os.path.join(D, f'out_{name}', f'{i}.out')) else None
        if kv is None:
            out['missing'].append(i); continue
        expect = (L - 1 - i) // nparts + 1 if i < L else 0
        r = int(kv['resumed']); resumed += r
        if r != expect:
            out['bad_resumed'].append([i, r, expect])
        out['tests'] += int(kv['tests']); out['planar_tests'] += int(kv['planar_tests'])
        s = float(kv['secs']); out['cpu_seconds'] += s; out['longest_part_seconds'] = max(out['longest_part_seconds'], s)
        out['complete_planar'] += int(kv['complete_planar']); out['dumped'] += int(kv['dumped'])
        out['filtered_at_resume'] += int(kv['filtered_at_resume'])
        out['verdicts'][kv['verdict']] = out['verdicts'].get(kv['verdict'], 0) + 1
    out['resumed'] = resumed
    out['cover_exactly_once'] = (not out['missing'] and not out['bad_resumed'] and resumed == L)
    out['cpu_hours'] = round(out['cpu_seconds'] / 3600, 1)
    out.update(extra(out))
    return out


def extra_A(o):
    p = os.path.join(D, 'C10H.sys')
    n = lines(p) if os.path.exists(p) else None
    return dict(list_lines=n, list_ok=(n == o['complete_planar']))


def extra_B(o):
    p = os.path.join(D, 'T_L10.states')
    n = lines(p) if os.path.exists(p) else None
    return dict(l10_lines=n, l10_ok=(n == o['dumped']))


def extra_C(o):
    return dict(all_not_thrackleable=(o['verdicts'] == {'NOT_THRACKLEABLE': o['parts']} and o['complete_planar'] == 0))


rep = {}
if os.path.isdir(os.path.join(D, 'out_A')):
    rep['A'] = stage('A', 4096, 'AC_L8.states', extra_A)
if os.path.isdir(os.path.join(D, 'out_B')):
    rep['B'] = stage('B', 1024, 'T_L9.states', extra_B)
if os.path.isdir(os.path.join(D, 'out_C')):
    rep['C'] = stage('C', 4096, 'T_L9.states', extra_C)
print(json.dumps(rep, indent=1))
