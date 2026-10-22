/* thr2: thrackleability search with subgraph-system filters (clean-room).
   Model (Fulek-Pach reduction): G is thrackleable iff for some crossing orders pi_e (order along the directed edge e
   of its crossings with the edges not incident to e) the augmented graph G' is planar. G' has a vertex per crossing,
   one subdivision vertex on every segment between two consecutive crossings, and a 4-cycle through the four neighbours
   of each crossing vertex alternating between the two edges (forces a proper crossing).
   Search: edges are added in input order; the new edge is traced from its tail, choosing its next crossing (partner f
   among earlier non-incident edges, and the gap of pi_f where it lands). After every choice the partial G' (new edge
   drawn only up to its last crossing, its last diamond only on existing arms) is tested; it is a minor of the G' of
   every completion, so nonplanar prunes. A complete planar system restricts to a complete planar system of every
   subgraph H (sub-drawing), so a filter (the full list of planar complete systems of a subgraph H, computed by --dump)
   prunes every partial system whose restriction to H matches none of them (bitsets of still-possible systems).
   Usage: thr2 GRAPH [--count] [--dump FILE] [--filter SYSFILE=g0,g1,...]... [--maxsec S] [--first N]
   GRAPH: "n m" then m lines "u v" (edge order = addition order, u -> v). SYSFILE: written by --dump on the subgraph H
   (header "H h nH", h lines "u v", then one line per system: rows of H-edge indices separated by '|'); H-edge i is G-edge
   g_i (orientations are checked through a consistent vertex map). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include "lr.h"

#define MAXE 40
#define MAXF 8
#define MAXD 128
static int n, m, EU[MAXE], EV[MAXE];
static int nonadj[MAXE][MAXE];
static int row[MAXE][MAXE], len[MAXE];
static int used[MAXE][MAXE];
static long long tests = 0, planar_hits = 0, complete_found = 0, fprunes = 0;
static int count_mode = 0;
static FILE *dumpf = NULL;
static double t0, maxsec = 1e30;
static int timed_out = 0;
static long long level_tests[MAXE];
static long long choices = 0;

static double now(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + 1e-9 * ts.tv_nsec; }

/* ---------- G' construction and planarity ---------- */
static int GU[LR_MAXM], GV[LR_MAXM], gm, gn;
static int xid[MAXE][MAXE];
#define HSIZE 32768
static int hkey[HSIZE]; static long long hst[HSIZE]; static long long hstamp = 0;
static void add_edge(int a, int b) {
    if (a < 0 || b < 0 || a == b) return;
    if (a > b) { int t = a; a = b; b = t; }
    int key = a * LR_MAXN + b;
    unsigned h = ((unsigned)key * 2654435761u) & (HSIZE - 1);
    while (hst[h] == hstamp) { if (hkey[h] == key) return; h = (h + 1) & (HSIZE - 1); }
    hst[h] = hstamp; hkey[h] = key;
    GU[gm] = a; GV[gm] = b; gm++;
}
static int seqv[MAXE][2 * MAXE + 3];
static int cr_prev[MAXE][MAXE], cr_next[MAXE][MAXE];

static int build_and_test(int k, int closed) {
    hstamp++; gm = 0; gn = n;
    int ne = k + 1;
    for (int e = 0; e < ne; e++)
        for (int t = 0; t < len[e]; t++) xid[e][row[e][t]] = -1;
    for (int e = 0; e < ne; e++)
        for (int t = 0; t < len[e]; t++) {
            int f = row[e][t];
            if (xid[e][f] < 0) { xid[e][f] = xid[f][e] = gn++; }
        }
    for (int e = 0; e < ne; e++) {
        int L = 0;
        seqv[e][L++] = EU[e];
        for (int t = 0; t < len[e]; t++) {
            if (t > 0) seqv[e][L++] = gn++;
            seqv[e][L++] = xid[e][row[e][t]];
        }
        if (e < k || closed) seqv[e][L++] = EV[e];
        for (int i = 0; i + 1 < L; i++) add_edge(seqv[e][i], seqv[e][i + 1]);
        for (int t = 0; t < len[e]; t++) {
            int pos = 2 * t + 1, f = row[e][t];
            cr_prev[e][f] = seqv[e][pos - 1];
            cr_next[e][f] = (pos + 1 < L) ? seqv[e][pos + 1] : -1;
        }
    }
    for (int e = 0; e < ne; e++)
        for (int t = 0; t < len[e]; t++) {
            int f = row[e][t];
            if (f < e) continue;
            int pe = cr_prev[e][f], nee = cr_next[e][f], pf = cr_prev[f][e], nf = cr_next[f][e];
            if (pe >= 0 && pf >= 0) add_edge(pe, pf);
            if (pf >= 0 && nee >= 0) add_edge(pf, nee);
            if (nee >= 0 && nf >= 0) add_edge(nee, nf);
            if (nf >= 0 && pe >= 0) add_edge(nf, pe);
        }
    tests++;
    int r = lr_planar(gn, gm, GU, GV);
    if (r < 0) { fprintf(stderr, "LR capacity exceeded\n"); exit(2); }
    if (r) planar_hits++;
    return r;
}

/* ---------- filters ---------- */
typedef struct {
    int h, nsys, W;
    int hmap[MAXE];          /* H-edge -> G-edge */
    int inH[MAXE];           /* G-edge -> H-edge or -1 */
    uint64_t *prec;          /* [(e*h + x)*h + y][W]: systems where on H-edge e, x precedes y */
    uint64_t *cur;           /* [MAXD][W] */
    char name[256];
} Filter;
static Filter FL[MAXF]; static int nfl = 0;
static int D = 0;            /* current depth (number of crossings placed) */

static uint64_t *P_(Filter *F, int e, int x, int y) { return F->prec + ((size_t)((e * F->h + x) * F->h + y)) * F->W; }

static void load_filter(const char *spec) {
    Filter *F = &FL[nfl++];
    char buf[4096]; strncpy(buf, spec, sizeof buf - 1); buf[sizeof buf - 1] = 0;
    char *eq = strchr(buf, '=');
    if (!eq) { fprintf(stderr, "bad filter spec\n"); exit(1); }
    *eq = 0; strncpy(F->name, buf, 255);
    int h = 0;
    for (char *tok = strtok(eq + 1, ","); tok; tok = strtok(NULL, ",")) F->hmap[h++] = atoi(tok);
    FILE *fp = fopen(buf, "r");
    if (!fp) { fprintf(stderr, "cannot open %s\n", buf); exit(1); }
    int hh, nH;
    if (fscanf(fp, " H %d %d", &hh, &nH) != 2 || hh != h) { fprintf(stderr, "filter header mismatch %s\n", buf); exit(1); }
    int HU[MAXE], HV[MAXE], vmap[64];
    for (int i = 0; i < 64; i++) vmap[i] = -1;
    for (int i = 0; i < h; i++) {
        if (fscanf(fp, "%d %d", &HU[i], &HV[i]) != 2) exit(1);
        int g = F->hmap[i];
        int a[2] = {HU[i], HV[i]}, b[2] = {EU[g], EV[g]};
        for (int s = 0; s < 2; s++) {
            if (vmap[a[s]] < 0) vmap[a[s]] = b[s];
            else if (vmap[a[s]] != b[s]) { fprintf(stderr, "filter %s: inconsistent vertex/orientation map\n", buf); exit(1); }
        }
    }
    for (int i = 0; i < nH; i++) for (int j = i + 1; j < nH; j++)
        if (vmap[i] >= 0 && vmap[i] == vmap[j]) { fprintf(stderr, "filter %s: vertex map not injective\n", buf); exit(1); }
    for (int g = 0; g < m; g++) F->inH[g] = -1;
    for (int i = 0; i < h; i++) F->inH[F->hmap[i]] = i;
    /* read systems */
    int cap = 1024, ns = 0;
    int *R = malloc(sizeof(int) * (size_t)cap * h * h);   /* rank[s][e][x] */
    char line[1 << 16];
    if (!fgets(line, sizeof line, fp)) exit(1);   /* rest of header line */
    while (fgets(line, sizeof line, fp)) {
        if (line[0] == '\n' || line[0] == 0) continue;
        if (ns == cap) { cap *= 2; R = realloc(R, sizeof(int) * (size_t)cap * h * h); }
        int *rk = R + (size_t)ns * h * h;
        for (int i = 0; i < h * h; i++) rk[i] = -1;
        char *p = line; int e = 0, pos = 0;
        while (*p && *p != '\n') {
            if (*p == '|') { e++; pos = 0; p++; continue; }
            if (*p == ' ') { p++; continue; }
            int x = (int)strtol(p, &p, 10);
            rk[e * h + x] = pos++;
        }
        if (e != h - 1) { fprintf(stderr, "filter %s: bad system line %d\n", buf, ns); exit(1); }
        ns++;
    }
    fclose(fp);
    /* check partner sets equal G-nonadjacency */
    for (int s = 0; s < ns; s++)
        for (int e = 0; e < h; e++)
            for (int x = 0; x < h; x++) {
                int want = nonadj[F->hmap[e]][F->hmap[x]];
                int have = R[(size_t)s * h * h + e * h + x] >= 0;
                if (want != have) { fprintf(stderr, "filter %s: partner set mismatch\n", buf); exit(1); }
            }
    F->h = h; F->nsys = ns; F->W = (ns + 63) / 64;
    F->prec = calloc((size_t)h * h * h * F->W, sizeof(uint64_t));
    for (int s = 0; s < ns; s++) {
        int *rk = R + (size_t)s * h * h;
        for (int e = 0; e < h; e++)
            for (int x = 0; x < h; x++) {
                if (rk[e * h + x] < 0) continue;
                for (int y = 0; y < h; y++)
                    if (rk[e * h + y] >= 0 && rk[e * h + x] < rk[e * h + y]) P_(F, e, x, y)[s >> 6] |= 1ULL << (s & 63);
            }
    }
    F->cur = calloc((size_t)MAXD * F->W, sizeof(uint64_t));
    for (int s = 0; s < ns; s++) F->cur[s >> 6] |= 1ULL << (s & 63);
    free(R);
    fprintf(stderr, "filter %s: h=%d systems=%d\n", F->name, h, ns);
}

/* apply constraints of crossing (k crosses f; k at gap p of row[f]; f at index t of row[k]) to depth D+1 */
static int filters_step(int k, int f, int p, int t) {
    for (int i = 0; i < nfl; i++) {
        Filter *F = &FL[i];
        uint64_t *src = F->cur + (size_t)D * F->W, *dst = F->cur + (size_t)(D + 1) * F->W;
        memcpy(dst, src, sizeof(uint64_t) * F->W);
        int a = F->inH[k], b = F->inH[f];
        if (a < 0 || b < 0) continue;
        uint64_t *cons[2 * MAXE + 4]; int nc = 0;
        for (int j = p - 1; j >= 0; j--) { int x = F->inH[row[f][j]]; if (x >= 0) { cons[nc++] = P_(F, b, x, a); break; } }
        for (int j = p + 1; j < len[f]; j++) { int x = F->inH[row[f][j]]; if (x >= 0) { cons[nc++] = P_(F, b, a, x); break; } }
        for (int j = t - 1; j >= 0; j--) { int x = F->inH[row[k][j]]; if (x >= 0) { cons[nc++] = P_(F, a, x, b); break; } }
        for (int q = 0; q < k; q++)
            if (nonadj[k][q] && !used[k][q] && F->inH[q] >= 0) cons[nc++] = P_(F, a, b, F->inH[q]);
        uint64_t any = 0;
        for (int w = 0; w < F->W; w++) {
            uint64_t v = dst[w];
            for (int c = 0; c < nc; c++) v &= cons[c][w];
            dst[w] = v; any |= v;
        }
        if (!any) { fprunes++; return 0; }
    }
    return 1;
}

/* ---------- search ---------- */
static int nF[MAXE], FF[MAXE][MAXE];
static int search_edge(int k);

static int trace(int k, int t) {
    if (timed_out) return 0;
    if (t == nF[k]) {
        if (build_and_test(k, 1)) return search_edge(k + 1);
        return 0;
    }
    for (int q = 0; q < nF[k]; q++) {
        int f = FF[k][q];
        if (used[k][f]) continue;
        used[k][f] = 1;
        row[k][t] = f; len[k] = t + 1;
        for (int p = 0; p <= len[f]; p++) {
            for (int j = len[f]; j > p; j--) row[f][j] = row[f][j - 1];
            row[f][p] = k; len[f]++;
            level_tests[k]++;
            int ok = filters_step(k, f, p, t);
            if (ok && build_and_test(k, 0)) {
                D++;
                int r = trace(k, t + 1);
                D--;
                if (r && !count_mode) return 1;
            }
            for (int j = p; j < len[f] - 1; j++) row[f][j] = row[f][j + 1];
            len[f]--;
            if ((++choices & 0xFFFF) == 0 && now() - t0 > maxsec) timed_out = 1;
            if (timed_out) { len[k] = t; used[k][f] = 0; return 0; }
        }
        len[k] = t;
        used[k][f] = 0;
    }
    return 0;
}

static int search_edge(int k) {
    if (k == m) {
        complete_found++;
        if (dumpf) {
            for (int e = 0; e < m; e++) {
                if (e) fputs("|", dumpf);
                for (int t = 0; t < len[e]; t++) fprintf(dumpf, t ? " %d" : "%d", row[e][t]);
            }
            fputs("\n", dumpf);
        }
        if (!count_mode || complete_found <= 2) {
            printf("PLANAR COMPLETE SYSTEM #%lld:\n", complete_found);
            for (int e = 0; e < m; e++) {
                printf("  pi_%d (%d->%d):", e, EU[e], EV[e]);
                for (int t = 0; t < len[e]; t++) printf(" %d", row[e][t]);
                printf("\n");
            }
        }
        return 1;
    }
    len[k] = 0;
    return trace(k, 0);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: thr2 GRAPH [--count] [--dump FILE] [--filter SYS=map]... [--maxsec S]\n"); return 1; }
    FILE *fp = fopen(argv[1], "r");
    if (!fp || fscanf(fp, "%d %d", &n, &m) != 2) { fprintf(stderr, "bad graph file\n"); return 1; }
    for (int i = 0; i < m; i++) if (fscanf(fp, "%d %d", &EU[i], &EV[i]) != 2) return 1;
    fclose(fp);
    for (int e = 0; e < m; e++)
        for (int f = 0; f < m; f++)
            nonadj[e][f] = (e != f) && EU[e] != EU[f] && EU[e] != EV[f] && EV[e] != EU[f] && EV[e] != EV[f];
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--count")) count_mode = 1;
        else if (!strcmp(argv[i], "--dump") && i + 1 < argc) {
            count_mode = 1; dumpf = fopen(argv[++i], "w");
            fprintf(dumpf, "H %d %d\n", m, n);
            for (int e = 0; e < m; e++) fprintf(dumpf, "%d %d\n", EU[e], EV[e]);
        }
        else if (!strcmp(argv[i], "--filter") && i + 1 < argc) load_filter(argv[++i]);
        else if (!strcmp(argv[i], "--maxsec") && i + 1 < argc) maxsec = atof(argv[++i]);
        else { fprintf(stderr, "unknown arg %s\n", argv[i]); return 1; }
    }
    for (int k = 0; k < m; k++) {
        nF[k] = 0;
        for (int f = 0; f < k; f++) if (nonadj[k][f]) FF[k][nF[k]++] = f;
    }
    t0 = now();
    int res = search_edge(0);
    double dt = now() - t0;
    if (dumpf) fclose(dumpf);
    const char *verdict = timed_out ? "TIMEOUT" : count_mode ? "COUNT" : (res ? "THRACKLEABLE" : "NOT_THRACKLEABLE");
    printf("RESULT %s  complete_planar_systems=%lld  planarity_tests=%lld  planar=%lld  filter_prunes=%lld  wall=%.2fs\n",
           verdict, complete_found, tests, planar_hits, fprunes, dt);
    printf("choices per edge:");
    for (int k = 0; k < m; k++) printf(" e%d:%lld", k, level_tests[k]);
    printf("\n");
    return timed_out ? 3 : 0;
}
