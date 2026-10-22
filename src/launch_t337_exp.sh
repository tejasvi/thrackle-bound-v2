#!/bin/bash
# DB(6,10,-3) planning experiments: C9 list, C10 list (split over level-6 states), theta(3,3,7) unfiltered growth
cd "$(dirname "$0")"
mkdir -p logs sys/c10
: > logs/exp.pids
nohup ./thr2_static_v3 graphs/C9.txt --dump sys/C9.sys > logs/c9.log 2>&1 < /dev/null &
echo $! >> logs/exp.pids
nohup ./thr2_static_v3 graphs/r_DB_6_10_-3.txt --maxsec 1800 > logs/t337_unf.log 2>&1 < /dev/null &
echo $! >> logs/exp.pids
./thr2_static_v3 graphs/C10_prefix6.txt --dump sys/C10_states6.txt > logs/c10_prefix6.log 2>&1 < /dev/null
for i in $(seq 0 93); do
  nohup nice -n 5 ./thr2_static_v3 graphs/C10.txt --states sys/C10_states6.txt --slice $i/94 --dump sys/c10/C10_s$i.sys > logs/c10_s$i.log 2>&1 < /dev/null &
  echo $! >> logs/exp.pids
done
echo "started $(wc -l < logs/exp.pids) processes; C10 level-6 states: $(grep -v '^H' sys/C10_states6.txt | tail -n +8 | wc -l)"
