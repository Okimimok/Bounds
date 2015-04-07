import xlwt
import sys 
import numpy as np

def build(filePath, xlsPath):
	with open(filePath, 'r') as f:
		# Number of arrival regimes tested
		line  = f.readline().split()
		n     = int(line[0])
		m     = int(line[1])
		probs = np.zeros(n)
		vals  = np.zeros((n, m))
		utils = np.zeros((n, m))
		names = f.readline().split()
		for i in xrange(n):
			line = f.readline().split()
			probs[i] = float(line[0])
			for j in xrange(m):
				line        = f.readline().split()
				vals[i][j]  = float(line[0])
				utils[i][j] = float(line[2]) 

	# Font style for column headers
	fnt      = xlwt.Font()
	fnt.name = 'Arial'
	fnt.bold = True

	# Centered alignment
	al      = xlwt.Alignment()
	al.horz = xlwt.Alignment.HORZ_CENTER

	# Bold style
	styleB           = xlwt.XFStyle()
	styleB.font      = fnt
	styleB.alignment = al

	# Normal style
	styleN           = xlwt.XFStyle()
	styleN.alignment = al

	w = xlwt.Workbook()
	ws = w.add_sheet('Results')

	# First row
	ws.write(0, 0, 'P(Arrival)', styleB)
	ws.write_merge(0, 0, 1, m, 'Utilizations', styleB)
	cnt = m + 1
	for j in xrange(m):
		if j > 0:
			ws.write_merge(0, 0, cnt, cnt+1, names[j], styleB)
			cnt += 2
		else:
			ws.write(0, cnt, names[j], styleB)
			cnt += 1

	# Second row
	for j in xrange(m):
		if j > 0:
			ws.write(1, j+1, names[j], styleB)
			ws.write(1, m + 2*j, 'Value', styleB)
			ws.write(1, m + 2*j + 1, 'Gap (%)', styleB)
		else:
			ws.write(1, j+1, names[j], styleB)
			ws.write(1, m + 1 + 2*j, 'Value', styleB)

	# Subsequent rows
	for i in xrange(n):
		ws.write(i+2, 0, probs[i], styleN) 
		for j in xrange(m):
			if j > 0:
				ws.write(i+2, j + 1, '%.2f' % utils[i][j], styleN)
				ws.write(i+2, m + 2*j, '%.1f' %  vals[i][j], styleN)
				gap = 100*(vals[i][j] - vals[i][0])/vals[i][0]
				ws.write(i+2, m + 2*j + 1, '%.1f' % gap, styleN)
			else:
				ws.write(i+2, j + 1, '%.2f' % utils[i][j], styleN)
				ws.write(i+2, m + 1 + 2*j, '%.1f' %  vals[i][j], styleN)

	w.save(xlsPath)

def main(argv):
	build(argv[0], argv[1])

if __name__ == '__main__':
	main(sys.argv[1:])
