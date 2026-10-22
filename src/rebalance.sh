#!/bin/bash
# rebalance on one of the two 64-worker machines: the main worker is already stopped; keep all but the last NMOVE unstarted tasks here
# (new worker qworker2.sh, machine-wide limit NPROC), write the last NMOVE to tasks_moved.txt for another machine
NMOVE=$1; NPROC=$2
cd "$(dirname "$0")"
python3 -I -B - "$NMOVE" <<'PY'
import os, sys
n = int(sys.argv[1])
t = [l.strip() for l in open('tasks.txt') if l.strip()]
un = [i for i in t if not os.path.exists(f'logs/q_s{i}.log')]
moved, keep = un[-n:], un[:-n]
open('tasks_r1.txt', 'w').write('\n'.join(keep) + '\n')
open('tasks_moved.txt', 'w').write('\n'.join(moved) + '\n')
print('unstarted', len(un), 'keep', len(keep), 'moved', len(moved))
PY
nohup bash qworker2.sh $NPROC 4096 tasks_r1.txt sys/T337s_states10.txt > logs/q_worker2.log 2>&1 < /dev/null &
echo "worker2 pid $!" | tee -a logs/q_worker.pid
