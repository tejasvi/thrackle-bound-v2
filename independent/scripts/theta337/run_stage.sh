#!/bin/sh
# run_stage.sh STAGE IDSFILE PAR: run ./task_STAGE.sh ID for every ID in IDSFILE that has no done marker, PAR at a time.
# Resumable: a task writes to .tmp files and marks out_STAGE/ID.done only after its RESULT line is complete.
cd "$(dirname "$0")" || exit 1
st=$1; ids=$2; par=$3
mkdir -p "out_$st"
grep -v '^$' "$ids" | xargs -P "$par" -I{} sh -c "[ -e out_$st/{}.done ] || ./task_$st.sh {}"
echo FINISHED > "out_$st/STAGE_DONE.$(basename "$ids")"
