#!/bin/bash
# DB(6,10,-3) = theta(3,3,7) decision run (graphs/T337s.txt): slices FIRST..LAST of NS over the 32,626 level-8 states,
# both C10 filters (sys/T337s_C10.sys, the merged template list), starts staggered by STAG s; PIDs in logs/t337f.pids
FIRST=$1; LAST=$2; NS=$3; STAG=${4:-10}
cd "$(dirname "$0")"
: > logs/t337f.pids
for i in $(seq $FIRST $LAST); do
  nohup ./thr2_static_v3 graphs/T337s.txt --filter sys/T337s_C10.sys=0,1,2,6,7,8,9,10,11,12 \
    --filter sys/T337s_C10.sys=3,4,5,6,7,8,9,10,11,12 --states sys/T337s_states9.txt --slice $i/$NS \
    --maxsec 40000 > logs/t337f_s$i.log 2>&1 < /dev/null &
  echo $! >> logs/t337f.pids
  sleep $STAG
done
echo "started $(wc -l < logs/t337f.pids)"
