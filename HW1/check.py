import numpy as np

h,w = 500,500

M = [[0 for x in range(w)] for y in range(h)]
N = [[0 for x in range(w)] for y in range(h)]

with open("input.txt") as f:
	lines = f.readlines()
	for line in lines:
		words = line.split(',')
		i = int(words[1])
		j = int(words[2])
		val = int(words[3][:-1])
		if words[0] == 'M':
			M[i][j] = val
		else:
			N[i][j] = val

M = np.array(M)
N = np.array(N)

P = np.matmul(M, N)

fp = open("check_ans.txt", "w")
for i in range(P.shape[0]):
	for j in range(P.shape[1]):
		fp.write(f"{i},{j},{P[i][j]}\n")
fp.close()


