# TurtleNode.py

import sys, re

from myutils import rmPrefix
from TreeNode import TreeNode
from PythonNode import PythonNode
from PLLParser import parsePLL

reCommand = re.compile(r'^([A-Za-z]+)(?:\s+(.*))?$')
setNoChildren  = frozenset(('move','turn'))
setHasChildren = frozenset(('at','repeat'))

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
			if tail == None:
				tail = ''
			tail.rstrip()
			lArgs = tail.split(',')
			return (cmd.lower(), lArgs)
		else:
			raise Exception(f"Unknown turtle statement: '{label}'")

	def pythonify(self, *, debug=False, trace=False):
		# --- self is a TurtleNode
		#     returns and equivalent PythonNode
		if debug:
			self.printFragment()

		assert not self.parent
		pythonNode = self.pythonifyNode(trace=trace)

		# --- pythonify and append siblings
		prev = self
		node = self.nextSibling
		while node:
			pythonNode.appendNode(node.pythonifyNode(trace=trace, prev=prev))
			prev = node
			node = node.nextSibling
		if debug:
			pythonNode.printFragment()
		return pythonNode

	def pythonifyNode(self, *, debug=False, trace=False, prev=None):
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

		# --- Handle each command, creating pythonNode
		#     NOTE: turtle will be a TurtleWidget
		pythonNode = None
		if cmd == 'move':
			pythonNode = PythonNode(f"turtle.move({lArgs[0]})")
		elif cmd == 'turn':
			pythonNode = PythonNode(f"turtle.turn({lArgs[0]})")
		elif cmd == 'at':
			(xpos, ypos) = (lArgs[0], lArgs[1])

			# --- Save current position and heading, unless the previous node
			#     was an 'at' node
			prevAt = False
			if prev:
				(prevCmd, prevlArgs) = prev.parseNode()
				if prevCmd == 'at':
					prevAt = True

			if prevAt:
				pythonNode = PythonNode(f'turtle.moveTo({xpos}, {ypos})')
			else:
				pythonNode = PythonNode(f'turtle.saveState()')
				pythonNode.appendNode(
						PythonNode(f'turtle.moveTo({xpos}, {ypos})')
						)
			prev = None
			for child in self.children():
				pythonNode.appendNode(child.pythonifyNode(prev=self))
				prev = child

			# --- If next node is an 'at' node, don't restore
			if self.nextSibling:
				(nextCmd, nextlArgs) = self.nextSibling.parseNode()
				if nextCmd != 'at':
					pythonNode.append(f'turtle.restoreState()')
			else:
				pythonNode.append(f'turtle.restoreState()')
		elif cmd == 'repeat':
			pythonNode = PythonNode(f"for i in range({lArgs[0]}):")
			for child in self.children():
				child.pythonifyNode().makeChildOf(pythonNode)
		else:
			raise Exception(f"Unknown Command: '{cmd}'")
		return pythonNode

	def printProgram(self):
		print()
		print('='*48)
		print('-'*15 + '  Turtle Program  ' + '-'*15)
		print('='*48)
		print(self.asString())
		print('='*48)
