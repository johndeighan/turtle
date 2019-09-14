# TurtleEnv.py

import os, sys, re
from more_itertools import ilen
from turtle import TurtleScreen, TK

from tkutils import centerWindow, addMenuBar
from MyTurtle import MyTurtle
from TurtleNode import TurtleNode
from ProgramEditor import ProgramEditor
from PLLParser import parsePLL

# --- global to this file
root   = None
editor = None
turtle = None

class TurtleEnv:

	def __init__(self):

		global root, editor, turtle
		if turtle:
			raise Exception("You cannot create multiple TurtleEnv's")

		appDesc = '''
			App
				*MenuBar
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
				*Layout
					row
						ProgramEditor
							turtle.txt
						Canvas
							640 x 580
			'''

		(app, hSubTrees) = parsePLL(appDesc)
		menuBar = hSubTrees['MenuBar']
		layout  = hSubTrees['Layout']
		assert ilen(app.descendents())     == 27
		assert ilen(menuBar.descendents()) == 20
		assert ilen(layout.descendents())  ==  6

		root = TK.Tk()
		root.resizable(False, False)
		root.title('Turtle Graphics')

		addMenuBar(root, menuBar, globals())

		editor = ProgramEditor(root, defFileName='turtle.txt')
		editor.grid(row=0, column=0)

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
