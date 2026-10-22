# Second implementation of the search, and the enumerations

This directory contains:
- a second implementation of the thrackleability search of Section 5, in two versions: version 2 adds an option for
  filter lists with millions of systems and is otherwise identical;
- separate implementations of the enumerations behind Lemmas 3.2, 3.4 and 4.3 and of the discharging arithmetic of
  Section 4, for c = 15/11, 27/20, 51/38 and 4/3;
- the outputs of their runs, including the three dumbbells of Theorem 3.5, DB(5,5,-2), DB(5,6,-2) and DB(6,10,-3).

With these programs we repeated all searches and enumerations of the paper: the counts for C3, ..., C10 and for C8
with a pendant edge, Theorems 1.2, 3.1 and 3.5, Lemmas 3.2 and 3.4, the walks of Lemma 4.3 and the classes of their
unions, and the discharging of Section 4.

The search program was written from a description of the method (the Fulek-Pach criterion, Lemma 2.4, and the
pruning by complete lists of systems for subgraphs), Scoppetto (arXiv:2610.17508, Section 3) and Fulek and Pach
(2011), without reading the code of the first program. It differs from the first program in three ways:
- it uses a different planarity test;
- it uses its own edge orders and splittings;
- it uses no symmetry reduction.

Licence: Apache-2.0 (LICENSE). The planarity library is not included; see below.

## Contents

| path | contents |
|---|---|
| src/thr_indep.c | the search, version 1 (augmented graph, edge-by-edge search, filters, dump/resume of split states) |
| src/thr_indep_v2.c | version 2: version 1 plus --bigfilter, the same filters kept as lists of candidate systems; used for DB(6,10,-3) and its 10-cycle list |
| src/planarity_test.c | a small self-test of the planarity library (K5 minus an edge, K3,3, a grid) |
| scripts/mk_dumbbell.py | writes DB(c1, c2, -k) in a given edge order |
| scripts/prep_dumbbell.py | writes DB(6,8,-k) (8-cycle first) and its six filter subgraphs with their complete systems |
| scripts/unions68.py, run_union68.py, run_one_class68.py | Lemma 3.2: unions of a 6-cycle and an 8-cycle sharing an edge, and their decisions |
| scripts/unions66.py, unions66e.py, run_union66.py | Lemma 3.4: unions of two 6-cycles sharing a vertex (84 classes) or an edge (58 classes), and their decisions |
| scripts/runs10.py | Lemma 4.3: the closed 10-walks containing a run of s 6-edges, in two independent ways |
| scripts/classify_s3.py | Lemma 4.3, s = 3: the exclusions of the 19 unions and the isomorphism classes of the other nine, with the theta graphs they contain (needs networkx) |
| scripts/mk_theta.py | writes the theta graph with paths of lengths A, B, C between two poles |
| scripts/theta337/ | the DB(6,10,-3) run in three resumable stages (run_stage.sh, task_A.sh, task_B.sh, task_C.sh), the assembly steps between them (after_A.sh, after_B.sh), and the final check (final_C.sh, which runs account.py and hashes the files) |
| scripts/account_split_run.py | checks that every chunk of the split DB(6,8,-1) run was decided |
| scripts/discharge_check.py | every number of Lemmas 4.4-4.6 and of the proof of Theorem 1.1, for c = 15/11, 27/20 and 51/38, in exact arithmetic |
| scripts/discharge_check_43.py | the same for c = 4/3, where the final charges of 8-faces and of 10-faces with six 6-edges are 0 and the bound is non-strict |
| inputs/graphs, inputs/dumbbells, inputs/theta | the graph files; systems_sha256.txt lists the hashes of the generated system files |
| results/ | the outputs, described below |

## Requirements and build

The programs need gcc, Python 3 (standard library; the 6-cycle and 8-cycle enumerations and classify_s3.py also need networkx) and the
Edge Addition Planarity Suite.

The planarity library is the Edge Addition Planarity Suite (graphLib), version 5.0.0.0, as bundled in the PyPI
package planarity 1.0.0:
- sdist sha256 9129d2429fc54c70a976cdf59b21a9c6a542466cf49747c1bbce1f27d59f4f3e;
- https://pypi.org/project/planarity/1.0.0/ and https://github.com/graph-algorithms/planarity;
- BSD-3-Clause licence, Copyright (c) 1997-2026 John M. Boyer.

Build:

    pip download --no-binary :all: --no-deps planarity==1.0.0 && tar xzf planarity-1.0.0.tar.gz
    L=planarity-1.0.0/planarity/c/graphLib
    INC="-I$L -I$L/lowLevelUtils -I$L/planarityRelated -I$L/extensionSystem -I$L/homeomorphSearch -I$L/io"
    mkdir -p obj && for f in $(find $L -name '*.c'); do gcc -O2 -w $INC -c $f -o obj/$(basename $f .c).o; done
    ar rcs libeaps.a obj/*.o
    gcc -O2 -Wall -Wno-unused-result $INC -o thr_indep src/thr_indep.c libeaps.a
    gcc -O2 -Wall -Wno-unused-result $INC -o thr_indep_v2 src/thr_indep_v2.c libeaps.a
    gcc -O2 -w $INC -o planarity_test src/planarity_test.c libeaps.a

The runs used the same build with -static added. Built in this way, each of the two sources gives a binary that is
identical to the binary that ran once both are stripped of symbols and of the build-id note
(`strip --remove-section=.note.gnu.build-id`), with gcc 15.2.0 and GNU ld 2.46. Unstripped, the two differ only in the
source file name in the symbol table and in the build-id derived from it. The hashes of the binaries that ran are in
results/theta337_hashes.txt.

## The search program

    ./thr_indep GRAPH [--decide] [--filter HFILE SYSFILE]... [--dump L OUT] [--states FILE --slice I N] [--dumpall OUT]
    ./thr_indep_v2 GRAPH [the same options] [--bigfilter HFILE SYSFILE]...

- GRAPH is "n m" followed by m lines "u v"; edge i is oriented from u to v, and the file order is the search order.
- Without --decide the program counts the complete planar systems. With --decide it stops at the first one and
  prints THRACKLEABLE, or prints NOT_THRACKLEABLE.
- A filter is a subgraph HFILE of GRAPH (same vertex ids and orientations, so its edges must appear in GRAPH with the
  same orientation) together with the full list SYSFILE of its complete planar systems, made by --dumpall. A branch
  whose orders on HFILE fit none of these systems is pruned.
- --bigfilter (version 2 only) is the same filter for lists too long for bit sets: the consistent systems are kept
  as an explicit list of candidate indices, checked against a table of the positions of the crossings in each listed
  system. The table is written once to SYSFILE.pos and then mapped read-only.
- --dump L writes every surviving state after L complete edges. --states FILE --slice I N resumes the states of
  FILE whose index is congruent to I mod N.
- The output is one line: `RESULT graph=... m=... complete_planar=... NOT_THRACKLEABLE|THRACKLEABLE|count tests=...
  planar_tests=... dumped=... resumed=... filtered_at_resume=... secs=...`.
- In the result files, graph= gives the run's directory names: graphs/ and dbprep/ correspond to inputs/graphs/ and
  inputs/dumbbells/, theta/ and the bare names theta_337.txt, t337_AC.txt correspond to inputs/theta/, while unions/
  and unions66/ are the output directories of the enumerations.

## Reproducing the results

1. Calibration: `./thr_indep inputs/graphs/C8.txt` and likewise for the other cycles and C8p.txt (C8 with a
   pendant edge). DB66m3.txt and DB66m2.txt were run with --decide and no filter.
2. Dumbbell inputs:
   - `python3 scripts/prep_dumbbell.py K ./thr_indep D` for K = 1, 2, 3 writes DB68mK.txt and the six filters
     DB68mK_{C8,C6,C8b0,C8b1,C6a0,C6a1}.txt with their _sys.txt systems.
   - `python3 scripts/mk_dumbbell.py 8 6 K D/DB68mK_6first.txt --second-first` writes the 6-cycle-first order, which
     has the same edges and orientations.
   - Put F="--filter D/DB68mK_C8.txt D/DB68mK_C8_sys.txt ..." for all six filters.
3. DB(6,8,-3): `./thr_indep D/DB68m3_6first.txt --decide $F`, and the same with D/DB68m3.txt.
4. DB(6,8,-2) and DB(6,8,-1):
   - `./thr_indep D/DB68mK_6first.txt $F --dump 8 L8`
   - `./thr_indep D/DB68mK_6first.txt $F --states L8 --slice 0 1 --dump 9 L9`
   - then `./thr_indep D/DB68mK_6first.txt $F --decide --states L9 --slice I N` for I = 0, ..., N-1.
   The level-9 files have the hashes given in the result headers. DB(6,8,-2) used N = 200. DB(6,8,-1) used 4,079
   files of 8 consecutive states each, each run with --slice 0 1.
   For the slowest DB(6,8,-1) chunks the level-9 states were also dumped to level 10 (`--states CHUNK --slice 0 1
   --dump 10 CHUNK.L10`), and each level-10 state was decided separately. A chunk counts as decided when one of the
   two runs is complete. `python3 scripts/account_split_run.py RUNS` checks this.
5. Lemma 3.2:
   - `python3 scripts/unions68.py U` gives 1,045 choices and 343 classes.
   - Then `python3 scripts/run_union68.py U ./thr_indep`, or `run_one_class68.py U ./thr_indep CLASSFILE` for one
     class.
6. Lemma 3.4:
   - `python3 scripts/unions66.py V` gives 1,544 choices and 84 classes.
   - `python3 scripts/unions66e.py E` gives 208 choices and 58 classes.
   - Then `python3 scripts/run_union66.py V ./thr_indep [CLASSFILE]`.
   - DB(6,6,0) was split at level 9 (32,626 states) with its two 6-cycle filters, and decided in 400 interleaved
     slices.
7. Lemma 4.3: `python3 scripts/runs10.py W`, then `python3 scripts/classify_s3.py W/runs10.json` for s = 3.
8. Discharging: `python3 scripts/discharge_check.py` and `python3 scripts/discharge_check_43.py`.
9. DB(5,5,-2) and DB(5,6,-2): `./thr_indep inputs/theta/theta_233.txt --decide` and the same for theta_234.txt, with
   both versions and no filters. C9: `./thr_indep inputs/graphs/C9.txt`.
10. DB(6,10,-3), in a directory holding thr_indep_v2 (a static build), the files of inputs/theta/ and the scripts
    of scripts/theta337/. Every edge of theta_337.txt is oriented from pole 0 to pole 1, the 6-cycle
    comes first and the 7-path last. t337_AC.txt and t337_BC.txt are the two 10-cycles, each listed as the 3-path
    followed by the 7-path, so they are the same oriented graph with the same edge order and use one list C10H.sys.
    - Split states: `./thr_indep_v2 t337_AC.txt --dump 8 AC_L8.states` and `./thr_indep_v2 theta_337.txt --dump 9
      T_L9.states` (no filters).
    - Stage A, the list of the complete planar systems of the 10-cycle: `./run_stage.sh A IDS P` for the part ids
      0..4095, then `for i in $(seq 0 4095); do cat out_A/$i.sys; done > C10H.sys`. One run with --bigfilter
      writes C10H.sys.pos before the next stage starts.
    - Stage B, the states on the first ten edges: `./run_stage.sh B IDS P` for 0..1023, then T_L10.states is the
      concatenation of out_B/0.states, ..., out_B/1023.states.
    - Stage C, the search: `./run_stage.sh C IDS P` for 0..4095. It resumes the 9-edge states, not the 10-edge
      states of stage B. Every resume rebuilds the candidate lists of both filters from the whole list of 6,059,712
      systems, which took about 2.7 s per resume with all threads busy, against about 4.7 s of search below an
      average 10-edge state; the split at nine edges makes 37 times fewer resumes. Stage B serves to compare the
      number of 10-edge states with the first program.
    - run_stage.sh skips the parts that are already done, so after an interruption the same command finishes the stage.
      `python3 scripts/theta337/account.py DIR` checks every part of every stage.

## Results

| claim | result | file |
|---|---|---|
| complete planar systems of C3, ..., C8 | 1, 0, 1, 8, 92, 2,544 | calibration.txt |
| C8 with a pendant edge | 60,196 (with and without the C8 filter) | calibration.txt |
| dump/resume | C8 + pendant gives 60,196 when dumped at level 5 and resumed whole, in 3 slices, with the C8 filter at level 6, and in two steps (levels 3 and 7) | dump_resume_tests.txt |
| DB(6,6,-3), DB(6,6,-2) without filters | not thrackleable | calibration.txt |
| DB(6,8,-3), two edge orders | not thrackleable | db6_8_3.txt |
| DB(6,8,-2) | 26,550 level-9 states in 200 slices, all not thrackleable, 650,586,506 tests | db6_8_2_slices.txt |
| DB(6,8,-1) | 32,626 level-9 states in 4,079 chunks; 4,010 decided by their own run, 53 by both runs, 16 by the level-10 split; none thrackleable; about 1,130 CPU-hours | db6_8_1_chunks.tsv, db6_8_1_accounting.json |
| Lemma 3.2 | 343 classes: 266 with a triangle, 60 with a C4, DB(6,8,-1), DB(6,8,-2), DB(6,8,-3), 4 with two 6-cycles sharing a vertex, 10 others; the 14 are not thrackleable | union68_classes.json, union68_decisions.txt |
| Lemma 3.4 | vertex mode: 84 classes (56 triangle, 20 C4, DB(6,6,0..-3), 4 others); edge mode: 58 classes (38, 15, DB(6,6,-1..-3), 2 others), each isomorphic to a vertex-mode class; all not thrackleable | union66_vertex_classes.json, union66_edge_classes.json, union66_decisions.txt, db6_6_split.json, db6_6_split_slices.txt |
| Lemma 4.3 | 0, 3, 4 and 19 walks for s = 6, 5, 4, 3, the same for both methods. Each s = 5 union contains two 6-cycles with a common vertex; each s = 4 union contains a 6-cycle and an 8-cycle sharing an edge | runs10.json |
| discharging, c = 15/11, 27/20, 51/38 | all printed values pass | discharge_check.out |
| Lemma 4.3, s = 3 | 5 unions with two 6-cycles sharing a vertex and 5 more with a 6-cycle and an 8-cycle sharing an edge; the other 9 fall into 5 classes, of sizes 1, 2, 4, 1, 1: DB(5,5,-2), classes containing DB(5,5,-2), containing DB(5,6,-2), containing DB(5,5,-2), and DB(6,10,-3) | s3_classes.txt |
| discharging, c = 4/3 | all checks pass | discharge_check_43.out |
| C9 | 72,916 complete planar systems (version 1, 204,998,075 tests) | c9_count.txt |
| C10 (as t337_AC.txt) | 6,059,712 complete planar systems; 4,096 parts covering the 143,557 states on eight edges once each; 22,926,241,152 tests, about 227 CPU-hours | theta337_stageA.txt, theta337_accounting.json |
| DB(5,5,-2), DB(5,6,-2) | not thrackleable, no filters, both versions (17,578 and 856,864 tests) | theta_small.txt |
| DB(6,10,-3), states | 32,626 states on the first nine edges; 1,211,878 states on the first ten edges (1,024 parts, 16,690,052 tests) | theta337_stageB.txt |
| DB(6,10,-3) | 4,096 parts covering the 32,626 states on the first nine edges once each, all not thrackleable; 83,418,336,044 planarity tests (36,316,208,498 planar), about 1,593 CPU-hours, longest part 7,148 s | theta337_stageC.txt, theta337_accounting.json, theta337_hashes.txt |

The DB(6,8,-1) run used 216 processes on one 224-thread machine. The level-10 split used up to 160 further
processes on idle threads. The DB(6,10,-3) run used 224 processes on one 224-thread machine, for stages A, B and C
one after the other.

Below the 10-edge states, the DB(6,10,-3) search made 83,418,336,044 - 16,690,052 = 83,401,645,992 planarity tests
(stage C minus stage B, which made exactly the tests of stage C above the 10-edge states). This number, the number of
10-edge states and the size of the 10-cycle list are the same as those reported for the first program.

## Relation to the copies that ran

The runs used copies of these files under other file names, with other descriptions in their comments and docstrings.
The C sources here are identical to them once comments are removed, and the Python files have the same syntax trees
once docstrings are removed. There are three exceptions:
- account_split_run.py now requires its argument; the run used a default directory.
- discharge_check.py prints a shorter final line.
- the scripts in scripts/theta337/ call ./thr_indep_v2 (and final_C.sh also hashes thr_indep); the copies that ran
  used other names for the same static builds.
