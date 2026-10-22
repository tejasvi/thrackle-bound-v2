#!/bin/sh
# after_B.sh: assemble T_L10.states from the stage B parts in part order and write its line count and hash.
cd "$(dirname "$0")" || exit 1
n=$(ls out_B | grep -c '\.done$'); [ "$n" -eq 1024 ] || { echo "stage B incomplete: $n of 1024 done"; exit 1; }
[ -e T_L10.states ] && { echo "T_L10.states exists already"; exit 1; }
for i in $(seq 0 1023); do cat "out_B/$i.states"; done > T_L10.states.tmp && mv T_L10.states.tmp T_L10.states || exit 1
wc -l < T_L10.states > T_L10.lines
sha256sum T_L10.states > T_L10.sha256
echo "T_L10.states lines $(cat T_L10.lines)"; cat T_L10.sha256
