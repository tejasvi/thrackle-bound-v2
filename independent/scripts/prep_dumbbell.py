"""prep_dumbbell.py K THR OUTDIR: DB(6,8,-K) in my labelling with the 8-cycle first (shared path 0..K, the 8-cycle's path,
then the 6-cycle's path) and its filter subgraphs, each with its complete planar systems from thr_indep --dumpall:
C8 (first 8 edges), C6 (shared path + 6-cycle path), C8 + first / last edge of the 6-path, C6 + first / last edge of
the 8-path.  Prints the --filter arguments."""
import sys, os, subprocess
K, thr, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
edges = [(i, i + 1) for i in range(K)]; nv = K + 1
def closing(length):
    global nv
    vs = [K] + [nv + i for i in range(length - 1)] + [0]; nv += length - 1
    return [(vs[i], vs[i + 1]) for i in range(length)]
A = closing(8 - K); B = closing(6 - K)          # A: 8-cycle path, B: 6-cycle path
S = edges[:]
G = S + A + B
def write(name, es):
    fn = os.path.join(out, name + '.txt')
    with open(fn, 'w') as f: f.write(f'{nv} {len(es)}\n' + ''.join(f'{u} {v}\n' for u, v in es))
    return fn
g = write(f'DB68m{K}', G)
H = {'C8': S + A, 'C6': S + B, 'C8b0': S + A + [B[0]], 'C8b1': S + A + [B[-1]], 'C6a0': S + B + [A[0]], 'C6a1': S + B + [A[-1]]}
args = []
for name, es in H.items():
    hf = write(f'DB68m{K}_{name}', es); sf = hf[:-4] + '_sys.txt'
    cmd = [thr, hf, '--dumpall', sf]
    if name in ('C8b0', 'C8b1'): cmd += ['--filter', os.path.join(out, f'DB68m{K}_C8.txt'), os.path.join(out, f'DB68m{K}_C8_sys.txt')]
    if not os.path.exists(sf):
        r = subprocess.run(cmd, capture_output=True, text=True, check=True); print(name, r.stdout.strip())
    args += ['--filter', hf, sf]
print('GRAPH', g, 'edges', G)
print('FILTERS', ' '.join(args))
