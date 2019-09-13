# TurtleNode.py

import sys, re

from myutils import rmPrefix
from TreeNode import TreeNode
from PythonNode import PythonNode
from PLLParser import parsePLL

reCommand = re.compile(r'^([A-Za-z]+)(?:\s+(.*))?$')
setNoChildren  = frozenset(('move','turn','center'))
setHasChildren = frozenset(('turtle','at','repeat'))

class TurtleNode(TreeNode):

	def __init__(self, label, lHereDoc=None):
		TreeNode.__init__(self, label, lHereDoc)

	def execute(self, hGlobals=None, hLocals=None):
		programText = self.asString()
		exec(programText, hGlobals, hLocals)

	def parseNode(self, *, debug=False):
		label = self['label']
		matches = reCommand.search(label)
		if matches:
			(cmd, tail) = matches.groups()
			if tail == None: tail = ''
			tail.rstrip()
			lArgs = tail.split(',')
			return (cmd.lower(), lArgs)
		else:
			raise Exception(f"Unknown turtle statement: '{label}'")

	def pythonifyProgram(self, *, debug=False, trace=False):
		if debug:
			self.printFragment()

		pythonNode = self.pythonifyNode(trace=trace)

		# --- pythonify and append siblings
		node = self.nextSibling
		while node:
			pythonNode.appendNode(node.pythonifyNode(trace=trace))
			node = node.nextSibling
		if debug:
			pythonNode.printFragment()
		return pythonNode

	def pythonifyNode(self, *, debug=False, trace=False):
		# --- debug causes turtle & python trees to be printed
		#     trace causes verbose tracing output

		assert isinstance(self, TurtleNode)
		(cmd, lArgs) = self.parseNode()
		if trace:
			print(f"CMD:  '{cmd}'")
			print(f"ARGS: '{lArgs}'")

		# --- Check of required children are missing, or
		#     children exist that should not be there
		if cmd in setNoChildren and self.hasChildren():
			raise Exception(f"Command {cmd} cannot have children")
		if cmd in setHasChildren and not self.hasChildren():
			raise Exception(f"Command {cmd} must have children")

		# --- Handle each command, creating newNode
		newNode = None
		if cmd == 'move':
			newNode = PythonNode(f"turtle.forward({lArgs[0]})")
		elif cmd == 'turn':
			newNode = PythonNode(f"turtle.right({lArgs[0]})")
		elif cmd == 'center':
			newNode = PythonNode(f"turtle.center()")
		elif cmd == 'at':
			# --- Save current position and heading
			newNode = PythonNode(f'turtle.moveTo({lArgs[0]}, {lArgs[1]})')
			for child in self.children():
				newNode.appendNode(child.pythonifyNode())

			# --- If next node is an 'at' node, don't re-show the turtle
			reshow = 'True'
			if self.nextSibling:
				(nextCmd, nextlArgs) = self.nextSibling.parseNode()
				if nextCmd == 'at':
					reshow = 'False'

			newNode.append(f'turtle.restore(show={reshow})')
		elif cmd == 'repeat':
			newNode = PythonNode(f"for i in range({lArgs[0]}):")
			for child in self.children():
				child.pythonifyNode().makeChildOf(newNode)
		else:
			raise Exception(f"Unknown Command: '{cmd}'")
		return newNode

	def printProgram(self):
		print()
		print('='*48)
		print('-'*15 + '  Turtle Program  ' + '-'*15)
		print('='*48)
		print(self.asString())
		print('='*48)

def parseAndCompare(s, *, debug=False):
	(turtleNode,) = parsePLL(s, constructor=TurtleNode)
	assert isinstance(turtleNode, TurtleNode)
	turtleNode.printProgram()

	pythonNode = turtleNode.pythonifyNode()
	assert isinstance(pythonNode, PythonNode)
	pythonNode.printProgram()

	return pythonNode

# ---------------------------------------------------------------------------
#                 UNIT TESTS
# ---------------------------------------------------------------------------

def test_1():
	pythonTree = parseAndCompare('''
		at 9, 9
			repeat 4
				move 5
				turn 15
		''')
