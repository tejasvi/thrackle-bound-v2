#!/bin/sh
# task_A.sh I: slice I of 4096 of the 8-edge states of the A+C cycle listing; writes every complete planar system.
i=$1; o=out_A/$i
./thr_indep_v2 t337_AC.txt --states AC_L8.states --slice "$i" 4096 --dumpall "$o.sys.tmp" > "$o.out.tmp" 2> "$o.err" || exit 1
grep -q '^RESULT' "$o.out.tmp" || exit 1
mv "$o.sys.tmp" "$o.sys" && mv "$o.out.tmp" "$o.out" && touch "$o.done"
