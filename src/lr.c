/* Left-Right planarity test (Brandes, "The Left-Right Planarity Test", 2009), test only, no embedding.
   lr_planar(n, m, U, V): 1 if the simple undirected graph with vertices 0..n-1 and edges (U[i], V[i]) is planar.
   Duplicate edges and loops must be removed by the caller. Not thread-safe (static work arrays). */
#include <string.h>
#include "lr.h"

typedef struct { int low, high; } Iv;          /* edge ids, -1 = none */
typedef struct { Iv L, R; } CP;

static int N, M;
static int eu[LR_MAXM], ev[LR_MAXM];
static int adj_start[LR_MAXN + 1], adj_list[2 * LR_MAXM], deg[LR_MAXN];
static int src[LR_MAXM], dst[LR_MAXM], oriented[LR_MAXM];
static int height[LR_MAXN], parent_edge[LR_MAXN];
static int lowpt[LR_MAXM], lowpt2[LR_MAXM], nest[LR_MAXM];
static int out_start[LR_MAXN + 1], out_list[2 * LR_MAXM], out_fill[LR_MAXN];
static int ref_[LR_MAXM], lowpt_edge[LR_MAXM], stack_bottom[LR_MAXM];
static CP S[LR_MAXM + 1];
static int sp;
static int roots[LR_MAXN], nroots;

static inline int imin(int a, int b) { return a < b ? a : b; }
static inline int iv_empty(Iv I) { return I.low < 0 && I.high < 0; }
static inline int conflicting(Iv I, int b) { return !iv_empty(I) && lowpt[I.high] > lowpt[b]; }
static inline int lowest(const CP *P) {
    if (iv_empty(P->L)) return lowpt[P->R.low];
    if (iv_empty(P->R)) return lowpt[P->L.low];
    return imin(lowpt[P->L.low], lowpt[P->R.low]);
}

static void dfs1(int v) {
    int e = parent_edge[v];
    for (int k = adj_start[v]; k < adj_start[v + 1]; k++) {
        int id = adj_list[k];
        if (oriented[id]) continue;
        oriented[id] = 1;
        int w = (eu[id] == v) ? ev[id] : eu[id];
        src[id] = v; dst[id] = w;
        out_list[out_start[v] + out_fill[v]++] = id;
        lowpt[id] = height[v]; lowpt2[id] = height[v];
        if (height[w] < 0) {                    /* tree edge */
            parent_edge[w] = id; height[w] = height[v] + 1;
            dfs1(w);
        } else {                                 /* back edge */
            lowpt[id] = height[w];
        }
        nest[id] = 2 * lowpt[id];
        if (lowpt2[id] < height[v]) nest[id] += 1;   /* chordal */
        if (e >= 0) {
            if (lowpt[id] < lowpt[e]) { lowpt2[e] = imin(lowpt[e], lowpt2[id]); lowpt[e] = lowpt[id]; }
            else if (lowpt[id] > lowpt[e]) lowpt2[e] = imin(lowpt2[e], lowpt[id]);
            else lowpt2[e] = imin(lowpt2[e], lowpt2[id]);
        }
    }
}

static int add_constraints(int ei, int e) {
    CP P = {{-1, -1}, {-1, -1}};
    do {                                          /* merge return edges of ei into P.R */
        CP Q = S[--sp];
        if (!iv_empty(Q.L)) { Iv t = Q.L; Q.L = Q.R; Q.R = t; }
        if (!iv_empty(Q.L)) return 0;
        if (lowpt[Q.R.low] > lowpt[e]) {
            if (iv_empty(P.R)) P.R = Q.R;
            else ref_[P.R.low] = Q.R.high;
            P.R.low = Q.R.low;
        } else {
            ref_[Q.R.low] = lowpt_edge[e];
        }
    } while (sp != stack_bottom[ei]);
    while (sp > 0 && (conflicting(S[sp - 1].L, ei) || conflicting(S[sp - 1].R, ei))) {
        CP Q = S[--sp];                           /* merge conflicting return edges of e_1..e_{i-1} into P.L */
        if (conflicting(Q.R, ei)) { Iv t = Q.L; Q.L = Q.R; Q.R = t; }
        if (conflicting(Q.R, ei)) return 0;
        if (P.R.low >= 0) ref_[P.R.low] = Q.R.high;
        if (Q.R.low >= 0) P.R.low = Q.R.low;
        if (iv_empty(P.L)) P.L = Q.L;
        else ref_[P.L.low] = Q.L.high;
        P.L.low = Q.L.low;
    }
    if (!(iv_empty(P.L) && iv_empty(P.R))) S[sp++] = P;
    return 1;
}

static void remove_back_edges(int e) {
    int u = src[e];
    while (sp > 0 && lowest(&S[sp - 1]) == height[u]) sp--;
    if (sp > 0) {
        CP *P = &S[sp - 1];
        while (P->L.high >= 0 && dst[P->L.high] == u) P->L.high = ref_[P->L.high];
        if (P->L.high < 0 && P->L.low >= 0) { ref_[P->L.low] = P->R.low; P->L.low = -1; }
        while (P->R.high >= 0 && dst[P->R.high] == u) P->R.high = ref_[P->R.high];
        if (P->R.high < 0 && P->R.low >= 0) { ref_[P->R.low] = P->L.low; P->R.low = -1; }
    }
    if (lowpt[e] < height[u] && sp > 0) {        /* ref of e = highest return edge (embedding only) */
        int hl = S[sp - 1].L.high, hr = S[sp - 1].R.high;
        ref_[e] = (hl >= 0 && (hr < 0 || lowpt[hl] > lowpt[hr])) ? hl : hr;
    }
}

static int dfs2(int v) {
    int e = parent_edge[v];
    for (int k = out_start[v]; k < out_start[v + 1]; k++) {
        int ei = out_list[k], w = dst[ei];
        stack_bottom[ei] = sp;
        if (ei == parent_edge[w]) {
            if (!dfs2(w)) return 0;
        } else {
            lowpt_edge[ei] = ei;
            S[sp].L.low = S[sp].L.high = -1; S[sp].R.low = S[sp].R.high = ei; sp++;
        }
        if (lowpt[ei] < height[v]) {
            if (k == out_start[v]) lowpt_edge[e] = lowpt_edge[ei];
            else if (!add_constraints(ei, e)) return 0;
        }
    }
    if (e >= 0) remove_back_edges(e);
    return 1;
}

int lr_planar(int n, int m, const int *U, const int *V) {
    if (n > LR_MAXN || m > LR_MAXM) return -1;
    if (n >= 3 && m > 3 * n - 6) return 0;
    N = n; M = m;
    memset(deg, 0, sizeof(int) * n);
    for (int i = 0; i < m; i++) { eu[i] = U[i]; ev[i] = V[i]; deg[U[i]]++; deg[V[i]]++; }
    adj_start[0] = 0;
    for (int v = 0; v < n; v++) adj_start[v + 1] = adj_start[v] + deg[v];
    memset(deg, 0, sizeof(int) * n);
    for (int i = 0; i < m; i++) {
        adj_list[adj_start[eu[i]] + deg[eu[i]]++] = i;
        adj_list[adj_start[ev[i]] + deg[ev[i]]++] = i;
    }
    /* out_start: an upper bound slot per vertex (degree), filled during dfs1, compacted after */
    for (int v = 0; v <= n; v++) out_start[v] = adj_start[v];
    for (int v = 0; v < n; v++) { height[v] = -1; parent_edge[v] = -1; out_fill[v] = 0; }
    for (int i = 0; i < m; i++) { oriented[i] = 0; ref_[i] = -1; lowpt_edge[i] = -1; }
    nroots = 0;
    for (int v = 0; v < n; v++)
        if (height[v] < 0) { height[v] = 0; roots[nroots++] = v; dfs1(v); }
    /* compact out lists and sort each by nesting depth (stable insertion sort) */
    {
        static int tmp[2 * LR_MAXM];
        int pos = 0;
        for (int v = 0; v < n; v++) {
            int s = out_start[v], c = out_fill[v];
            for (int j = 0; j < c; j++) tmp[pos + j] = out_list[s + j];
            for (int j = 1; j < c; j++) {
                int x = tmp[pos + j], k = j - 1;
                while (k >= 0 && nest[tmp[pos + k]] > nest[x]) { tmp[pos + k + 1] = tmp[pos + k]; k--; }
                tmp[pos + k + 1] = x;
            }
            out_start[v] = pos; pos += c;
        }
        out_start[n] = pos;
        memcpy(out_list, tmp, sizeof(int) * pos);
    }
    for (int r = 0; r < nroots; r++) { sp = 0; if (!dfs2(roots[r])) return 0; }
    return 1;
}
