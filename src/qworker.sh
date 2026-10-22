#!/bin/bash
# qworker.sh NPROC NT TASKFILE STATES [RAMP]: DB(6,10,-3) decision run, task pool on this machine. Runs task i
# (--slice i/NT of STATES, both C10 filters) for every i in TASKFILE whose log has no RESULT line yet, at most NPROC at
# a time; the first NPROC starts are spaced RAMP s apart (filter loading needs memory transiently).
NPROC=$1; NT=$2; TASKS=$3; STATES=$4; RAMP=${5:-4}
cd "$(dirname "$0")"
started=0
while read -r i; do
  [ -z "$i" ] && continue
  [ -f logs/q_s$i.log ] && grep -q RESULT logs/q_s$i.log && continue
  while [ "$(jobs -rp | wc -l)" -ge "$NPROC" ]; do sleep 2; done
  ./thr2_static_v3 graphs/T337s.txt --filter sys/T337s_C10.sys=0,1,2,6,7,8,9,10,11,12 \
    --filter sys/T337s_C10.sys=3,4,5,6,7,8,9,10,11,12 --states $STATES --slice $i/$NT > logs/q_s$i.log 2>&1 < /dev/null &
  echo "$! $i" >> logs/q.pids
  started=$((started+1))
  [ "$started" -le "$NPROC" ] && sleep $RAMP
done < $TASKS
wait
echo "worker done $(date -u +%T)" >> logs/q_worker.log
