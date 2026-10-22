#!/bin/bash
# DB(6,8,-1) timing sample: 192 random level-8 states (of 32,626), 96 slices x 2 states; filters C8, Ha, Hb
cd "$(dirname "$0")"
: > logs/db681s.pids
for i in $(seq 0 95); do
  nohup nice -n 5 ./thr2_static_v2 graphs/DB_6_8_-1r.txt --filter sys/DB681_C8.sys=0,6,7,8,9,10,11,12 \
    --filter sys/DB681_Ha.sys=0,6,7,8,9,10,11,12,1 --filter sys/DB681r_Hb.sys=0,6,7,8,9,10,11,12,5 \
    --states sys/DB681r_sample192.txt --slice $i/96 > logs/db681s_s$i.log 2>&1 < /dev/null &
  echo $! >> logs/db681s.pids
done
echo "started $(wc -l < logs/db681s.pids)"
