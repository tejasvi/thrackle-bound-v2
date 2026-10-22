#!/bin/bash
# theta(3,3,7) prep, redo-aware: merge the C10-template list from the finished original slices plus the re-split redo
# (states of the unfinished slices, split at level 7), then dump the level-8 states with both C10 filters and sample.
set -eu
cd "$(dirname "$0")"
UNF=$(sed -n 's/^unfinished slices //p' sys/C10t_redo.info)
python3 -I -B concat_dump.py sys/C10t_redo_states7.txt sys/C10r_merged.sys sys/c10r/C10r_s*.sys
FILES=""
for f in sys/c10t/C10t_s*.sys; do
  i=${f#sys/c10t/C10t_s}; i=${i%.sys}
  skip=0; for u in $UNF; do [ "$u" = "$i" ] && skip=1; done
  if [ $skip = 0 ]; then grep -q RESULT logs/c10t_s$i.log || { echo "slice $i unfinished and not redone"; exit 1; }; FILES="$FILES $f"; fi
done
python3 -I -B concat_dump.py sys/C10t_states6.txt sys/T337s_C10.sys $FILES sys/C10r_merged.sys
sha256sum sys/T337s_C10.sys
./thr2_static_v3 graphs/T337s_prefix9.txt --dump sys/T337s_states9.txt \
  --filter sys/T337s_C10.sys=0,1,2,6,7,8,x,x,x,x --filter sys/T337s_C10.sys=3,4,5,6,7,8,x,x,x,x > logs/t337_states9.log 2>&1
grep RESULT logs/t337_states9.log
python3 -I -B - <<'PY'
import random
lines = open('sys/T337s_states9.txt').read().splitlines()
h = int(lines[0].split()[1]); hdr = lines[:1 + h]; st = [l for l in lines[1 + h:] if l.strip()]
rng = random.Random(20261022)
idx = sorted(rng.sample(range(len(st)), min(192, len(st))))
open('sys/T337s_sample192.txt', 'w').write('\n'.join(hdr + [st[i] for i in idx]) + '\n')
open('sys/T337s_sample192.idx', 'w').write(' '.join(map(str, idx)) + '\n')
print(len(st), 'level-8 states; sample', len(idx))
PY
