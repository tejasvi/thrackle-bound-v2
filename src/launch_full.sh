#!/bin/bash
# DB(6,8,-1)r full run, share K: 96 slices of the symmetric level-9 states; filters C8, Ha, Hb
K=$1
cd "$(dirname "$0")"
: > logs/full.pids
for i in $(seq 0 95); do
  nohup nice -n 5 ./thr2_static_v2 graphs/DB_6_8_-1r.txt --filter sys/DB681_C8.sys=0,6,7,8,9,10,11,12 \
    --filter sys/DB681_Ha.sys=0,6,7,8,9,10,11,12,1 --filter sys/DB681r_Hb.sys=0,6,7,8,9,10,11,12,5 \
    --states sys/share_$K.txt --slice $i/96 > logs/full_s$i.log 2>&1 < /dev/null &
  echo $! >> logs/full.pids
done
echo "share $K started $(wc -l < logs/full.pids)"
