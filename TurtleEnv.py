# TurtleEnv.py

import os, sys, re
from turtle import TurtleScreen, TK

from tkutils import centerWindow, addMenuBar
from MyTurtle import MyTurtle
from TurtleNode import TurtleNode
from ProgramEditor import ProgramEditor

# --- global to this file
root   = None
editor = None
turtle = None

class TurtleEnv:

	def __init__(self):

		global root, editor, turtle
		if turtle:
			raise Exception("You cannot create multiple TurtleEnv's")

		root = TK.Tk()
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
				globals())

		editor = ProgramEditor(root, defFileName='turtle.txt')
		editor.grid(0, 0)

		canvas = self.canvas = TK.Canvas(root, width="640", height="580")
		canvas.grid(row=0, column=1)

		centerWindow(root)
		turtle = MyTurtle(canvas, TurtleScreen(canvas))

	def mainloop(self):
		turtle.mainloop()

# ---------------------------------------------------------------------------
#       Menu Item Handler Functions
# ---------------------------------------------------------------------------

def cmdNew():
	editor.clear()
	filename = None

def cmdSave():
	print("MENU save()")

def cmdClear():
	turtle.clear()

def cmdExecute():
	turtle.execute(editor.getText())

def cmdExit():
	global root
	if root:
		root.destroy()    # this will cleanly exit the app

# ---------------------------------------------------------------------------
#                 UNIT TESTS
# ---------------------------------------------------------------------------

def test_1():
	myenv = TurtleEnv()
	myenv.mainloop()
