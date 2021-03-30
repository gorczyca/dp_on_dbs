"""A-Folio DPDB Solver

Usage:
	./subsolver.py (-p | --problem) <task> (-f | --file) <file> (-fo | --format) <fileformat> [-a <additional_parameter>]
	./subsolver.py --formats
	./subsolver.py --problems
	./subsolver.py (-h | --help)

Options:
	-h --help			Show this screen.
	--formats			Show all supported file formats
	--problems			Show all supported problems
	-fo		File format of the input file
	-p  	Argumentation problem to solve
	-f 		Input file for the problem to solve
	-a 		Additional parameter for DC and DS problem: arguments that are queried for acceptance
"""

import subprocess
import re
import argparse
import sys


SUPPORTED_TASKS = [
	'DS-CO', 'DS-ST',
	'DC-CO', 'DC-ST',
	'SE-CO', 'SE-ST',
	'CE-CO', 'CE-ST',
]

DPDB_SUPPORTED_TASKS = [
	'CE-CO', 'CE-ST'
]

EXTENSIONS_NO_DPDB_RE = re.compile(r'\[INFO]\s*dpdb\.problems\.[a-zA-Z0-9_]*:\s*Problem\s*has\s*(?P<val>\d+)\s*[a-zA-Z0-9_]*\s*extensions.*$', re.DOTALL)
EXTENSIONS_NO_D4_RE = re.compile(r's\s*(?P<val>\d+).*$', re.DOTALL)
COUNT_WITH_MU_TOKSIA = True
DESCRIPTION = """A-Folio DPDB v0.1
Johannes Fichte (johannes.fichte@tu-dresden.de), 
Markus Hecher (markus.hecher@tuwien.ac.at), 
Piotr Gorczyca (gorczycapj@gmail.com), 
Ridhwan Dewoprabowo (ridhwan.dewoprabowo@gmail.com)
"""
ONE_BAG_ERROR_MESSAGE = 'One Bag Error'
TW_LIMIT_ERROR_MESSAGE = 'Treewidth Limit Reached'


def main(formats, problems, p, f, fo, a):

	if formats:
		print('[apx,tgf]')
		# print('[tgf]')
	elif problems:
		print(f'[{",".join(SUPPORTED_TASKS)}]')
	else:
		if p not in SUPPORTED_TASKS:
			print(f'{p} task not supported.')

		elif p in DPDB_SUPPORTED_TASKS:
			# problem, semantics = ('CEComplete', 'complete') if task == 'CE-CO' else ('CEStable', 'stable')
			problem, semantics = ('CEComplete', 'CO') if p == 'CE-CO' else ('CEStable', 'ST')
			#output = subprocess.check_output(args=['python', "dpdb.py", "-f", f, problem, "--input-format", fo], shell=True, stderr=subprocess.STDOUT)
			output = subprocess.check_output(args=[f'./run_dpdb.sh {f} {problem} {fo}'], shell=True, stderr=subprocess.STDOUT)
			#output = subprocess.check_output(args=['./run_dpdb.sh', f, problem, fo], shell=True, stderr=subprocess.STDOUT)
			#  DPDB sends info logs to stderr
			# proc = subprocess.Popen(args=[PYTHON_PATH, "dpdb.py", "-f", args['<file>'], problem, "--input-format", args['<fileformat>']], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
			# _, errs = proc.communicate()  # DPDB sends output logs to stderr
			# proc.wait()
			# output = errs.decode()
			output = output.decode()
			# print(output)
			dpdb_task_aborted = (TW_LIMIT_ERROR_MESSAGE in output) or (ONE_BAG_ERROR_MESSAGE in output)

			#if False:  # for testing solvers when TW to high
			if not dpdb_task_aborted:
				extensions_no = re.findall(EXTENSIONS_NO_DPDB_RE, output)[0]
			elif COUNT_WITH_MU_TOKSIA:  # If aborted (TW limit reached) run mu-toksia
				mu_toksia_proc = subprocess.Popen(['./binaries/mu-toksia', '-p', f'EE-{semantics}', '-f', f, '-fo', fo], stdout=subprocess.PIPE)
				extensions_no = 0
				for _ in iter(lambda: mu_toksia_proc.stdout.readline(), b''):
					extensions_no += 1

				# If there are no extensions, then mu_toksia will return only one line, i.e.
				# []
				# oterwise it will always append opening and closing brackets e.g.
				# [
				#	[1,2,3]
				# ]
				# therefore we have to remove 2
				extensions_no = max(0, extensions_no-2)
			else:  # Run the d4
				aspartix_file = 'comp.dl' if p == 'CE-CO' else 'stable.dl'
				output = subprocess.check_output(args=[f'./d4_bash.sh ./aspartix/{aspartix_file} {f}'],
									shell=True, stderr=subprocess.STDOUT)

				output = output.decode()
				extensions_no = re.findall(EXTENSIONS_NO_D4_RE, output)[0]


			print(extensions_no)

		else: 	# If task unsupported by DPDB run mu-toksia
			mu_toksia_command = ['./binaries/mu-toksia', '-p', p, '-f', f, '-fo', fo]
			if a:
				mu_toksia_command += ['-a', a]

			proc = subprocess.Popen(mu_toksia_command, stderr=subprocess.STDOUT)
			proc.wait()


def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.epilog = DESCRIPTION
	parser.add_argument('--formats', help='Prints the supported formats of the solver.', action="store_true")
	parser.add_argument('--problems', help='Prints the supported computational problems.', action="store_true")
	parser.add_argument('-p', help='Problem to solve (see supported problems by invoking with "--problems").')
	parser.add_argument('-f', help='File.')
	parser.add_argument('-fo', help='File format (see supported file formats by invoking with "--formats").')
	parser.add_argument('-a', help='Additional parameters')

	if len(sys.argv) == 1:
		print(DESCRIPTION)
		sys.exit(0)

	args, _ = parser.parse_known_args()
	return args


if __name__ == '__main__':
	arguments = parse_arguments()
	main(**vars(arguments))




