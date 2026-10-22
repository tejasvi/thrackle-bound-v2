#!/bin/bash
# level-9 states of DB(6,10,-3) (complete planar systems of the first 10 edges, both C10 filters with x for e10..e12):
# split over the 32,626 level-8 states; slices FIRST..LAST of NS; PIDs in logs/p10.pids
FIRST=$1; LAST=$2; NS=$3; STAG=${4:-5}
cd "$(dirname "$0")"
mkdir -p sys/p10
: > logs/p10.pids
for i in $(seq $FIRST $LAST); do
  nohup ./thr2_static_v3 graphs/T337s_prefix10.txt --filter sys/T337s_C10.sys=0,1,2,6,7,8,9,x,x,x \
    --filter sys/T337s_C10.sys=3,4,5,6,7,8,9,x,x,x --states sys/T337s_states9.txt --slice $i/$NS \
    --dump sys/p10/T337s_p10_s$i.sys > logs/p10_s$i.log 2>&1 < /dev/null &
  echo $! >> logs/p10.pids
  sleep $STAG
done
echo "started $(wc -l < logs/p10.pids)"
