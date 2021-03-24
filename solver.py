# -*- coding: future_fstrings -*-
"""DPDB Solver

Usage:
	solver.py (-p | --problem) <task> (-f | --file) <file> (-fo | --format) <fileformat> [-a <additional_parameter>]
	solver.py --formats
	solver.py --problems
	solver.py (-h | --help)

Options:
	-h --help			Show this screen.
	--formats			Show all supported file formats
	--problems			Show all supported problems
	-p --problem 			Argumentation problem to solve
	-f --file 			Input file for the problem to solve
	-fo --fileformat		File format of the input file
	-a 				Additional parameter for DC and DS problem: arguments that are queried for acceptance
"""
import subprocess
from docopt import docopt
from subprocess import Popen
from dpdb.reader import ApxReader, TgfReader, TdReader
from dpdb.writer import StreamWriter, FileWriter

# Version 2 of solver wrapper
# Requires docopt in conda

def read_cfg(cfg_file):
	import json

	with open(cfg_file) as c:
		cfg = json.load(c)
	return cfg

if __name__ == '__main__':
	tw_limit = 100
	run_mutoksia = False

	args = docopt(__doc__)
	if args['--formats']:
		print("[apx,tgf]")
	elif args['--problems']:
		print("[DS-CO,DS-PR,DS-ST,DS-SST,DS-STG,DS-ID,DC-CO,DC-PR,DC-ST,DC-SST,DC-STG,SE-CO,SE-PR,SE-ST,SE-SST,SE-STG,SE-ID,CE-CO,CE-ST]")
	else:
		problem = ''
		if (args['<task>'] == "CE-CO"):
			problem = "CEComplete"
		elif (args['<task>'] == "CE-ST"):
			problem = "CEStable"
		else:
			problem = args['<task>']

		if (problem == "CEComplete" or problem == "CEStable"):
			proc = subprocess.Popen(f"python dpdb.py -f {args['<file>']} {problem} --input-format {args['<fileformat>']}", stdout=subprocess.PIPE)
			outs, errs = proc.communicate()
			proc.wait()
			if ("Treewidth Limit Reached" in str(outs)):
				run_mutoksia = True
		else:
			run_mutoksia = True
			
	if run_mutoksia:
		if args['-a']:
			proc = subprocess.Popen(f"../mu-toksia/mu-toksia -p {args['<task>']} -f {args['<file>']} -fo {args['<fileformat>']} -a {args['<additional_parameter>']}")
			proc.wait()
		else:
			proc = subprocess.Popen(f"../mu-toksia/mu-toksia -p {args['<task>']} -f {args['<file>']} -fo {args['<fileformat>']}")
			proc.wait()