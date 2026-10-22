#!/bin/sh
# task_B.sh I: slice I of 1024 of the 9-edge states of theta(3,3,7), both C10 filters; writes the 10-edge states.
i=$1; o=out_B/$i
./thr_indep_v2 theta_337.txt --bigfilter t337_AC.txt C10H.sys --bigfilter t337_BC.txt C10H.sys \
    --states T_L9.states --slice "$i" 1024 --dump 10 "$o.states.tmp" > "$o.out.tmp" 2> "$o.err" || exit 1
grep -q '^RESULT' "$o.out.tmp" || exit 1
mv "$o.states.tmp" "$o.states" && mv "$o.out.tmp" "$o.out" && touch "$o.done"
