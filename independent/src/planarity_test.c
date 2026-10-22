/* planarity_test.c: harness for the Edge Addition Planarity Suite (third-party planarity library) */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "graphLib.h"
static int is_planar(int n, int m, const int *eu, const int *ev) {
    graphP g = gp_New();
    if (gp_EnsureVertexCapacity(g, n) != OK) { fprintf(stderr, "cap\n"); exit(2); }
    if (gp_EnsureEdgeCapacity(g, m > 0 ? m : 1) != OK) { fprintf(stderr, "ecap\n"); exit(2); }
    for (int i = 0; i < m; i++) if (gp_AddEdge(g, eu[i] + 1, 0, ev[i] + 1, 0) != OK) { fprintf(stderr, "add %d %d\n", eu[i], ev[i]); exit(2); }
    int r = gp_Embed(g, EMBEDFLAGS_PLANAR);
    gp_Free(&g);
    if (r == OK) return 1;
    if (r == NONEMBEDDABLE) return 0;
    fprintf(stderr, "embed error %d\n", r); exit(2);
}
int main(void) {
    int k5u[10], k5v[10], k = 0;
    for (int a = 0; a < 5; a++) for (int b = a + 1; b < 5; b++) { k5u[k] = a; k5v[k] = b; k++; }
    printf("K5 planar? %d (expect 0)\n", is_planar(5, 10, k5u, k5v));
    printf("K5-e planar? %d (expect 1)\n", is_planar(5, 9, k5u + 1, k5v + 1));
    int k33u[9], k33v[9]; k = 0;
    for (int a = 0; a < 3; a++) for (int b = 3; b < 6; b++) { k33u[k] = a; k33v[k] = b; k++; }
    printf("K33 planar? %d (expect 0)\n", is_planar(6, 9, k33u, k33v));
    /* speed: grid 12x14 (168 vertices, planar) */
    int W = 12, H = 14, n = W * H, m = 0; int *u = malloc(4 * 1000), *v = malloc(4 * 1000);
    for (int y = 0; y < H; y++) for (int x = 0; x < W; x++) { int id = y * W + x;
        if (x + 1 < W) { u[m] = id; v[m] = id + 1; m++; } if (y + 1 < H) { u[m] = id; v[m] = id + W; m++; } if (x + 1 < W && y + 1 < H) { u[m] = id; v[m] = id + W + 1; m++; } }
    clock_t t0 = clock(); int s = 0;
    for (int it = 0; it < 20000; it++) s += is_planar(n, m, u, v);
    printf("grid %d vertices %d edges: %d/20000 planar, %.1f us/test\n", n, m, s, 1e6 * (double)(clock() - t0) / CLOCKS_PER_SEC / 20000);
    return 0;
}
