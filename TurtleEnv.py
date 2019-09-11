# TurtleEnv.py

import os, sys, re
from turtle import TurtleScreen, RawTurtle, TK

from myutils import rmPrefix
from tkutils import centerWindow, addMenuBar
from TreeNode import TreeNode
from MyTurtle import MyTurtle
from TurtleNode import TurtleNode
from PLLParser import parsePLL
from ProgramEditor import ProgramEditor
from PythonNode import PythonNode

class TurtleEnv:
	env = None        # a class level variable, refer to as TurtleEnv.env

	def __init__(self,
	             speed=1,
	             bgcolor='#dddddd',
	             ):

		if TurtleEnv.env:
			raise Exception("You cannot create multiple TurtleEnv's")
		TurtleEnv.env = self

		root = self.root = TK.Tk()
		root.resizable(False, False)
		root.title('Turtle Graphics')

		addMenuBar(root, '''
				MenuBar
					File
						New
						Open...
						Save
						Save As...
						Save a Copy As...
						-----
						Exit
					Edit
						Cut
						Copy
						Paste
						-----
						Preferences...
					Turtle
						Clear
						Execute
					Help
						About...
				''',
				handlers=sys.modules[__name__])  # pass in module object

		editor = self.editor = ProgramEditor(root, defFileName='turtle.txt')
		editor.grid(0, 0)

		canvas = self.canvas = TK.Canvas(root, width="640", height="580")
		canvas.grid(row=0, column=1)

		screen = self.screen = TurtleScreen(canvas)
		screen.bgcolor(bgcolor)

		centerWindow(root)

		self.turtle = MyTurtle(screen)

	def mainloop(self):
		self.screen.mainloop()

	def execute(self):
		if not TurtleEnv.env:
			raise Exception("No Turtle Environment has been set up yet")

		turtleTree = parsePLL(self.editor.getText(),
		                      asTree='Turtle', constr=TurtleNode)
		assert isinstance(turtleTree, TurtleNode)

		pythonTree = turtleTree.pythonify()
		assert isinstance(pythonTree, PythonNode)

		hGlobals = {
			'turtle': self.turtle,
			}
		pythonTree.execute(hGlobals)

	def pythonify(self, node, *, debug=False):
		assert isinstance(node, TreeNode)
		matches = reCommand.search(node['label'])
		if matches:
			(cmd, tail) = matches.groups()
			if debug:
				print(f"CMD:  '{cmd}'")
				print(f"TAIL: '{tail}'")

			# --- Check of required children are missing, or
			#     children exist that should not be there
			if cmd in setNoChildren and node.hasChildren():
				raise Exception(f"Command {cmd} cannot have children")
			if cmd in setHasChildren and not node.hasChildren():
				raise Exception(f"Command {cmd} must have children")

			# --- Handle each command
			if cmd == 'Turtle':
				pythonTree = PythonNode('Python')
				for child in node.children():
					newChild = self.pythonify(child)
					newChild.makeChildOf(pythonTree)
				return pythonTree
			elif cmd == 'move':
				return PythonNode(f"turtle.forward({tail})")
			elif cmd == 'turn':
				return PythonNode(f"turtle.right({tail})")
			else:
				return PythonNode(f"Unknown Command: '{cmd}'")

		else:
			raise Exception(f"Unknown turtle statement: '{label}'")
		return newNode

# ---------------------------------------------------------------------------
#       Menu Item Handler Functions
# ---------------------------------------------------------------------------

def cmdNew():
	TurtleEnv.env.editor.clear()
	filename = None

def cmdSave():
	print("MENU save()")

def cmdClear():
	TurtleEnv.env.screen.reset()

def cmdExecute():
	TurtleEnv.env.execute()

def cmdExit():
	if TurtleEnv.env and TurtleEnv.env.root:
		TurtleEnv.env.root.destroy()    # this will cleanly exit the app

# ---------------------------------------------------------------------------
#                 UNIT TESTS
# ---------------------------------------------------------------------------

def test_1():
	myenv = TurtleEnv()
	myenv.mainloop()
