# PythonNode.py

from TreeNode import TreeNode
from PLLParser import parsePLL

class PythonNode(TreeNode):

	def __init__(self, label, lHereDoc=None):
		TreeNode.__init__(self, label, lHereDoc)

	def append(self, text):
		(node, hSubTrees) = parsePLL(text, PythonNode)
		self.appendNode(node)
		return self    # allow chaining

	def appendChild(self, text):
		(node, hSubTrees) = parsePLL(text, PythonNode)
		self.appendChildNode(node)
		return self    # allow chaining

	def execute(self, hGlobals=None, hLocals=None, debug=False):
		programText = self.asString()
		if debug:
			self.printProgram(programText)
		exec(programText, hGlobals, hLocals)
		return programText

	def printProgram(self, text=None):
		if not text:
			text = self.asString()
		print()
		print('='*48)
		print('-'*15 + '  Python Program  ' + '-'*15)
		print('='*48)
		print(text)
		print('='*48)
