#!/bin/sh
# final_C.sh: after stage C, check all stages (account.py), hash the inputs and lists, and pack the logs.
cd "$(dirname "$0")" || exit 1
n=$(ls out_C | grep -c '\.done$'); [ "$n" -eq 4096 ] || { echo "stage C incomplete: $n of 4096 done"; exit 1; }
python3 -I -B account.py . > accounting.json || exit 1
sha256sum AC_L8.states T_L9.states C10H.sys C10H.sys.pos T_L10.states theta_337.txt t337_AC.txt t337_BC.txt \
    thr_indep_v2 thr_indep graphs/C9.txt > final_hashes.txt
wc -l AC_L8.states T_L9.states C10H.sys T_L10.states > final_lines.txt
tar czf final_C.tgz out_C/*.out accounting.json final_hashes.txt final_lines.txt stageA.log stageB.log stageC.log \
    stageA.start stageB.start stageC.start
ls -la final_C.tgz; cat final_lines.txt
