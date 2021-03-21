#!/usr/bin/python3
# -*- coding: future_fstrings -*-
"""DPDB Solver

Usage:
	solve.py (-p | --problem) <task> (-f | --file) <file> (-fo | --format) <fileformat> [-a <additional_parameter>]
	solve.py --formats
	solve.py --problems
	solve.py (-h | --help)

Options:
	-h --help			Show this screen.
	--formats			Show all supported file formats
	--problems			Show all supported problems
	-p --problem 		Argumentation problem to solve
	-f --file 			Input file for the problem to solve
	-fo --fileformat	File format of the input file
	-a 					Additional parameter for DC and DS problem: arguments that are queried for acceptance
"""
import subprocess, random
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
	args = docopt(__doc__)
	if args['--formats'] == True:
		print("[apx, tgf]")
	elif args['--problems'] == True:
		print("[CE-CO, CE-PR, CE-ST]")
	else:
		cfg = read_cfg("config.json")
		p = subprocess.Popen([cfg["htd"]["path"], "--seed", "0", *cfg["htd"]["parameters"]], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

		input_ = None
		if args['<fileformat>'] == "apx":
			input_ = ApxReader.from_file(args['<file>'])
		elif args['<fileformat>'] == "tgf":
			input_ = TgfReader.from_file(args['<file>'])
		input = (input_.num_vertices, input_.edges)

		StreamWriter(p.stdin).write_gr(*input)
		p.stdin.close()
		tdr = TdReader.from_stream(p.stdout)
		p.wait()

		problem = ''
		if (args['<task>'] == "CE-CO"):
			problem = "CEComplete"
		elif (args['<task>'] == "CE-ST"):
			problem = "CEStable"
		elif (args['<task>'] == "CE-PR"):
			problem = "CEPreferred"

		# Should be using popen.
		if tdr.tree_width < tw_limit:
			print(f"python ../../dpdb.py -f {args['<file>']} {problem} --input-format {args['<fileformat>']}")
		else:
			print(f"../mu-toksia/mu-toksia -p {args['<task>']} -f {args['<file>']} -fo {args['<fileformat>']}")