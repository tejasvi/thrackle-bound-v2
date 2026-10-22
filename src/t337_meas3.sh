#!/bin/bash
# theta(3,3,7) timing sample: slices FIRST..LAST of NS over SAMPLE, both C10 filters from SYS, staggered starts, cap MAXSEC
FIRST=$1; LAST=$2; NS=$3; SYS=$4; SAMPLE=$5; MAXSEC=${6:-1800}; STAG=${7:-15}; TAG=${8:-m}
cd "$(dirname "$0")"
: > logs/t337$TAG.pids
for i in $(seq $FIRST $LAST); do
  nohup ./thr2_static_v3 graphs/T337s.txt --filter $SYS=0,1,2,6,7,8,9,10,11,12 --filter $SYS=3,4,5,6,7,8,9,10,11,12 \
    --states $SAMPLE --slice $i/$NS --maxsec $MAXSEC > logs/t337${TAG}_s$i.log 2>&1 < /dev/null &
  echo $! >> logs/t337$TAG.pids
  sleep $STAG
done
echo "started $(wc -l < logs/t337$TAG.pids)"
