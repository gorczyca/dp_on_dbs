import unittest
import logging
import ast
from dpdb.reader import ApxReader, TgfReader

logger = logging.getLogger(__name__)
TESTCASE_PATH = 'input/TestCases'

class TestCEReader(unittest.TestCase):
	def openFile(self, filename, filetype):
		input = None
		if filetype == "apx":
			input = ApxReader.from_file(filename+filetype)
		elif filetype == "tgf":
			input = TgfReader.from_file(filename+filetype)

		return (input.vertices, input.num_vertices, input.edges, input.adjacency_list)

	def assertEqualList(self, list1, list2):
		# Determine if two lists are the same despite ordering
		if len(list1) != len(list2):
			raise AssertionError
		if sorted(list1) != sorted(list2):
			raise AssertionError
		return True
	
	def assertEqualDictList(self, dic1, dic2):
		# Determine if two dictionaries of lists are the same despite ordering in the list
		if len(dic1) != len(dic2):
			raise AssertionError
		if sorted(dic1) != sorted(dic2):
			raise AssertionError
		for key in sorted(dic1):
			if not self.assertEqualList(dic1[key], dic2[key]):
				raise AssertionError
		return True

	def assertEquals(self, properties, validator):
		# Determine if the data obtained from parsing is valid
		self.assertEqual(properties[0], ast.literal_eval(validator[0]))
		self.assertEqualList(properties[1], ast.literal_eval(validator[1]))
		self.assertEqualList(properties[2], ast.literal_eval(validator[2]))
		self.assertEqualDictList(properties[3], ast.literal_eval(validator[3]))

	def assertValid(self, filetype):
		# Check when the input file is valid
		# Valid1 = Random
		# Valid2 = Contain clique
		# Valid3 = Large size
		for i in range(1,4):
			fname = TESTCASE_PATH+"/valid"+str(i)+".txt"
			verts, num, edges, adjl = self.openFile(TESTCASE_PATH+"/valid"+str(i)+".", filetype)
			with open(fname, "r") as f:
				validator = f.read().split('\n')
			self.assertEquals([num, verts, edges, adjl], validator)
			logger.info("assertValid "+str(i)+" passed")

	def assertDuplicate(self, filetype):
		# Check when there are duplicate declarations
		try:
			verts, num, edges, adjl = self.openFile(TESTCASE_PATH+"/duplicate.", filetype)
		except:
			logger.info("assertDuplicate passed")

	def assertEmptyDecs(self, filetype):
		# Check when there are declarations without any argument.
		# Check when there are no sharp symbol.
		try:
			verts, num, edges, adjl = self.openFile(TESTCASE_PATH+"/emptydecs.", filetype)
		except:
			logger.info("assertEmptyDecs passed")

	def assertInsufAttArg(self, filetype):
		# Check when there are attack declarations with insufficient argument.
		try:
			verts, num, edges, adjl = self.openFile(TESTCASE_PATH+"/insufattarg.", filetype)
		except:
			logger.info("assertInsufAttArg passed")

	def assertExcessArg(self, filetype):
		# Check when there are declarations with excessive arguments.
		try:
			verts, num, edges, adjl = self.openFile(TESTCASE_PATH+"/excessarg.", filetype)
		except:
			logger.info("assertExcessArg passed")

	def assertMixedUp(self, filetype):
		# Check when there are declarations with excessive arguments.
		try:
			verts, num, edges, adjl = self.openFile(TESTCASE_PATH+"/mixup.", filetype)
		except:
			logger.info("assertMixedUp passed")

	def assertUndeclared(self, filetype):
		# Check when there are attack declarations involving undeclared arguments.
		try:
			verts, num, edges, adjl = self.openFile(TESTCASE_PATH+"/undeclared.", filetype)
		except:
			logger.info("assertUndeclared passed")

	def assertInvalidType(self, filetype):
		# Check when there are declarations with excessive arguments.
		try:
			verts, num, edges, adjl = self.openFile(TESTCASE_PATH+"/invalidtype.", filetype)
		except:
			logger.info("assertInvalidType passed")

	def assertNoSharp(self, filetype):
		# Check when there are no sharp symbol.
		try:
			verts, num, edges, adjl = self.openFile(TESTCASE_PATH+"/nosharp.", filetype)
		except:
			logger.info("assertNoSharp passed")

	def assertMultiSharp(self, filetype):
		# Check when there are multiple sharp symbol.
		try:
			verts, num, edges, adjl = self.openFile(TESTCASE_PATH+"/multisharp.", filetype)
		except ValueError:
			logger.info("assertMultiSharp passed")

	def perform_testing(self, filetype):
		self.assertValid(filetype)
		# self.assertDuplicate(filetype)
		# self.assertEmptyDecs(filetype)
		self.assertInsufAttArg(filetype)
		self.assertExcessArg(filetype)
		# self.assertUndeclared(filetype)
		if (filetype == "apx"):
			self.assertInvalidType(filetype)
		# 	self.assertMixedUp(filetype)
		if (filetype == "tgf"):
			self.assertNoSharp(filetype)
		# 	self.assertMultiSharp(filetype)
		logger.info("Passed all tests")

if __name__ == '__main__':
	unittest.main()