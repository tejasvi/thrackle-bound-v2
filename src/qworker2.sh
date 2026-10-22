#!/bin/bash
# qworker2.sh NPROC NT TASKFILE STATES: like qworker.sh, but limits the number of decision processes on the whole
# machine (so it can run next to orphaned or other workers' tasks) and skips tasks whose log already exists.
NPROC=$1; NT=$2; TASKS=$3; STATES=$4
cd "$(dirname "$0")"
while read -r i; do
  [ -z "$i" ] && continue
  [ -f logs/q_s$i.log ] && continue
  while [ "$(pgrep -fc -- '--states sys/T337s_states10')" -ge "$NPROC" ]; do sleep 3; done
  ./thr2_static_v3 graphs/T337s.txt --filter sys/T337s_C10.sys=0,1,2,6,7,8,9,10,11,12 \
    --filter sys/T337s_C10.sys=3,4,5,6,7,8,9,10,11,12 --states $STATES --slice $i/$NT > logs/q_s$i.log 2>&1 < /dev/null &
  echo "$! $i" >> logs/q.pids
  sleep 1
done < $TASKS
wait
echo "worker2 done $(date -u +%T) ($TASKS)" >> logs/q_worker.log
