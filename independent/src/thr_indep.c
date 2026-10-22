/* thr_indep.c: a second implementation of the Fulek-Pach thrackleability search.
 *
 * Written from a description of the method (the specification of the first program, sections 2-5 and 8), Scoppetto,
 * arXiv:2610.17508 (section 3), and Fulek and Pach (2011), without reading the code of the first program.  Planarity
 * tests: the third-party Edge Addition Planarity Suite (gp_Embed).
 *
 * Model.  Edges are oriented (file order = search order).  N(e) = edges with no endpoint in common with e.  A crossing
 * system gives for each edge e a linear order row[e] of N(e) (order of the crossings from the tail).  G'(G, Pi):
 * the vertices of G, a vertex X(e,f) per crossing pair, a subdivision vertex between consecutive crossings of an edge;
 * edge e is the path tail, X1, s, X2, s, ..., Xt, head; for X = X(e,f) with neighbours a1, a2 along e and b1, b2 along f
 * the 4-cycle a1 b1 a2 b2.  G is thrackleable iff some Pi makes G'(G, Pi) planar (Fulek-Pach).
 * Search.  Edge k is traced from its tail: each step picks an earlier edge f in N(k) not yet crossed by k and a gap of
 * row[f] where k is inserted; f is appended to row[k].  After every step the partial G' (edges < k complete, edge k up to
 * its last crossing, diamonds only on existing arms) is tested; when k has crossed every earlier edge of N(k), its last
 * segment is added and the G' of edges 0..k is tested.  The partial G' is a minor of the G' of every completion, so a
 * nonplanar partial G' prunes soundly; every complete Pi lies on exactly one branch (completeness).
 * Filters (optional).  For a subgraph H (same vertex ids, a subset of the edges, same orientations) with the FULL list of
 * its complete planar systems (made by this program, --dumpall), a branch whose restriction to H extends to none of
 * them is pruned (a complete planar system of G restricts to one of H, by the same minor argument).
 *
 * Usage: thr_indep GRAPH [--decide] [--filter HFILE SYSFILE]... [--dump L OUT] [--states FILE --slice I N]
 *              [--dumpall OUT] [--gsample K OUT]
 *   GRAPH: "n m" then m lines "u v" (edge i oriented u -> v).   Output: one RESULT line.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include "graphLib.h"

#define MAXE 40
#define MAXR 40
#define MAXV 512
#define MAXF 16

static int n, m, eu[MAXE], ev[MAXE];
static int nonadj[MAXE][MAXE];
static int row[MAXE][MAXR], len[MAXE];
static long long ntests = 0, nplanar = 0, ncomplete = 0, nstates_dumped = 0;
static int decide = 0, found = 0;
static int dumpL = -1; static FILE *dumpf = NULL;
static FILE *allf = NULL;
static long long gsample = 0; static FILE *gsf = NULL;

/* ---------------------------------------------------------------- filters */
typedef struct {
    int h, nsys, W;
    int gof[MAXE];          /* H-edge -> G-edge */
    int hof[MAXE];          /* G-edge -> H-edge or -1 */
    uint64_t *B;            /* B[(e*h + x)*h + y] : systems with x before y on H-edge e */
    uint64_t *cur;          /* stack of consistent sets, one per search step */
    int sp;
} Filter;
static Filter F[MAXF]; static int nF = 0;

static uint64_t *Bp(Filter *f, int e, int x, int y) { return f->B + (size_t)((e * f->h + x) * f->h + y) * f->W; }

static void load_filter(const char *hfile, const char *sysfile) {
    if (nF >= MAXF) { fprintf(stderr, "too many filters\n"); exit(2); }
    Filter *f = &F[nF++];
    FILE *fp = fopen(hfile, "r"); int hn, hm;
    if (!fp || fscanf(fp, "%d %d", &hn, &hm) != 2) { fprintf(stderr, "bad filter graph %s\n", hfile); exit(2); }
    f->h = hm;
    for (int i = 0; i < MAXE; i++) f->hof[i] = -1;
    for (int i = 0; i < hm; i++) {
        int u, v; if (fscanf(fp, "%d %d", &u, &v) != 2) { fprintf(stderr, "bad filter edge\n"); exit(2); }
        int g = -1;
        for (int j = 0; j < m; j++) if (eu[j] == u && ev[j] == v) g = j;
        if (g < 0) { fprintf(stderr, "filter edge %d->%d is not an edge of G with this orientation\n", u, v); exit(2); }
        f->gof[i] = g; f->hof[g] = i;
    }
    fclose(fp);
    /* systems: one per line, rows of H-edges 0..h-1 separated by '|', partner ids = H-edge ids */
    fp = fopen(sysfile, "r"); if (!fp) { fprintf(stderr, "no %s\n", sysfile); exit(2); }
    char *line = NULL; size_t cap = 0; int ns = 0;
    while (getline(&line, &cap, fp) > 0) if (line[0] != '\n' && line[0] != '#') ns++;
    rewind(fp);
    f->nsys = ns; f->W = (ns + 63) / 64;
    f->B = calloc((size_t)hm * hm * hm * f->W, 8);
    f->cur = malloc((size_t)(MAXE * MAXR + 8) * f->W * 8);
    int s = 0;
    while (getline(&line, &cap, fp) > 0) {
        if (line[0] == '\n' || line[0] == '#') continue;
        int e = 0, r[MAXR], rl = 0; char *p = line;
        for (;;) {
            while (*p == ' ') p++;
            if (*p == '|' || *p == '\n' || *p == 0) {
                for (int a = 0; a < rl; a++) for (int b = a + 1; b < rl; b++) Bp(f, e, r[a], r[b])[s >> 6] |= 1ULL << (s & 63);
                if (*p != '|') break;
                e++; rl = 0; p++; continue;
            }
            r[rl++] = (int)strtol(p, &p, 10);
        }
        if (e != hm - 1) { fprintf(stderr, "bad system line %d in %s\n", s, sysfile); exit(2); }
        s++;
    }
    free(line); fclose(fp);
    for (int w = 0; w < f->W; w++) f->cur[w] = ~0ULL;
    if (ns % 64) f->cur[f->W - 1] = (1ULL << (ns % 64)) - 1;
    f->sp = 0;
    fprintf(stderr, "filter %s: %d edges, %d systems\n", sysfile, hm, ns);
}

static int and_into(Filter *f, uint64_t *dst, const uint64_t *src) {
    uint64_t any = 0;
    for (int w = 0; w < f->W; w++) { dst[w] &= src[w]; any |= dst[w]; }
    return any != 0;
}

/* push a new consistent set for the step "k crosses fe: k inserted at gap p of row[fe], fe appended to row[k]"
   (called BEFORE the rows are modified); returns 0 if some filter becomes empty (the push is done anyway) */
static int filters_step(int k, int fe, int p) {
    int ok = 1;
    for (int i = 0; i < nF; i++) {
        Filter *f = &F[i];
        uint64_t *src = f->cur + (size_t)f->sp * f->W, *dst = src + f->W;
        memcpy(dst, src, (size_t)f->W * 8); f->sp++;
        int hk = f->hof[k], hf = f->hof[fe];
        if (hk < 0 || hf < 0) continue;
        int a = -1, b = -1;
        for (int j = p - 1; j >= 0; j--) if (f->hof[row[fe][j]] >= 0) { a = f->hof[row[fe][j]]; break; }
        for (int j = p; j < len[fe]; j++) if (f->hof[row[fe][j]] >= 0) { b = f->hof[row[fe][j]]; break; }
        if (a >= 0 && !and_into(f, dst, Bp(f, hf, a, hk))) { ok = 0; continue; }
        if (b >= 0 && !and_into(f, dst, Bp(f, hf, hk, b))) { ok = 0; continue; }
        int y = -1;
        for (int j = len[k] - 1; j >= 0; j--) if (f->hof[row[k][j]] >= 0) { y = f->hof[row[k][j]]; break; }
        if (y >= 0 && !and_into(f, dst, Bp(f, hk, y, hf))) { ok = 0; continue; }
        for (int q = 0; q < k; q++) {
            if (q == fe || !nonadj[k][q] || f->hof[q] < 0) continue;
            int crossed = 0;
            for (int j = 0; j < len[k]; j++) if (row[k][j] == q) { crossed = 1; break; }
            if (!crossed && !and_into(f, dst, Bp(f, hk, hf, f->hof[q]))) { ok = 0; break; }
        }
    }
    return ok;
}
static void filters_pop(void) { for (int i = 0; i < nF; i++) F[i].sp--; }

/* recompute the consistent sets from complete rows of edges 0..L-1 (state resume) */
static int filters_reset(int L) {
    int ok = 1;
    for (int i = 0; i < nF; i++) {
        Filter *f = &F[i]; f->sp = 0;
        uint64_t *c = f->cur;
        for (int w = 0; w < f->W; w++) c[w] = ~0ULL;
        if (f->nsys % 64) c[f->W - 1] = (1ULL << (f->nsys % 64)) - 1;
        for (int e = 0; e < L; e++) {
            int he = f->hof[e]; if (he < 0) continue;
            int prev = -1;
            for (int j = 0; j < len[e]; j++) {
                int hx = f->hof[row[e][j]]; if (hx < 0) continue;
                if (prev >= 0 && !and_into(f, c, Bp(f, he, prev, hx))) ok = 0;
                prev = hx;
            }
        }
    }
    return ok;
}

/* ---------------------------------------------------------------- G' and planarity */
static int eA[4 * MAXV], eB[4 * MAXV], ne;
static uint64_t adjbits[MAXV][MAXV / 64];
static int path[MAXE][2 * MAXR + 2];

static void add_edge(int a, int b) {
    if (a == b) { fprintf(stderr, "self loop in G'\n"); exit(3); }
    if (adjbits[a][b >> 6] & (1ULL << (b & 63))) return;
    adjbits[a][b >> 6] |= 1ULL << (b & 63); adjbits[b][a >> 6] |= 1ULL << (a & 63);
    eA[ne] = a; eB[ne] = b; ne++;
}

/* G' of: edges 0..k-1 complete, edge k traced up to its row (closed: also its last segment); returns planarity */
static int test_gprime(int k, int closed) {
    int nv = n;
    static int xid[MAXE][MAXE];
    for (int e = 0; e <= k; e++) for (int j = 0; j < len[e]; j++) xid[e][row[e][j]] = -1;
    for (int e = 0; e <= k; e++)
        for (int j = 0; j < len[e]; j++) {
            int f = row[e][j];
            if (xid[e][f] < 0) { xid[e][f] = xid[f][e] = nv++; }
        }
    /* paths */
    int plen[MAXE];
    for (int e = 0; e <= k; e++) {
        int c = (e < k) || closed, L = 0;
        path[e][L++] = eu[e];
        for (int j = 0; j < len[e]; j++) {
            if (j > 0) path[e][L++] = nv++;               /* subdivision vertex */
            path[e][L++] = xid[e][row[e][j]];
        }
        if (c) path[e][L++] = ev[e];
        plen[e] = L;
    }
    if (nv > MAXV) { fprintf(stderr, "G' too large\n"); exit(3); }
    for (int v = 0; v < nv; v++) memset(adjbits[v], 0, ((nv + 63) / 64) * 8);
    ne = 0;
    for (int e = 0; e <= k; e++) for (int i = 0; i + 1 < plen[e]; i++) add_edge(path[e][i], path[e][i + 1]);
    /* diamonds */
    for (int e = 0; e <= k; e++)
        for (int j = 0; j < len[e]; j++) {
            int f = row[e][j];
            if (f < e) continue;                          /* each crossing once */
            int jf = -1;
            for (int t = 0; t < len[f]; t++) if (row[f][t] == e) { jf = t; break; }
            if (jf < 0) { fprintf(stderr, "asymmetric rows %d %d\n", e, f); exit(3); }
            int ie = 1 + 2 * j, iff = 1 + 2 * jf;         /* index of X in path[e], path[f] */
            int a1 = path[e][ie - 1], a2 = (ie + 1 < plen[e]) ? path[e][ie + 1] : -1;
            int b1 = path[f][iff - 1], b2 = (iff + 1 < plen[f]) ? path[f][iff + 1] : -1;
            add_edge(a1, b1);
            if (a2 >= 0) add_edge(b1, a2);
            if (a2 >= 0 && b2 >= 0) add_edge(a2, b2);
            if (b2 >= 0) add_edge(b2, a1);
        }
    graphP g = gp_New();
    if (gp_EnsureVertexCapacity(g, nv) != OK || gp_EnsureEdgeCapacity(g, ne > 0 ? ne : 1) != OK) { fprintf(stderr, "eaps alloc\n"); exit(3); }
    for (int i = 0; i < ne; i++) if (gp_AddEdge(g, eA[i] + 1, 0, eB[i] + 1, 0) != OK) { fprintf(stderr, "eaps add\n"); exit(3); }
    int r = gp_Embed(g, EMBEDFLAGS_PLANAR);
    gp_Free(&g);
    ntests++;
    if (r != OK && r != NONEMBEDDABLE) { fprintf(stderr, "eaps embed error %d\n", r); exit(3); }
    int planar = (r == OK);
    if (planar) nplanar++;
    if (gsf && gsample > 0 && (ntests % gsample) == 0) {
        fprintf(gsf, "%d %d %d", planar, nv, ne);
        for (int i = 0; i < ne; i++) fprintf(gsf, " %d,%d", eA[i], eB[i]);
        fprintf(gsf, "\n");
    }
    return planar;
}

/* ---------------------------------------------------------------- search */
static void write_rows(FILE *fp, int upto) {
    for (int e = 0; e < upto; e++) {
        if (e) fputs(" |", fp);
        for (int j = 0; j < len[e]; j++) fprintf(fp, " %d", row[e][j]);
    }
    fputc('\n', fp);
}

static void search(int k);

static void trace(int k, uint64_t todo) {
    if (found) return;
    if (!todo) {                                          /* all earlier partners crossed: close edge k */
        if (test_gprime(k, 1)) search(k + 1);
        return;
    }
    for (int fe = 0; fe < k && !found; fe++) {
        if (!(todo & (1ULL << fe))) continue;
        for (int p = 0; p <= len[fe] && !found; p++) {
            int fok = filters_step(k, fe, p);
            if (fok) {
                memmove(&row[fe][p + 1], &row[fe][p], (len[fe] - p) * sizeof(int)); row[fe][p] = k; len[fe]++;
                row[k][len[k]++] = fe;
                if (test_gprime(k, 0)) trace(k, todo & ~(1ULL << fe));
                len[k]--;
                len[fe]--; memmove(&row[fe][p], &row[fe][p + 1], (len[fe] - p) * sizeof(int));
            }
            filters_pop();
        }
    }
}

static void search(int k) {
    if (found) return;
    if (k == dumpL) { write_rows(dumpf, k); nstates_dumped++; return; }
    if (k == m) {
        ncomplete++;
        if (allf) write_rows(allf, m);
        if (decide) { found = 1; fprintf(stdout, "THRACKLE SYSTEM:"); write_rows(stdout, m); }
        return;
    }
    uint64_t todo = 0;
    for (int f = 0; f < k; f++) if (nonadj[k][f]) todo |= 1ULL << f;
    len[k] = 0;
    trace(k, todo);
}

static int parse_rows(char *line, int upto) {
    char *p = line; int e = 0; len[0] = 0;
    for (;;) {
        while (*p == ' ') p++;
        if (*p == '|') { e++; if (e >= upto) return 0; len[e] = 0; p++; continue; }
        if (*p == '\n' || *p == 0) break;
        row[e][len[e]++] = (int)strtol(p, &p, 10);
    }
    return e == upto - 1;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: see source\n"); return 2; }
    FILE *fp = fopen(argv[1], "r");
    if (!fp || fscanf(fp, "%d %d", &n, &m) != 2 || m > MAXE || m > 63) { fprintf(stderr, "bad graph\n"); return 2; }
    for (int i = 0; i < m; i++) if (fscanf(fp, "%d %d", &eu[i], &ev[i]) != 2) { fprintf(stderr, "bad edge\n"); return 2; }
    fclose(fp);
    for (int i = 0; i < m; i++) for (int j = 0; j < m; j++)
        nonadj[i][j] = (i != j) && eu[i] != eu[j] && eu[i] != ev[j] && ev[i] != eu[j] && ev[i] != ev[j];
    const char *states = NULL; int slice = 0, nslice = 1;
    for (int a = 2; a < argc; a++) {
        if (!strcmp(argv[a], "--decide")) decide = 1;
        else if (!strcmp(argv[a], "--filter")) { load_filter(argv[a + 1], argv[a + 2]); a += 2; }
        else if (!strcmp(argv[a], "--dump")) { dumpL = atoi(argv[a + 1]); dumpf = fopen(argv[a + 2], "w"); a += 2; }
        else if (!strcmp(argv[a], "--dumpall")) { allf = fopen(argv[a + 1], "w"); a += 1; }
        else if (!strcmp(argv[a], "--states")) { states = argv[a + 1]; a += 1; }
        else if (!strcmp(argv[a], "--slice")) { slice = atoi(argv[a + 1]); nslice = atoi(argv[a + 2]); a += 2; }
        else if (!strcmp(argv[a], "--gsample")) { gsample = atoll(argv[a + 1]); gsf = fopen(argv[a + 2], "w"); a += 2; }
        else { fprintf(stderr, "unknown option %s\n", argv[a]); return 2; }
    }
    clock_t t0 = clock();
    long long nres = 0, nskip = 0;
    if (!states) {
        if (filters_reset(0)) search(0);
    } else {
        FILE *sf = fopen(states, "r"); char *line = NULL; size_t cap = 0; long long idx = 0; int L = -1;
        while (getline(&line, &cap, sf) > 0 && !found) {
            if (L < 0) { L = 1; for (char *c = line; *c; c++) if (*c == '|') L++; }
            if (idx++ % nslice != slice) continue;
            if (!parse_rows(line, L)) { fprintf(stderr, "bad state line %lld\n", idx - 1); return 2; }
            nres++;
            if (filters_reset(L)) search(L); else nskip++;
        }
        free(line); fclose(sf);
    }
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("RESULT graph=%s m=%d complete_planar=%lld %s tests=%lld planar_tests=%lld dumped=%lld resumed=%lld filtered_at_resume=%lld secs=%.1f\n",
           argv[1], m, ncomplete, decide ? (found ? "THRACKLEABLE" : "NOT_THRACKLEABLE") : "count", ntests, nplanar,
           nstates_dumped, nres, nskip, secs);
    if (dumpf) fclose(dumpf);
    if (allf) fclose(allf);
    if (gsf) fclose(gsf);
    return 0;
}
