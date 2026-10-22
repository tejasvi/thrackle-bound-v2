#!/bin/sh
# task_C.sh I: slice I of 4096 of the 9-edge states of theta(3,3,7), both C10 filters, decide.
i=$1; o=out_C/$i
./thr_indep_v2 theta_337.txt --bigfilter t337_AC.txt C10H.sys --bigfilter t337_BC.txt C10H.sys \
    --decide --states T_L9.states --slice "$i" 4096 > "$o.out.tmp" 2> "$o.err" || exit 1
grep -q '^RESULT' "$o.out.tmp" || exit 1
mv "$o.out.tmp" "$o.out" && touch "$o.done"
