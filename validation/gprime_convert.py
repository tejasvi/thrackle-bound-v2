# convert the logged sample into dmp.py input and the LR verdict list
lines = open('prep/gprime_sample.txt').read().split('\n')
out = []; ver = []; i = 0
while i < len(lines):
    if not lines[i].strip(): i += 1; continue
    n, m, r = map(int, lines[i].split()); ver.append(r)
    out.append(f"{n} {m}"); out.extend(lines[i + 1:i + 1 + m]); i += 1 + m
open('prep/gprime_sample_in.txt', 'w').write('\n'.join(out) + '\n')
open('prep/gprime_sample_lr.txt', 'w').write('\n'.join(map(str, ver)) + '\n')
print(len(ver), 'graphs')
