#!/bin/bash
# run_union.sh GRAPH NAME MAXSEC: prep (order, orientation, cycle filters), dump each cycle's systems, run the decision search
set -u
G=$1; NAME=$2; MAXSEC=${3:-500}
cd "$(dirname "$(readlink -f "$0")")"
mkdir -p prep sys/u
python3 -I prep.py $G prep/$NAME 8 > prep/$NAME.prep.log
ARGS=""
k=0
while read -r CYC; do
  [ -z "$CYC" ] && continue
  python3 -I make_sub.py prep/$NAME.txt $CYC > prep/${NAME}_cyc$k.txt
  ./thr2 prep/${NAME}_cyc$k.txt --dump sys/u/${NAME}_cyc$k.sys > /dev/null 2>&1
  ARGS="$ARGS --filter sys/u/${NAME}_cyc$k.sys=$CYC"
  k=$((k + 1))
done < prep/$NAME.filters
echo "$NAME: $(cat prep/$NAME.prep.log | cut -c1-150)"
timeout $((MAXSEC + 30)) ./thr2 prep/$NAME.txt $ARGS --maxsec $MAXSEC 2>/dev/null | grep -E "RESULT"
