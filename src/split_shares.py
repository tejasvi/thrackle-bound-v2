import sys
lines = open(sys.argv[1]).read().splitlines()
h = int(lines[0].split()[1]); hdr = lines[:1 + h]; st = lines[1 + h:]
K = int(sys.argv[2])
for k in range(K):
    open(f'{sys.argv[3]}_{k}.txt', 'w').write('\n'.join(hdr + st[k::K]) + '\n')
print(len(st), 'states ->', K, 'shares')
