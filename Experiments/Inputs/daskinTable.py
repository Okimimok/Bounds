import configparser, sys
import numpy as np
from ...Methods.network import readNetwork	
from ...Lower.compliance import buildDaskinTable, writeTable
from ...Components.ArrStream import ArrStream
from os.path import abspath, dirname, realpath, join

def main():
	basePath    = dirname(realpath(__file__))
	networkFile = input("Network file : ")
	tableFile   = input("Table file   : ")
	networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
	tablePath   = abspath(join(abspath(join(basePath, "..//")), tableFile))

	# Read config file for input parameters
	configPath = abspath(join(abspath(join(basePath, "..//")), sys.argv[1]))
	cp         = configparser.ConfigParser()
	cp.read(configPath)

	# Inputs: q (busy prob. estimate), w (weight vector)
	q = cp['daskin'].getfloat('q')
	w = eval(cp['daskin']['w'])

	# Solver settings	 
	settings = {}
	for item in cp['daskinsettings']:
		settings[item] = eval(cp['daskinsettings'][item])

	# Network properties
	svca  = readNetwork(networkPath)
	astr  = ArrStream(svca, 2)
	table = buildDaskinTable(svca, astr, q, w, settings)
	writeTable(table, tablePath)

if __name__ == '__main__':
	main()
