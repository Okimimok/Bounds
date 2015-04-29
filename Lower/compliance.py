from ..Models import MECRP, MEXCRP

def buildTable(svca, astr,  w):
	# Solving the resulting coverage problems
	settings = {'OutputFlag' : 0, 'MIPGap' : 0.005}
	A = svca.A
	p = MECRP.ModelInstance(svca, astr, A, w)
	p.solve(settings)

	# Obtaining compliance table
	table = {}
	v     = p.getDecisionVars()

	for a in range(1, A+1):
		table[a] = []
		for j in svca.bases:
			for k in range(int(v['x'][a][j].x)):
				table[a].append(j)

	return table 

def buildDaskinTable(svca, astr, q, w, settings):
	A = svca.A
	p = MEXCRP.ModelInstance(svca, astr, A, q, w)
	p.solve(settings)

	# Obtaining compliance table
	table = {}
	v     = p.getDecisionVars()

	for a in range(1, A+1):
		table[a] = []
		for j in svca.bases:
			for k in range(int(v['x'][a][j].x)):
				table[a].append(j)

	return table 

def writeTable(table, tablePath):
	# Given a compliance table, save it to the location tablePath
	A = len(table)
	with open(tablePath, 'w') as f:
		f.write('%i\n' % A)
		for a in range(1, A+1):
			for j in range(a):
				f.write('%i ' % table[a][j])
			f.write('\n')

def readTable(tablePath):
	# Given a path to a compliance table policy, a file having the form
	# A
	# b1
	# b1 b2 (etc.)
	# ...reads the file and saves the compliance table in a dictionary
	table = {}
	with open(tablePath, 'r') as f:
		A = int(f.readline())
		for a in range(1, A+1):
			table[a] = [int(i) for i in f.readline().split()]

	return table

