# TurtleEnv.py

import os, sys, re
from more_itertools import ilen
from turtle import TurtleScreen
import tkinter as tk
from tkinter import messagebox

# --- Create alias
showinfo = messagebox.showinfo

from tkutils import getAppWindow
from TKWidgets import (findWidgetByName, ProgramEditorWidget,
                       TurtleWidget)
from TurtleNode import TurtleNode
from PythonNode import PythonNode
from PLLParser import parsePLL
from TurtleLanguage import compile

# --- global to this file
rootWindow   = None
wTurtleCode   = None
wPythonCode   = None
wTurtleEnv = None

class TurtleEnv:

	def __init__(self):

		global rootWindow, wTurtleCode, wPythonCode, wTurtleEnv
		if wTurtleEnv:
			raise Exception("You cannot create multiple TurtleEnv's")

		appDesc = '''
			App
				*title
					Turtle Graphics
				*menubar
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
						Compile
						Execute
					Help
						About...
				*layout
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
							speed = 2
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

		wTurtleEnv = findWidgetByName('turtle')
		assert wTurtleEnv
		assert isinstance(wTurtleEnv, TurtleWidget)

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
	global wTurtleEnv

	wTurtleEnv.reset()

def cmdCompile():
	global wTurtleCode, wPythonCode

	assert isinstance(wTurtleCode, ProgramEditorWidget)

	turtleCode = wTurtleCode.getValue()
	assert type(turtleCode) == str

	nChars = len(turtleCode)
	print(f"LEN turtleCode = {nChars}")
	if len(turtleCode) <= 1:
		showinfo(message="No Turtle Code to execute!")
		wPythonCode.setValue('')
		return

	pythonCode = compile(turtleCode)

	assert isinstance(wPythonCode, ProgramEditorWidget)
	wPythonCode.setValue(pythonCode)  # put code in python widget

def cmdExecute():
	global wTurtleCode, wPythonCode, wTurtleEnv

	cmdCompile()
	pythonCode = wPythonCode.getValue()
	assert type(pythonCode) == str
	exec(pythonCode, {'turtle': wTurtleEnv})

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
