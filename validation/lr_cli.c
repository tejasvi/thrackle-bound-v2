/* reads graphs from stdin: "n m" then m lines "u v"; prints 1/0 per graph */
#include <stdio.h>
#include "lr.h"
static int U[LR_MAXM], V[LR_MAXM];
int main(void) {
    int n, m;
    while (scanf("%d %d", &n, &m) == 2) {
        for (int i = 0; i < m; i++) if (scanf("%d %d", &U[i], &V[i]) != 2) return 1;
        printf("%d\n", lr_planar(n, m, U, V));
    }
    return 0;
}
