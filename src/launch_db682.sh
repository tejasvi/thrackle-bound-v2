#!/bin/bash
# DB(6,8,-2) split run: 96 slices of the 26,550 level-9 states; filters C8, H2, H5
cd "$(dirname "$0")"
: > logs/db682.pids
for i in $(seq 0 95); do
  nohup nice -n 5 ./thr2_static graphs/DB_6_8_-2.txt --filter sys/DB682_C8.sys=0,1,6,7,8,9,10,11 \
    --filter sys/DB682_H2.sys=0,1,6,7,8,9,10,11,2 --filter sys/DB682_H5.sys=0,1,6,7,8,9,10,11,5 \
    --states sys/DB682_states9.txt --slice $i/96 > logs/db682_s$i.log 2>&1 < /dev/null &
  echo $! >> logs/db682.pids
done
echo "started $(wc -l < logs/db682.pids)"
