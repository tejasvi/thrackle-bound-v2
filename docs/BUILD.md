# Build provenance and planarity validation

Staged 2026-10-21T21:48Z.
Nothing here changes a result. It records which source and which build command produced every binary used for a
published run, and the inputs, commands and outputs of the planarity validation.

Toolchain for every build: gcc 15.2.0 (Ubuntu 15.2.0-16ubuntu1), glibc 2.43. All commands below were run in the
working directory of the project, so paths such as graphs/, sys/, prep/ are relative to it.

## 1. Sources

lr.c and lr.h never changed after they were written. They are identical to src/lr.c
(sha256 0d5d6363...) and src/lr.h (6e6af993...); copies are in src_versions/.

thr2.c changed four times after its first build. Each change was a scripted text replacement; replaying the recorded
replacements on the first version (every replacement matched exactly once) gives the files in src_versions/, and the
last one is byte-identical to src/thr2.c. Versions are named by the UTC time of the build that
first used them.

| version | sha256 | change relative to the previous version |
|---|---|---|
| thr2_1322.c | 99dc28eb324ea0914a903c0fd7786892ee5fcc64d0b2a8807ba6da7e5f190d3f | first built version |
| thr2_1338.c | 6cfad0519e1e4385a04db3b5b9f3b7a43e2068d5a202d229aea3bb0f70aa5395 | filter maps accept "x" for an edge absent from the current graph (used for prefix dumps); progress counters on stderr |
| thr2_1349.c | 2745ba40824fff9550f8c08527f8f922a086ddacfda39d1c576515cb593a92d3 | --states FILE and --slice i/N: run the search from listed states (filters_init_state) |
| thr2_1408.c | 4448ba98376b3d23f8e5ae4d3a96b1c5b90118e0e250a994bbf219c1d44c3fd5 | filter bitset step iterates over the nonzero words only (active-word lists); performance only |
| thr2_1454.c | ef2e914947fc5ef76e86204e495867b1779cf4b12e0e3ac11cb9ecca5c7babf9 | --logg FILE p: write a random sample of the tested G' graphs (seeded xorshift); identical to src/thr2.c |

src_versions/steps/ has the diff for each step; src_versions/thr2_<v>_vs_frozen.diff compares each version with the
final version, src/thr2.c.

None of these changes can alter the result of a search that runs to completion:
- "x" entries: the new branches are taken only for filter maps that contain "x". Such maps occur only in the prefix
  state dumps (DB682_states9, DB681r_states9, the DB(6,8,-1) 10-edge states), all made with versions that have the
  feature (1349, 1408); the decision runs use full maps.
- Progress output and the time-cap check (when the cap is detected) do not affect a run that finishes.
- --states: without the option, main calls search_edge(0) exactly as before.
- Active-word lists: the filter bitsets are read only by the filter step itself and by the state initialisation. The
  active list holds exactly the nonzero words, and words outside it are never read, so every prune decision is
  unchanged. When the change was made, DB(6,6,-2) with its two filters gave identical counters before and after
  (planarity_tests=49867, planar=14563, filter_prunes=206244), and the C8+pendant count stayed 60,196.
- --logg reads G' after each planarity test and uses its own random generator.

## 2. Binaries

All four surviving binaries were rebuilt from the sources above with the recorded commands, in fresh directories
using the same file names. Every rebuild is bit-identical to the original.

| file | sha256 | source | build command | used by |
|---|---|---|---|---|
| bin/thr2_static | abc4fcb27ebf79f877559818d8c3397b1f4cfd8a4f3c09ce0e45f74e39ab35ff | thr2_1349.c | `gcc -O2 -march=x86-64-v2 -static -Wno-stringop-truncation -o bin/thr2_static thr2.c lr.c` | DB(6,8,-2) split run (src/launch_db682.sh, logs/db682). The copy on the run machine had the same sha256 prefix abc4fcb27ebf79f8, recorded at upload |
| bin/thr2_static_v2 | 430e1abedfbb1d18e05159de3de1d75498f4b959a69eaf42aa1bfed626054b5d | thr2_1408.c | same, `-o bin/thr2_static_v2` | DB(6,8,-1): the 10-edge state dump behind sys/DB681r_states10_sym.txt and DB681r_states10_full.sha256; the timing sample (src/launch_db681_sample.sh, logs/db681_sample); the full run (src/launch_full.sh, logs/db681_full). The prefix 430e1abe was recorded on all six run machines at upload |
| bin/thr2_static_v3 | c3e4e74a1d3d9145a89b2d3e7a8e1700ab3b779972c51013c99a5f460d45b888 | thr2_1454.c | same, `-o bin/thr2_static_v3` | logs/calib/db660.log (DB(6,6,0)); all runs in logs/db6103/ (DB(6,10,-3)). The copies on the six run machines had the same sha256 prefix c3e4e74a1d3d9145, recorded at upload |
| bin/thr2_dynamic_1454 | 29ff618b06df4de5cd7aad8c1220ba3a5fbbdc00eb260b4edb21d78fce00c0f9 | thr2_1454.c | `gcc -O2 -Wall -Wextra -Wno-stringop-truncation -o thr2 thr2.c lr.c` | logs/calib/cycles_count.log, logs/calib/dumbbells.log, logs/calib/union66_results.log and logs/calib/u610_results.log (run_union.sh), the filter dumps sys/DB661r_*.sys and sys/DB660r_*.sys; validation/gprime_sample.txt |
| bin/lr_cli | 0be53f025a23d0b03486bcabfda6fe25feab0d119d605c8dad4bd525df636641 | validation/lr_cli.c, lr.c, lr.h | `gcc -O2 -Wall -Wextra -o lr_cli lr_cli.c lr.c` | validation/val_lr.txt, val_lr2.txt |

The working dynamic binary ./thr2 was rebuilt in place after each source change, so the dynamic builds of the
earlier versions no longer exist. bin/rebuilt_dynamic/ holds rebuilds made now from the matching sources, with the
command used at the time. They are expected to equal the originals, since every surviving binary rebuilds
bit-identically on this toolchain, but the originals cannot be compared.

| file | sha256 | source | build command | produced |
|---|---|---|---|---|
| rebuilt_dynamic/thr2_dynamic_1322 | 6eebbc3ee79defe8309010063dea7d9e920c03a5df257b08f1600f9fbbe32952 | thr2_1322.c | `gcc -O2 -Wall -Wextra -o thr2 thr2.c lr.c` (adding -Wno-stringop-truncation gives the same binary) | sys/DB682_C8.sys, DB682_H2.sys, DB682_H5.sys, DB662_C6b.sys, DB662_C8o.sys |
| rebuilt_dynamic/thr2_dynamic_1338 | 74d068eb1b79da6ea42e6c0f9adf1bfe0c3e71ddc6c0f81e47fb00fd712994fc | thr2_1338.c | `gcc -O2 -Wall -Wextra -Wno-stringop-truncation -o thr2 thr2.c lr.c` | sys/DB681_C8.sys, DB681_Ha.sys, DB681r_Hb.sys |
| rebuilt_dynamic/thr2_dynamic_1349 | a957f4c3a68fa744e01e3a0b9b9047d168bb7e4ec03a4ad727b026e8c2d5b32a | thr2_1349.c | same | sys/DB682_states9.txt, sys/DB681r_states9.txt |
| rebuilt_dynamic/thr2_dynamic_1408 | 1c9b02cf3fa4d04a5f0731745e5d6fc7ed794674c49bd1cdbb1afd5520ed2db5 | thr2_1408.c | same | logs/union_results.txt (run_union.sh on the 15 graphs listed there, including the cycle-filter dumps it makes) |

This assignment comes from the recorded build and run order and is consistent with the modification times of the
outputs. Every listed output that also exists in the working directory (the sys/ files, logs/union_results.txt, the
calibration logs listed above) is byte-identical to its archived copy.

## 3. Planarity validation (validation/)

| file | sha256 | command |
|---|---|---|
| val_graphs.txt | 079ef1dcee832a4f7688312ddc515a45e478f44911cd18af503d4f4dc9efbed1 | `python3 -I gen_val.py 1 3000 > val_graphs.txt` |
| val_lr.txt | ffbf771abe30061bb3b53cb80a8138c366593c1f0ebd73f41d1a0850644ff9cc | `./lr_cli < val_graphs.txt > val_lr.txt` |
| val_dmp.txt | ffbf771abe30061bb3b53cb80a8138c366593c1f0ebd73f41d1a0850644ff9cc | `python3 -I dmp.py < val_graphs.txt > val_dmp.txt` |
| val_graphs2.txt | 931390950ddff0cce8bff386e5e4c17bacd6f423a255c8e4f32c7b08781e7e28 | `python3 -I gen_val.py 7 2000 220 > val_graphs2.txt` |
| val_lr2.txt | 9318ec62708ca70844d8206da12a20d7f2bff17884f522a6f512d830490d05bf | `./lr_cli < val_graphs2.txt > val_lr2.txt` |
| val_dmp2.txt | 9318ec62708ca70844d8206da12a20d7f2bff17884f522a6f512d830490d05bf | `python3 -I dmp.py < val_graphs2.txt > val_dmp2.txt` |
| gprime_sample.txt | 74c3a644dbb1e7148c235cbb350d86d75f2a4569a6afaaaa6195500995b8af1c | `./thr2 graphs/DB_6_8_-1r.txt --filter sys/DB681_C8.sys=0,6,7,8,9,10,11,12 --filter sys/DB681_Ha.sys=0,6,7,8,9,10,11,12,1 --filter sys/DB681r_Hb.sys=0,6,7,8,9,10,11,12,5 --maxsec 60 --logg prep/gprime_sample.txt 0.0003` |
| gprime_sample_in.txt | 8bdf12df73ad9e1892c7ecb090eb8f2de1dda91ead38753b16a6f6cdd1c6e4dc | `python3 -I gprime_convert.py` (reads prep/gprime_sample.txt, writes this file and gprime_sample_lr.txt) |
| gprime_sample_lr.txt | 5c73bcbcc1e7e70c093e7e0123bf57c3d79897213bb1280b637effe90553b98c | same |
| gprime_sample_dmp.txt | 5c73bcbcc1e7e70c093e7e0123bf57c3d79897213bb1280b637effe90553b98c | `python3 -I dmp.py < prep/gprime_sample_in.txt > prep/gprime_sample_dmp.txt` |

Scripts: gen_val.py (6b5a408e...; identical to src/gen_val.py), dmp.py (63dea3f9...; identical to
src/dmp.py), lr_cli.c (72cbc2a9...), gprime_convert.py (85adb8c3...; the conversion exactly as it was run).

Notes:
- val_graphs.txt was generated before gen_val.py gained its optional third argument (maximum n, default 60). With two
  arguments the current gen_val.py gives byte-identical output.
- The G' sample run stops at the 60 s cap by design (RESULT TIMEOUT, 8,488,548 planarity tests, 2,605 sampled
  graphs). The sample depends only on the test order and the seeded generator. A re-run of the same command reached
  2,620 samples, and the original 2,605 records are an exact prefix of its output.
- Identical sha256 for an LR file and its DMP file means the two tests agree on every graph.

Results: LR and DMP agree on all 3,000 + 2,000 random graphs (1,526 + 1,180 nonplanar, 1,474 + 820 planar) and on all
2,605 G' graphs sampled from the DB(6,8,-1) search (2,395 nonplanar, 210 planar). lr_cli run on gprime_sample_in.txt
reproduces the verdicts recorded inside the search. Every file in this section was regenerated during this check
and is byte-identical to the stored copy, apart from gprime_sample.txt, which is reproduced as a prefix as described.
