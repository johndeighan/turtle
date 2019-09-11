# TurtleNode.py

import sys, re

from myutils import rmPrefix
from TreeNode import TreeNode
from PythonNode import PythonNode
from PLLParser import parsePLL

reCommand = re.compile(r'^([A-Za-z]+)(?:\s+(.*))?$')
setNoChildren  = frozenset(('move','turn'))
setHasChildren = frozenset(('turtle','at','repeat'))

class TurtleNode(TreeNode):

	def __init__(self, label):
		TreeNode.__init__(self, label)

	def execute(self, hGlobals=None, hLocals=None):
		programText = self.asFragment()
		exec(programText, hGlobals, hLocals)

	def parse(self, *, debug=False):
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

	def pythonify(self, *, debug=False):
		assert isinstance(self, TurtleNode)
		(cmd, lArgs) = self.parse()
		if debug:
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
		if cmd == 'turtle':
			newNode = PythonNode('Python')
			for child in self.children():
				newChild = child.pythonify().makeChildOf(newNode)
		elif cmd == 'move':
			newNode = PythonNode(f"turtle.forward({lArgs[0]})")
		elif cmd == 'turn':
			newNode = PythonNode(f"turtle.right({lArgs[0]})")
		elif cmd == 'at':
			# --- Save current position and heading
			newNode = PythonNode('save_pos = turtle.pos()')
			newNode.append(f'''
					save_heading = turtle.heading()
					#
					# --- Set new position and heading
					turtle.hideturtle()
					turtle.penup()
					turtle.setpos({lArgs[0]}, {lArgs[1]})
					turtle.setheading(0)
					turtle.pendown()
					turtle.showturtle()
					''')

			for child in self.children():
				newNode.appendNode(child.pythonify())
			newNode.append(f'''
					# --- Restore saved position and heading
					turtle.hideturtle()
					turtle.penup()
					turtle.setpos(save_pos)
					turtle.setheading(save_heading)
					turtle.pendown()
					turtle.showturtle()
					''')
		elif cmd == 'repeat':
			newNode = PythonNode(f"for i in range({lArgs[0]}):")
			for child in self.children():
				child.pythonify().makeChildOf(newNode)
		else:
			raise Exception(f"Unknown Command: '{cmd}'")
		return newNode

	def printProgram(self):
		print()
		print('='*48)
		print('-'*15 + '  Turtle Program  ' + '-'*15)
		print('='*48)
		print(self.asFragment())
		print('='*48)

def parseTurtle(s):
	return parsePLL(s, asTree='Turtle', constr=TurtleNode)

def parseAndCompare(s, *, debug=False):
	turtleTree = parseTurtle(s)
	turtleTree.printProgram()
	pythonTree = turtleTree.pythonify()
	pythonTree.printProgram()
	return pythonTree

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
