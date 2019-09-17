# TurtleEnv.py

import os, sys, re
from more_itertools import ilen
from turtle import TurtleScreen
import tkinter as tk

from tkutils import getAppWindow
from TKWidgets import (findWidgetByName, ProgramEditorWidget,
                       TurtleWidget)
from TurtleNode import TurtleNode
from PythonNode import PythonNode
from PLLParser import parsePLL

# --- global to this file
rootWindow   = None
wTurtleCode   = None
wPythonCode   = None
wTurtle = None

class TurtleEnv:

	def __init__(self):

		global rootWindow, wTurtleCode, wPythonCode, wTurtle
		if wTurtle:
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
						Reset
						Execute
					Help
						About...
				*Layout
					row
						label Turtle Program
						label Python Program
						label Turtle Environment

						====================

						ProgramEditor
							name = turtleCode
							width = 25
							height = 36
							sticky = n
							file = turtle.txt
						ProgramEditor
							name = pythonCode
							width = 40
							height = 36
							sticky = n
						Turtle
							name = turtle
							width = 648
							height = 648
							sticky = n
							background = light gray
			'''

		rootWindow = getAppWindow(appDesc, globals())

		wTurtleCode = findWidgetByName('turtleCode')
		assert wTurtleCode
		assert isinstance(wTurtleCode, ProgramEditorWidget)

		wPythonCode = findWidgetByName('pythonCode')
		assert wPythonCode
		assert isinstance(wPythonCode, ProgramEditorWidget)

		wTurtle = findWidgetByName('turtle')
		assert wTurtle
		assert isinstance(wTurtle, TurtleWidget)

# ---------------------------------------------------------------------------
#       Menu Item Handler Functions
# ---------------------------------------------------------------------------

def cmdNew():
	global wTurtleCode

	wTurtleCode.clear()
	filename = None

def cmdSave():
	print("MENU save()")

def cmdReset():
	global wTurtle

	wTurtle.reset()

def cmdExecute():
	global wTurtleCode, wPythonCode, wTurtle

	assert isinstance(wTurtleCode, ProgramEditorWidget)

	turtleCode = wTurtleCode.getValue()
	assert type(turtleCode) == str

	if len(turtleCode) == 0:
		print("No Turtle Code to execute!")
		return

	(turtleNode, hSubTrees) = parsePLL(turtleCode, constructor=TurtleNode)
	assert isinstance(turtleNode, TurtleNode)

	pythonNode = turtleNode.pythonify()
	assert isinstance(pythonNode, PythonNode)

	pythonCode = pythonNode.asString()
	assert type(pythonCode) == str

	assert isinstance(wPythonCode, ProgramEditorWidget)
	wPythonCode.setValue(pythonCode)  # put code in python widget

	pythonNode.execute({'turtle': wTurtle})

def cmdExit():
	global rootWindow

	if rootWindow:
		rootWindow.destroy()    # this will cleanly exit the app

# ---------------------------------------------------------------------------
#                 UNIT TESTS
# ---------------------------------------------------------------------------

def test_1():
	myenv = TurtleEnv()
	tk.mainloop()
