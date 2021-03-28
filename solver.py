#!/home/piotrek/System/programs/anaconda3/envs/testing/bin/python
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
	-fo --fileformat		File format of the input file
	-p --problem 			Argumentation problem to solve
	-f --file 			Input file for the problem to solve
	-a 				Additional parameter for DC and DS problem: arguments that are queried for acceptance
"""

import subprocess
import re

from docopt import docopt

# Version 2 of solver wrapper

# Path to python interpreter in anaconda (should be the same as in 1st line)
PYTHON_PATH = '/home/piotrek/System/programs/anaconda3/envs/nesthdb/bin/python'
# ALL_TASKS = [
# 	'DS-CO', 'DS-PR', 'DS-ST', 'DS-SST', 'DS-STG', 'DS-ID',
# 	'DC-CO', 'DC-PR', 'DC-ST', 'DC-SST', 'DC-STG',
# 	'SE-CO', 'SE-PR', 'SE-ST', 'SE-SST', 'SE-STG', 'SE-ID',
# 	'CE-CO', 'CE-ST'
# ]
SUPPORTED_TASKS = [
	'DS-CO', 'DS-ST',
	'DC-CO', 'DC-ST',
	'SE-CO', 'SE-ST',
	'CE-CO', 'CE-ST',
	'EE-CO', 'EE-ST',
]

DPDB_SUPPORTED_TASKS = [
	'CE-CO', 'CE-ST'
]

EXTENSIONS_NO_RE = re.compile(r'\[INFO]\s*dpdb\.problems\.[a-zA-Z0-9_]*:\s*Problem\s*has\s*(?P<val>\d+)\s*[a-zA-Z0-9_]*\s*extensions.*$', re.DOTALL)
COUNT_WITH_MU_TOKSIA = True

# TODO: current input parsing doesn't allow to change the order of the arguments -> change to argparse?


if __name__ == '__main__':

	args = docopt(__doc__)

	if args['--formats']:
		print('[apx,tgf]')
	elif args['--problems']:
		print(f'[{",".join(SUPPORTED_TASKS)}]')
	else:
		task = args['<task>']
		if task not in SUPPORTED_TASKS:
			print(f'{task} task not supported.')

		elif task in DPDB_SUPPORTED_TASKS:
			# problem, semantics = ('CEComplete', 'complete') if task == 'CE-CO' else ('CEStable', 'stable')
			problem, semantics = ('CEComplete', 'CO') if task == 'CE-CO' else ('CEStable', 'ST')
			output = subprocess.check_output(args=[PYTHON_PATH, "dpdb.py", "-f", args['<file>'], problem, "--input-format", args['<fileformat>']], stderr=subprocess.STDOUT)
			#  DPDB sends info logs to stderr
			# proc = subprocess.Popen(args=[PYTHON_PATH, "dpdb.py", "-f", args['<file>'], problem, "--input-format", args['<fileformat>']], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
			# _, errs = proc.communicate()  # DPDB sends output logs to stderr
			# proc.wait()
			# output = errs.decode()
			output = output.decode()
			dpdb_task_aborted = "Treewidth Limit Reached" in output

			if not dpdb_task_aborted:
				extensions_no = re.findall(EXTENSIONS_NO_RE, output)[0]
			elif COUNT_WITH_MU_TOKSIA:  # If aborted (TW limit reached) run mu-toksia
				mu_toksia_proc = subprocess.Popen(['./mu-toksia', '-p', f'EE-{semantics}', '-f', args['<file>'], '-fo', args['<fileformat>']], stdout=subprocess.PIPE)
				extensions_no = 0
				for ext in iter(lambda: mu_toksia_proc.stdout.readline(), b''):
					extensions_no += 1

				# If there are no extensions, then mu_toksia will return only one line, i.e.
				# []
				# oterwise it will always append opening and closing brackets e.g.
				# [
				#	[1,2,3]
				# ]
				# therefore we have to remove 2
				extensions_no = max(0, extensions_no-2)
			else:  #
				# TODO:
				extensions_no = None
				pass
				# run this bash script
				# clingo -n0
				# -> bash ....
				#d4_proc = subprocess.call('./d4_bash.sh')


			print(extensions_no)

		else: 	# If task unsupported by DPDB run mu-toksia
			mu_toksia_command = ['./mu-toksia', '-p', args['<task>'], '-f', args['<file>'], '-fo', args['<fileformat>']]
			if args['-a']:
				mu_toksia_command += ['-a', args['<additional_parameter>']]

			proc = subprocess.Popen(mu_toksia_command, stderr=subprocess.STDOUT)
			proc.wait()


