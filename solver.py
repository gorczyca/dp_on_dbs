#!/usr/bin/python3
# -*- coding: future_fstrings -*-
import argparse, textwrap
import subprocess
from subprocess import Popen
from dpdb.reader import ApxReader, TgfReader, TdReader
from dpdb.writer import StreamWriter, FileWriter

# Container example for the actual solver file.

def read_cfg(cfg_file):
	import json

	with open(cfg_file) as c:
		cfg = json.load(c)
	return cfg

if __name__ == "__main__":
	tw_limit = 100

	class FormatsAction(argparse.Action):
		def __init__(self, nargs=0, **kw):
			super().__init__(nargs=nargs, **kw)
		def __call__(self, parser, namespace, values, option_string=None):
			print("[apx,tgf]")

	class ProblemsAction(argparse.Action):
		def __init__(self, nargs=0, **kw):
			super().__init__(nargs=nargs, **kw)
		def __call__(self, parser, namespace, values, option_string=None):
			print("[CE-CO,CE-PR,CE-ST]")

	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description=textwrap.dedent('''\
	DPDB Solver
	--------------------------------
	Authors
	authors@email.com
			'''),
		prog='solver',
		usage="python solver.py -p <task> -f <file> -fo <fileformat> [-a <additional_parameter>]")

	parser.add_argument("-p", "--problem", dest="problem", help="Argumentation problem to solve", required=True)
	parser.add_argument("-f", "--file", dest="file", help="Input file for the problem to solve", required=True)
	parser.add_argument("-fo", dest="format", help="File format of the input file", required=True)
	parser.add_argument("-a", dest="more", help="Additional parameter for DC and DS problem: arguments that are queried for acceptance", required=False)

	args = parser.parse_args()
	args = vars(args)

	cfg = read_cfg("config.json")
	p = subprocess.Popen([cfg["htd"]["path"], "--seed", "0", *cfg["htd"]["parameters"]], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

	input_ = None
	if args['format'] == "apx":
		input_ = ApxReader.from_file(args['file'])
	elif args['format'] == "tgf":
		input_ = TgfReader.from_file(args['file'])
	input = (input_.num_vertices, input_.edges)

	StreamWriter(p.stdin).write_gr(*input)
	p.stdin.close()
	tdr = TdReader.from_stream(p.stdout)
	p.wait()

	problem = ''
	if (args['problem'] == "CE-CO"):
		problem = "CEComplete"
	elif (args['problem'] == "CE-ST"):
		problem = "CEStable"
	elif (args['problem'] == "CE-PR"):
		problem = "CEPreferred"

	# Should be using popen.
	if tdr.tree_width < tw_limit:
		print(f"python ../../dpdb.py -f {args['file']} {problem} --input-format {args['format']}")
	else:
		print(f"../mu-toksia/mu-toksia -p {args['problem']} -f {args['file']} -fo {args['format']}")
