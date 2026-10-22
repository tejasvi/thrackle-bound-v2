#!/bin/bash
# C10 template list for the theta(3,3,7) filters (sub_T337s_C10A = sub_T337s_C10B): split over the level-6 states
cd "$(dirname "$0")"
mkdir -p logs sys/c10t
: > logs/c10t.pids
./thr2_static_v3 graphs/T337s_C10A_prefix6.txt --dump sys/C10t_states6.txt > logs/c10t_prefix6.log 2>&1 < /dev/null
for i in $(seq 0 95); do
  nohup nice -n 5 ./thr2_static_v3 graphs/sub_T337s_C10A.txt --states sys/C10t_states6.txt --slice $i/96 --dump sys/c10t/C10t_s$i.sys > logs/c10t_s$i.log 2>&1 < /dev/null &
  echo $! >> logs/c10t.pids
done
echo "started $(wc -l < logs/c10t.pids); $(tail -2 logs/c10t_prefix6.log | head -1)"
