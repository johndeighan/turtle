# TurtleEnv.py

import os, sys, re
from more_itertools import ilen
from turtle import TurtleScreen, TK

from tkutils import getAppWindow
from TKWidgets import findWidgetByName
from TKTurtle import TKTurtle
from TurtleNode import TurtleNode
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
				*Title
					Turtle Graphics
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
							name = editor
							width = 32
							height = 36
							sticky = n
							file = turtle.txt
						Canvas
							name = canvas
							width = 648
							height = 648
							sticky = n
			'''

		root = getAppWindow(appDesc, globals())

		editor = findWidgetByName('editor')
		assert editor

		canvas = findWidgetByName('canvas')
		assert canvas

		turtle = TKTurtle(canvas)
		assert turtle

	def mainloop(self):
		turtle.mainloop()

# ---------------------------------------------------------------------------
#       Menu Item Handler Functions
# ---------------------------------------------------------------------------

def cmdNew():
	editor.setValue('')
	filename = None

def cmdSave():
	print("MENU save()")

def cmdClear():
	turtle.clear()

def cmdExecute():
	turtle.execute(editor.getValue())

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
