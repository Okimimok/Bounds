import future
import xlwt
import numpy as np
import sys
from os.path import abspath, dirname, realpath, join

def main():
	basePath = dirname(realpath(__file__))
	outFile  = sys.argv[1]
	xlsFile  = sys.argv[2]
	outPath  = abspath(join(abspath(join(basePath, "..//")), outFile))
	xlsPath  = abspath(join(abspath(join(basePath, "..//")), xlsFile))

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

	# Open output file
	with open(outPath, 'r') as f:
		line   = f.readline().split()
		# Number of arrival probabilities/utilizations tested
		nProbs = int(line[0])
		nBnds  = int(line[1])
		names  = f.readline().split()

		#############################################
		# Interlude: Create spreadsheet
		w = xlwt.Workbook()
		ws = w.add_sheet('Results')
		#
		# ------First row
		# Four columns for lower bd: (obj, util, late, missed)
		ws.write(0, 0, 'P(Arrival)', styleB)
		ws.write_merge(0, 0, 1, 4, names[0], styleB)
		#
		# Two columns for each upper bd considered (obj, gap)
		cnt = 5
		for j in range(1, nBnds):
			ws.write_merge(0, 0, cnt, cnt+1, names[j], styleB)
			cnt += 2
		#
		# ------Second row
		for j in range(nBnds):
			if j == 0:
				ws.write(1, 1, 'Utiliz.', styleB)
				ws.write(1, 2, 'Late'   , styleB)
				ws.write(1, 3, 'Missed ', styleB)
				ws.write(1, 4, 'Value'  , styleB)
			else:	
				ws.write(1, 2*j + 3, 'Value', styleB)
				ws.write(1, 2*j + 4, 'Gap (%)', styleB)
		#
		# ------ Subsequent rows
		for i in range(nProbs):
			line = f.readline().split()
			ws.write(i+2, 0, float(line[0]), styleN) 
			for j in range(nBnds):
				line = f.readline().split()
				if j == 0:
					valLB = float(line[1])
					util  = float(line[3])
					late  = float(line[4])
					miss  = float(line[5])
					ws.write(i+2, 1, '%.2f' %  util, styleN)
					ws.write(i+2, 2, '%.2f' %  late, styleN)
					ws.write(i+2, 3, '%.2f' %  miss, styleN)
					ws.write(i+2, 4, '%.2f' % valLB, styleN)
				else:
					valUB = float(line[1])
					gap   = 100*(valUB - valLB)/valLB
					ws.write(i+2, 2*j + 3, '%.2f' % valUB, styleN)
					ws.write(i+2, 2*j + 4, '%.2f' % gap, styleN)
			'''
			for j in xrange(m):
				if j > 0:
					ws.write(i+2, j + 1, '%.2f' % utils[i][j], styleN)
					ws.write(i+2, m + 2*j, '%.1f' %  vals[i][j], styleN)
					gap = 100*(vals[i][j] - vals[i][0])/vals[i][0]
					ws.write(i+2, m + 2*j + 1, '%.1f' % gap, styleN)
				else:
					ws.write(i+2, j + 1, '%.2f' % utils[i][j], styleN)
					ws.write(i+2, m + 1 + 2*j, '%.1f' %  vals[i][j], styleN)
			'''
		# End interlude
		#############################################
		
		'''
		for i in xrange(nProbs):
			line = f.readline().split()
			probs[i] = float(line[0])
			for j in xrange(nBnds):
				line        = f.readline().split()
				vals[i][j]  = float(line[0])
		'''
	w.save(xlsPath)

	'''

	'''

if __name__ == '__main__':
	main()
