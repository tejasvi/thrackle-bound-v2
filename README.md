# Computations for "A thrackle on n vertices has fewer than 4n/3 edges"

This repository contains the programs, input graphs, filter lists, split states and logs of the computations in the
paper. The paper is archived at doi:10.5281/zenodo.23554361; this repository is archived at doi:10.5281/zenodo.23554362.

## What is computed

| paper | statement | files |
|---|---|---|
| Theorem 1.2, Theorem 3.1 | DB(6,8,-1) is not thrackleable | `logs/db681_full/`, `logs/RESULTS_DB681.txt` |
| Theorem 1.2, Theorem 3.5 | DB(6,10,-3) is not thrackleable | `logs/db6103/` |
| Theorem 3.1 | DB(6,8,-2) and DB(6,8,-3) are not thrackleable | `logs/db682/`; `logs/union_results.txt` (line `r_udb_6`) |
| Lemma 3.2 | unions of a 6-cycle and an 8-cycle with a common edge: 343 classes; the 14 that need a search are not thrackleable | `src/unions.py`, `logs/unions_C6C8.log`, `logs/union_results.txt` |
| Lemma 3.4 | unions of two distinct 6-cycles with a common vertex (84 classes) or edge (58 classes) | `src/unions66.py`, `logs/calib/unions66_*.log`, `logs/calib/union66_results.log`, `logs/calib/dumbbells.log`, `logs/calib/db660.log` |
| Theorem 3.5 | DB(5,5,-2) and DB(5,6,-2) are not thrackleable | `logs/calib/u610_results.log` (`r_u610_3_0`, which is DB(5,5,-2), and `r_DB_5_6_-2`) |
| Lemma 4.3 | closed walks of length 10 along a run of 6-edges (0, 3, 4 and 19 walks for runs of length 6, 5, 4, 3) and the types of their unions | `src/unions610.py`, `src/unions610_check.py`, `logs/calib/unions610*.log`, `logs/calib/u610_results.log` |
| Section 5.1 | the left-right planarity test agrees with an implementation of the algorithm of Demoucron, Malgrange and Pertuiset | `validation/` |
| Section 5.3 | the 6,059,712 complete planar crossing systems of the oriented 10-cycle that serves as filter for DB(6,10,-3), computed twice | `sys/T337s_C10.sys.xz`; `logs/db6103/m2/` and `logs/db6103/m1/` (see below) |
| Section 5.4 | complete planar crossing systems of C3,...,C8 (1, 0, 1, 8, 92, 2,544) and of C8 with a pendant edge (60,196) | `logs/calib/cycles_count.log`, `logs/calib/dumbbells.log` |
| Section 5.4 | the second implementation: Theorems 3.1 and 3.5, Lemmas 3.2, 3.4 and 4.3, the discharging arithmetic and the checks, with the same results | `independent/` |
| Section 6 | the constants of the discharging (all except 51/38, which is `r_needed(10, 7)/2`) | `src/discharge.py` |

A dumbbell DB(c1,c2,-k) is the union of a c1-cycle and a c2-cycle whose intersection is a path with k edges, and
DB(c1,c2,0) is the union of two cycles with exactly one common vertex. DB(5,5,-2), DB(5,6,-2) and DB(6,10,-3) consist of
three paths between two vertices, of lengths 2, 3, 3, of lengths 2, 3, 4 and of lengths 3, 3, 7.

## The method

A graph G is thrackleable if and only if, for some crossing system, the augmented graph G' is planar (Fulek and Pach).
Orient every edge of G. A crossing system gives, for each edge e, the order in which the edges without a common
endpoint with e cross e. G' has one vertex for each crossing, one vertex on each segment between two consecutive
crossings of an edge, and for each crossing a 4-cycle through its four neighbours, alternating between the two edges.

`src/thr2.c` adds the edges in the order of the graph file and traces each new edge from its tail. At each step it
chooses the next crossing: an earlier edge without a common endpoint and a position in that edge's order. After each
step it tests the planarity of the partial augmented graph, which is obtained from the augmented graph of every
completion by deleting and contracting, and it prunes the branch if the graph is not planar. A filter is the complete
list of planar crossing systems of a subgraph, computed by the same program with `--dump`. A partial system whose
restriction to the subgraph extends to no listed system is pruned. Planarity is tested by the left-right algorithm
(`src/lr.c`).

## Building

```
gcc -O2 -o thr2 src/thr2.c src/lr.c
```

The large runs for DB(6,8,-1) and DB(6,8,-2) used static builds of earlier revisions of `src/thr2.c`, and the runs for
DB(6,10,-3) used `bin/thr2_static_v3`, a static build of `src/thr2.c` itself. These binaries are in `bin/`, with their
sources in `src_versions/` and the build commands, sha256 sums and the assignment of binaries to runs in `docs/BUILD.md`.
Each of these binaries is reproduced bit for bit by its recorded build command (gcc 15.2.0, glibc 2.43). The differences
between the revisions are command-line options (`x` entries in filter maps, `--states`/`--slice`, `--logg`) and a faster
implementation of the filter step; `src_versions/steps/` has the diffs. The files in `bin/` are stored without the
executable bit; to run them, check their sha256 against `docs/BUILD.md` and make them executable.

## File formats

- Graph files (`graphs/`): first line `n m`, then m lines `u v`; edge i is oriented from u to v, and the search adds the
  edges in this order.
- Rows of a crossing system: for each edge, the ids of the edges it crosses, in order from its tail.
- Filter and state files (`sys/`): first line `H h nv`, where h and nv are the numbers of edges and vertices of the
  subgraph; then h lines `u v` (the edges of the subgraph, with the orientations of G); then one line per complete planar
  system of the subgraph, giving the rows of its edges 0,...,h-1 separated by `|`. A filter is passed as
  `--filter FILE=g0,...,g_{h-1}`, where edge i of the subgraph is edge g_i of G, or `x` if that edge is not in G (used
  for prefix graphs).
- Logs: each run ends with a line `RESULT NOT_THRACKLEABLE`, `RESULT THRACKLEABLE`, `RESULT COUNT` or
  `RESULT TIMEOUT`, with the number of complete planar systems found, the number of planarity tests and the running
  time.

## Reproducing

The scripts expect one working directory that contains `thr2` (or the binaries in `bin/`), the Python scripts in
`src/`, and the directories `graphs/`, `sys/` and `logs/`:

```
mkdir work && cp src/* work/ && cp -r graphs sys work/ && mkdir work/logs && cd work
gcc -O2 -o thr2 thr2.c lr.c
xz -dk sys/DB681r_states10_sym.txt.xz sys/T337s_C10.sys.xz sys/T337s_states10.txt.xz
```

The commands below are the ones that produced the files in this repository. Rerunning the steps that produce graphs,
filter lists and state files gives identical files; the logs of the searches record their counters and running times.

**Counts and small graphs.** `./thr2 graphs/C6.txt --count` and so on for C3,...,C8 (`logs/calib/cycles_count.log`).
`bash run_union.sh graphs/G.txt NAME [MAXSEC]` prepares the graph G (edge order, orientations, and filters for all its
cycles of length 5 to 8) and runs the search with a time limit of MAXSEC seconds (default 500). Its runs for the 14
classes of Lemma 3.2 and for DB(6,8,-3) are logged in `logs/union_results.txt`, those for the remaining classes of
Lemma 3.4 in `logs/calib/union66_results.log`, and those for DB(5,5,-2), DB(5,6,-2) and the two classes of Lemma 4.3
that contain DB(5,5,-2) in `logs/calib/u610_results.log`. The enumerations are `python3 -I unions.py`,
`python3 -I unions66.py edge`, `python3 -I unions66.py vertex` and `python3 -I unions610.py 6 5 4 3`;
`python3 -I unions610_check.py 6 5 4 3`, which shares no code with `unions610.py`, checks the last. They write the
graphs of the remaining classes to `graphs/` and print the counts.

**Input graphs.**
```
for spec in "6 6 -1" "6 6 0" "6 8 -3" "6 8 -2" "6 8 -1" "6 10 -3"; do set -- $spec; python3 -I gen_db.py $1 $2 $3 > graphs/DB_$1_$2_$3.txt; done
awk 'NR==7 {print $2, $1; next} {print}' graphs/DB_6_8_-1.txt > graphs/DB_6_8_-1r.txt
G=graphs/DB_6_8_-2.txt;  for K in 7 8 9;    do python3 -I make_sub.py $G $(seq -s, 0 $((K-1))) > graphs/DB682_prefix$K.txt; done
G=graphs/DB_6_8_-1r.txt; for K in 7 8 9 10; do python3 -I make_sub.py $G $(seq -s, 0 $((K-1))) > graphs/DB681r_prefix$K.txt; done
```
The awk line reverses the orientation of edge 5. The search for DB(6,10,-3) uses the listing `graphs/T337s.txt`, in
which the three paths from vertex 0 to vertex 3 are 0,1,2,3 and 0,4,5,3 (edges 0 to 5, the 6-cycle) and
0,6,7,...,11,3 (edges 6 to 12), each edge oriented along its path from 0 to 3. In each of `graphs/T337s.txt`,
`graphs/DB_6_10_-3.txt` and `graphs/u610_3_4.txt` (the class of Lemma 4.3), two vertices have degree 3 and are joined by
three paths of lengths 3, 3 and 7; `logs/db6103/iso_T337s.log` records the same check made by a program that is not
included. Its subgraphs:
```
G=graphs/T337s.txt
python3 -I make_sub.py $G 0,1,2,6,7,8,9,10,11,12 > graphs/sub_T337s_C10A.txt
python3 -I make_sub.py $G 3,4,5,6,7,8,9,10,11,12 > graphs/sub_T337s_C10B.txt
for K in 9 10; do python3 -I make_sub.py $G $(seq -s, 0 $((K-1))) > graphs/T337s_prefix$K.txt; done
for K in 6 7; do python3 -I make_sub.py graphs/sub_T337s_C10A.txt $(seq -s, 0 $((K-1))) > graphs/T337s_C10A_prefix$K.txt; done
for K in 6 7; do python3 -I make_sub.py graphs/C10.txt $(seq -s, 0 $((K-1))) > graphs/C10_prefix$K.txt; done
```
The two 10-cycles give identical files `sub_T337s_C10A.txt` and `sub_T337s_C10B.txt`, so one list of systems serves as
filter for both. `graphs/C10.txt` and `graphs/C9.txt` are the cycles with edge i oriented from vertex i to vertex i+1.

**Filters.**
```
G=graphs/DB_6_8_-2.txt
python3 -I make_sub.py $G 0,1,6,7,8,9,10,11 > graphs/sub_DB682_C8.txt
python3 -I make_sub.py $G 0,1,6,7,8,9,10,11,2 > graphs/sub_DB682_H2.txt
python3 -I make_sub.py $G 0,1,6,7,8,9,10,11,5 > graphs/sub_DB682_H5.txt
./thr2 graphs/sub_DB682_C8.txt --dump sys/DB682_C8.sys
./thr2 graphs/sub_DB682_H2.txt --dump sys/DB682_H2.sys --filter sys/DB682_C8.sys=0,1,2,3,4,5,6,7
./thr2 graphs/sub_DB682_H5.txt --dump sys/DB682_H5.sys --filter sys/DB682_C8.sys=0,1,2,3,4,5,6,7
G=graphs/DB_6_8_-1.txt
python3 -I make_sub.py $G 0,6,7,8,9,10,11,12 > graphs/sub_DB681_C8.txt
python3 -I make_sub.py $G 0,6,7,8,9,10,11,12,1 > graphs/sub_DB681_Ha.txt
./thr2 graphs/sub_DB681_C8.txt --dump sys/DB681_C8.sys
./thr2 graphs/sub_DB681_Ha.txt --dump sys/DB681_Ha.sys --filter sys/DB681_C8.sys=0,1,2,3,4,5,6,7
G=graphs/DB_6_8_-1r.txt
python3 -I make_sub.py $G 0,6,7,8,9,10,11,12,5 > graphs/sub_DB681r_Hb.txt
./thr2 graphs/sub_DB681r_Hb.txt --dump sys/DB681r_Hb.sys --filter sys/DB681_C8.sys=0,1,2,3,4,5,6,7
```
C8 has 2,544 complete planar systems; each of the four graphs C8 plus a pendant edge has 60,196.

**DB(6,8,-2).** The states on the first nine edges (26,550 states):
```
./thr2 graphs/DB682_prefix9.txt --dump sys/DB682_states9.txt --filter sys/DB682_C8.sys=0,1,6,7,8,x,x,x --filter sys/DB682_H2.sys=0,1,6,7,8,x,x,x,2 --filter sys/DB682_H5.sys=0,1,6,7,8,x,x,x,5
```
Then `bash launch_db682.sh` runs 96 parts (`--states sys/DB682_states9.txt --slice i/96`) with the binary `thr2_static`.
All 96 logs in `logs/db682/` end with `RESULT NOT_THRACKLEABLE`.

**DB(6,8,-1).** The states on the first ten edges (1,215,372 states, about 450 s on one core):
```
./thr2 graphs/DB681r_prefix10.txt --dump sys/DB681r_states10.txt --filter sys/DB681_C8.sys=0,6,7,8,9,x,x,x --filter sys/DB681_Ha.sys=0,6,7,8,9,x,x,x,1 --filter sys/DB681r_Hb.sys=0,6,7,8,9,x,x,x,5
```
The sha256 of the output is 75c618cd134671e32a8da79fcd386b8927c07a4b272a1400999cbde9217818e6; it is recorded in
`sys/DB681r_states10_full.sha256`. The symmetry reduction keeps 694,211 states. Decompressed, `sys/DB681r_states10_sym.txt.xz` is this list; its sha256 is
b85af604a8812b0855478d3f77b751f7413170a384d6263508d0280c1fde90d0. It was made by
```
python3 -I sym_states.py graphs/DB_6_8_-1r.txt sys/DB681r_states10.txt 1,0,5,4,3,2,11,10,9,8,7,6 sys/DB681r_states10_sym.txt
```
The last argument is the automorphism sigma = (0 1)(2 5)(3 4)(6 11)(7 10)(8 9) as a vertex map. The script prints the
edge set R = {e0,...,e5,e9} that it computes and keeps a state if its restriction to R is lexicographically at most the
image of that restriction under sigma. Then
```
python3 -I split_shares.py sys/DB681r_states10_sym.txt 6 sys/share
bash launch_full.sh K        # for K = 0,...,5; each runs 96 parts with --states sys/share_K.txt --slice i/96
```
`launch_full.sh` uses the binary `thr2_static_v2`. All 576 logs in `logs/db681_full/` end with
`RESULT NOT_THRACKLEABLE`; `logs/RESULTS_DB681.txt` sums them (207,380,593,775 planarity tests). The full run takes about
7.8 million thread-seconds. The timing sample in `logs/db681_sample/` (192 of the states on the first nine edges) is not
used in the paper.

**DB(6,10,-3).** All steps used the binary `thr2_static_v3`. Its copies on the run machines were hashed when they were
uploaded, and they had the sha256 prefix c3e4e74a1d3d9145 of `bin/thr2_static_v3`; this is recorded in the notes of
the runs, not in a log of this repository. The steps ran on six machines with 96 hardware threads each, called m1, ...,
m6 here, and `logs/db6103/mK/` holds the logs and task lists of machine mK.

The filter list. `bash launch_c10t.sh` lists the 229 states on the first six edges of the 10-cycle
(`sys/C10t_states6.txt`) and runs 96 parts:
```
./thr2_static_v3 graphs/T337s_C10A_prefix6.txt --dump sys/C10t_states6.txt
./thr2_static_v3 graphs/sub_T337s_C10A.txt --states sys/C10t_states6.txt --slice i/96 --dump sys/c10t/C10t_s$i.sys    # i = 0,...,95
```
Parts 8, 9, 24, 25, 28, 83 and 85 had not finished when `bash launch_c10redo.sh` took their 19 states, extended them
by the seventh edge to 537 states and ran these in 88 parts; the output of the seven original parts was not used. The
files are `sys/C10t_redo.info`, `sys/C10t_redo_states6.txt` and `sys/C10t_redo_states7.txt`. `bash t337_prep2.sh` then merged the outputs with `concat_dump.py` into the order of a single
unsplit run and listed the states on the first nine edges of DB(6,10,-3) (see below). The merged list has 6,059,712
systems; its sha256 is e9279cbcc2f3f2642200c641dd4e8c38f6a11441ac82dee1b05773a6b5ed30dc, and it is the file
`sys/T337s_C10.sys.xz` after decompression. `logs/db6103/m2/merge_template.log` records a second run of the merge with
the same sha256, and the logs of the parts are `logs/db6103/m2/c10t_*` and `c10r_*`.

The second computation of the list used `graphs/C10.txt`, in which every edge is oriented around the cycle.
`bash launch_t337_exp.sh` ran it in 94 parts over the 229 states on the first six edges of this cycle
(`sys/C10_states6.txt`), and `bash launch_c10predo.sh 40` redid its part 11 in 40 parts at the seventh edge. Its
merged list, which is not archived, also has 6,059,712 systems (`logs/db6103/m1/c10p_merge.log`). The isomorphism
between the two cycles reverses seven edges; `python3 -I c10_iso_check.py PLAIN TEMPLATE` found that it maps this list
onto `sys/T337s_C10.sys` (`logs/db6103/m1/c10_iso_check.log`). `launch_t337_exp.sh` also counted the 72,916 complete
planar systems of C9, logged in `logs/db6103/m1/c9.log`.

The states. In `t337_prep2.sh`,
```
./thr2_static_v3 graphs/T337s_prefix9.txt --dump sys/T337s_states9.txt --filter sys/T337s_C10.sys=0,1,2,6,7,8,x,x,x,x --filter sys/T337s_C10.sys=3,4,5,6,7,8,x,x,x,x
```
lists the 32,626 states on the first nine edges (`logs/db6103/m2/t337_states9.log`). Their extensions by the tenth edge
were listed in 120 parts, 60 on each of m1 and m2 (`bash launch_t337_p10.sh FIRST LAST 120`):
```
./thr2_static_v3 graphs/T337s_prefix10.txt --filter sys/T337s_C10.sys=0,1,2,6,7,8,9,x,x,x --filter sys/T337s_C10.sys=3,4,5,6,7,8,9,x,x,x --states sys/T337s_states9.txt --slice i/120 --dump sys/p10/T337s_p10_s$i.sys
```
and merged with `concat_dump.py` into the order of a single run (`logs/db6103/m2/p10_merge.log`). The merged list has
1,211,878 states. Decompressed, `sys/T337s_states10.txt.xz` is this list; its sha256 is
2afc9f2ed69d393e9d2202e0000b9de160f741ac75b703ecf6decdc7c333ccc6.

The search. The 1,211,878 states were split into 4,096 parts, each run as
```
./thr2_static_v3 graphs/T337s.txt --filter sys/T337s_C10.sys=0,1,2,6,7,8,9,10,11,12 --filter sys/T337s_C10.sys=3,4,5,6,7,8,9,10,11,12 --states sys/T337s_states10.txt --slice i/4096
```
by `qworker.sh`, which works through a list of parts with a fixed number of parts running at a time: 64 on m1 and m2,
and 96 on m3, ..., m6. The lists are `logs/db6103/mK/tasks.txt`. Near the end, `rebalance.sh` moved the last 60 parts
not yet started on each of m1 and m2 to m3 and m6. The task lists for the move are `tasks_moved.txt` on m1 and m2,
`tasks_from_m1.txt` on m3 and `tasks_from_m2.txt` on m6. `qworker2.sh` then ran the remaining lists: `tasks_r1.txt` on
m1 and m2, and the moved parts on m3 and m6. Each of the 4,096
logs `logs/db6103/mK/q_s<i>.log` ends with `RESULT NOT_THRACKLEABLE` and reports `states: total seen 1211878` and the
number of states run in its part; these numbers add up to 1,211,878. Together the parts made 83,401,645,992 planarity
tests in 2,439,459 thread-seconds, and the longest took 1,013 s.

Not used in the paper: `logs/db6103/m1/aborted_t337f/` and `logs/db6103/m2/aborted_t337f/`, a first attempt over the
32,626 states on the first nine edges in 80 parts (`launch_t337_full.sh`), stopped after 36 minutes because its parts kept
no record of the states already completed; `logs/db6103/m2/t337p_s*.log`, a timing sample with a provisional filter list
(`t337_prov.sh`, `t337_meas3.sh`); and `logs/db6103/m1/t337_unf.log`, a run without filters of
`graphs/r_DB_6_10_-3.txt`, stopped at its time limit of 1,800 s.

**Planarity comparison.** `validation/` contains the inputs, outputs and commands (see `docs/BUILD.md`, Section 3). The
inputs are 5,000 random graphs, made with `python3 -I gen_val.py 1 3000` and `python3 -I gen_val.py 7 2000 220`, and
2,605 augmented graphs sampled from the search for DB(6,8,-1). Each was tested by `lr_cli`, built from
`validation/lr_cli.c` with `src/lr.c`, and by `python3 -I dmp.py`; the two outputs are identical for each input file.

## The second implementation

`independent/` contains the second implementation of the search described in Section 5.4 of the paper, separate
implementations of the enumerations of Lemmas 3.2, 3.4 and 4.3 and of the discharging arithmetic, and the outputs of
their runs. It was written from a description of the method, without reference to the programs in `src/`. It uses the
Edge Addition Planarity Suite, which is not included; `independent/README.md` gives its version and licence, and the
build and run commands.

With it we repeated all searches and enumerations of the paper, among them DB(5,5,-2), DB(5,6,-2) and DB(6,10,-3),
the classes of the unions of Lemma 4.3, and the discharging at 4/3. For DB(6,10,-3) it used the edge order of
`graphs/T337s.txt` and computed its own list of the systems of the 10-cycle. It found the same 6,059,712 systems of
the 10-cycle and the same 1,211,878 states on the first ten edges, and below these states it made the same number of
planarity tests, 83,401,645,992, as the run in `logs/db6103/`.

## Notes

- Some scripts and notes call the states on the first ten edges e0,...,e9 "level-9" states, after the index of the
  last edge, and the states on the first nine edges "level-8" states.
- The usage line of `src/thr2.c` lists an option `--first N`, which is not implemented.
- In `independent/`, a level-L state is a state on the first L edges.
- `logs/unions_C6C8.log` was produced for this release by running `src/unions.py`; the graph files it writes are
  identical to those in `graphs/`.
- The scripts for DB(6,10,-3) refer to the state files of the filter list as `sys/C10t_*` and `sys/C10_*`; these are in
  `sys/`, while the outputs of the parts (`sys/c10t/`, `sys/c10r/`, `sys/c10/`, `sys/c10pr/`, `sys/p10/`) are not
  archived.

## License

Apache License 2.0 (`LICENSE`; the same text is in `independent/LICENSE`).
