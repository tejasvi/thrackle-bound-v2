#!/bin/bash
# PROVISIONAL C10 list for TIMING ONLY (never for the decision run): finished original slices (minus the redone ones)
# plus all redo output so far; then level-8 states with it and a seeded sample of 64 states.
set -eu
cd "$(dirname "$0")"
UNF=$(sed -n 's/^unfinished slices //p' sys/C10t_redo.info)
mkdir -p sys/c10r_prov
python3 -I -B - <<'PY'
import glob, os
for f in glob.glob('sys/c10r/C10r_s*.sys'):
    i = f.split('_s')[-1][:-4]
    done = 'RESULT' in open(f'logs/c10r_s{i}.log').read()
    L = open(f).read().split('\n')
    h = int(L[0].split()[1])
    body = L[1 + h:]
    if body and body[-1] == '':
        body = body[:-1]
    if not done and body:
        body = body[:-1]          # a running process may have written a partial last line
    body = [l for l in body if l.count('|') == h - 1]
    open(f'sys/c10r_prov/C10r_s{i}.sys', 'w').write('\n'.join(L[:1 + h] + body) + '\n')
PY
python3 -I -B concat_dump.py sys/C10t_redo_states7.txt sys/C10r_prov.sys sys/c10r_prov/C10r_s*.sys
FILES=""
for f in sys/c10t/C10t_s*.sys; do
  i=${f#sys/c10t/C10t_s}; i=${i%.sys}
  skip=0; for u in $UNF; do [ "$u" = "$i" ] && skip=1; done
  [ $skip = 0 ] && FILES="$FILES $f"
done
python3 -I -B concat_dump.py sys/C10t_states6.txt sys/T337s_C10_prov.sys $FILES sys/C10r_prov.sys
./thr2_static_v3 graphs/T337s_prefix9.txt --dump sys/T337s_states9_prov.txt \
  --filter sys/T337s_C10_prov.sys=0,1,2,6,7,8,x,x,x,x --filter sys/T337s_C10_prov.sys=3,4,5,6,7,8,x,x,x,x > logs/t337_states9_prov.log 2>&1
grep RESULT logs/t337_states9_prov.log
python3 -I -B - <<'PY'
import random
lines = open('sys/T337s_states9_prov.txt').read().splitlines()
h = int(lines[0].split()[1]); hdr = lines[:1 + h]; st = [l for l in lines[1 + h:] if l.strip()]
rng = random.Random(20261022)
idx = sorted(rng.sample(range(len(st)), min(64, len(st))))
open('sys/T337s_sample_prov.txt', 'w').write('\n'.join(hdr + [st[i] for i in idx]) + '\n')
print(len(st), 'level-8 states (provisional); sample', len(idx))
PY
