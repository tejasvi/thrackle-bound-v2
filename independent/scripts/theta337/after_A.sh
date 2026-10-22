#!/bin/sh
# after_A.sh: assemble C10H.sys from the stage A parts in part order, write its line count and hash, and build
# C10H.sys.pos once (a run that only loads the big filter), so that the parallel stage B processes find it.
cd "$(dirname "$0")" || exit 1
n=$(ls out_A | grep -c '\.done$'); [ "$n" -eq 4096 ] || { echo "stage A incomplete: $n of 4096 done"; exit 1; }
[ -e C10H.sys ] && { echo "C10H.sys exists already"; exit 1; }
for i in $(seq 0 4095); do cat "out_A/$i.sys"; done > C10H.sys.tmp && mv C10H.sys.tmp C10H.sys || exit 1
wc -l < C10H.sys > C10H.lines
sha256sum C10H.sys > C10H.sha256
./thr_indep_v2 theta_337.txt --bigfilter t337_AC.txt C10H.sys --dump 0 /dev/null > posbuild.out 2>&1 || exit 1
sha256sum C10H.sys.pos > C10H.pos.sha256
echo "C10H.sys lines $(cat C10H.lines)"; cat C10H.sha256 C10H.pos.sha256 posbuild.out
