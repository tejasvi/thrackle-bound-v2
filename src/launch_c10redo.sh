#!/bin/bash
# re-split the unfinished C10-template slices: redo all level-6 states of the slices without a RESULT line, split at
# level 7 over NP processes (the original slices keep running; whichever finishes first is used)
NP=${1:-88}
cd "$(dirname "$0")"
mkdir -p sys/c10r
python3 -I -B - <<'PY'
import glob, re
lines = open('sys/C10t_states6.txt').read().splitlines()
h = int(lines[0].split()[1]); hdr = lines[:1 + h]; st = [l for l in lines[1 + h:] if l.strip()]
unf = sorted(int(re.search(r'_s(\d+)\.log', f).group(1)) for f in glob.glob('logs/c10t_s*.log') if 'RESULT' not in open(f).read())
redo = [j for j in range(len(st)) if j % 96 in unf]
open('sys/C10t_redo_states6.txt', 'w').write('\n'.join(hdr + [st[j] for j in redo]) + '\n')
open('sys/C10t_redo.info', 'w').write('unfinished slices ' + ' '.join(map(str, unf)) + '\nredo states ' + ' '.join(map(str, redo)) + '\n')
print('unfinished slices', unf, 'redo states', len(redo))
PY
./thr2_static_v3 graphs/T337s_C10A_prefix7.txt --states sys/C10t_redo_states6.txt --dump sys/C10t_redo_states7.txt > logs/c10r_prefix7.log 2>&1
tail -2 logs/c10r_prefix7.log | head -1
: > logs/c10r.pids
for i in $(seq 0 $((NP - 1))); do
  nohup nice -n 5 ./thr2_static_v3 graphs/sub_T337s_C10A.txt --states sys/C10t_redo_states7.txt --slice $i/$NP --dump sys/c10r/C10r_s$i.sys > logs/c10r_s$i.log 2>&1 < /dev/null &
  echo $! >> logs/c10r.pids
done
echo "started $(wc -l < logs/c10r.pids)"
