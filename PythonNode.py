# PythonNode.py

from TreeNode import TreeNode
from PLLParser import parsePLL

class PythonNode(TreeNode):

	def __init__(self, label):
		TreeNode.__init__(self, label)

	def append(self, text):
		node = parsePLL(text, asTree="Python", constr=PythonNode)
		self.appendNode(node.firstChild)
		return self    # allow chaining

	def appendChild(self, text):
		node = parsePLL(text, asTree="Python", constr=PythonNode)
		self.appendChildNode(node.firstChild)
		return self    # allow chaining

	def execute(self, hGlobals=None, hLocals=None):
		programText = self.asFragment()
		exec(programText, hGlobals, hLocals)

	def printProgram(self):
		print()
		print('='*48)
		print('-'*15 + '  Python Program  ' + '-'*15)
		print('='*48)
		print(self.asFragment())
		print('='*48)
