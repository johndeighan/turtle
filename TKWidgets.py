# TKWidgets.py

import os, sys
from math import hypot
import tkinter as tk
from tkinter import ttk, font as tkfont
from pprint import pprint
from turtle import TurtleScreen, RawTurtle
import smokesignal as ss

from PLLParser import parsePLL
from TurtleNode import TurtleNode
from PythonNode import PythonNode
from WidgetStorage import saveWidget, findWidgetByName

# --- Generally supported keys in hOptions:
#        label - a text string
#        text  - user editable text
#        emit - name of signal to emit if activated

# ---------------------------------------------------------------------------

class _Widget():

	def __init__(self, parent, hOptions={}):
		super().__init__()
		self.parent = parent
		self.tkWidget = None     # holds reference to a tk widget, if any
		if 'sticky' in hOptions:
			self.sticky = hOptions['sticky']
		else:
			self.sticky = None

		# --- If the widget has a name, save it in a dictionary
		#     so it can later be retrieved by name

		if 'name' in hOptions:
			saveWidget(hOptions['name'], self)

		# --- You can specify an initial value for the widget

		if 'value' in hOptions:
			self.initValue = hOptions['value']
		else:
			self.initValue = None

		# --- Some widgets support a label, which is
		#     different than the value managed by the widget
		#     (though it's the same thing for a LabelWidget)

		if 'label' in hOptions:
			self.label = hOptions['label']
		else:
			self.label = '<Missing Label>'

		self.tkWidget = self.newTKWidget(parent, hOptions)
		self.configWidget(hOptions)
		self.initialize(hOptions)

	def newTKWidget(parent, hOptions):
		raise Exception("You must define a newTKWidget() method!")

	def allowOption(self, option):
		return option in {
			'anchor',
			'font',
			'width',
			'height',
			'foreground',
			'background',
			'cursor',
			}

	def configWidget(self, hOptions):
		# --- By default, assume it's a standard Tk widget
		assert self.tkWidget
		assert isinstance(self.tkWidget, tk.Widget)
		hTkConfig = {}
		for (key, value) in hOptions.items():
			if self.allowOption(key):
				hTkConfig[key] = value
		self.tkWidget.config(**hTkConfig)

	def initialize(self, hOptions):
		pass

	def grid(self, row, col):
		if self.sticky:
			self.tkWidget.grid(row=row, column=col, sticky=self.sticky)
		else:
			self.tkWidget.grid(row=row, column=col)

	def setValue(self, value):
		# --- By default, does nothing
		#     should return self to allow chaining
		return self

	def getValue(self):
		# --- By default, returns None
		return None

# ---------------------------------------------------------------------------
#             Individual Widgets
# ---------------------------------------------------------------------------

class FrameWidget(_Widget):
	# --- name 'frame'

	def newTKWidget(self, parent, hOptions):
		return ttk.Frame(parent)

# ---------------------------------------------------------------------------

class LabelWidget(_Widget):
	# --- name 'label'

	def newTKWidget(self, parent, hOptions):
		return ttk.Label(parent, text=self.label)

	# --- The value is the label

	def setValue(self, value):
		self.label = value
		return self

	def getValue(self):
		return self.label

# ---------------------------------------------------------------------------

class ButtonWidget(_Widget):
	# --- name 'button'

	def newTKWidget(self, parent, hOptions):
		label = self.label    # always set by constructor
		handler = getHandler('Button', label, hOptions)
		button = ttk.Button(parent, text=label)
		button.bind('<KeyPress-Return>', handler)
		button.bind('<Button-1>', handler)
		return button

	def setValue(self, value):
		# --- should set the value in the widget
		self.label = value
		return self

	def getValue(self):
		# --- should get the value from the widget
		return self.label

# ---------------------------------------------------------------------------

class EditFieldWidget(_Widget):
	# --- name 'editField'

	def newTKWidget(self, parent, hOptions):
		return ttk.Entry(parent, text=self.initValue)

	def setValue(self, value):
		# --- should set the value in the widget
		self.label = value
		return self

	def getValue(self):
		# --- should get the value from the widget
		return self.label

# ---------------------------------------------------------------------------

class CheckBoxWidget(_Widget):

	def newTKWidget(self, parent, hOptions):
		return ttk.Checkbutton(parent, text=self.label)

	def setValue(self, value):
		raise Exception("Cannot call setValue() on a checkbox widget")

	def getValue(self):
		raise Exception("Cannot call getValue() on a checkbox widget")

# ---------------------------------------------------------------------------

class RadioButtonWidget(_Widget):

	def newTKWidget(self, parent, hOptions):
		return ttk.Radiobutton(parent, text=self.label)

	def setValue(self, value):
		raise Exception("Cannot call setValue() on a radio button widget")

	def getValue(self):
		raise Exception("Cannot call getValue() on a radio button widget")

# ---------------------------------------------------------------------------

class ProgramEditorWidget(_Widget):

	def newTKWidget(self, parent, hOptions):

		width = hOptions.get('width', 36)
		height = hOptions.get('height', 36)

		widget = tk.Text(parent, width=width, height=height,
		                         font=('Courier New', 12))

		# --- Set TAB stops to every 3 spaces
		self.font = tkfont.Font(font=widget['font'])
		widget.config(tabs=self.font.measure('   '))

		return widget

	def initialize(self, hOptions):

		current_dir = os.getcwd()    # current working directory
		if 'file' in hOptions:
			try:
				path = os.path.join(current_dir, hOptions['file'])
				with open(path) as fh:
					text = fh.read()
					self.setValue(text)
			except IOError:
				print(f"ERROR: Unable to load initial file")

	def clear(self):
		self.tkWidget.delete('1.0', 'end')

	def setValue(self, value):
		self.clear()
		self.tkWidget.insert('1.0', value)

	def getValue(self):
		return self.tkWidget.get('1.0', 'end')

# ---------------------------------------------------------------------------

class CanvasWidget(_Widget):

	def newTKWidget(self, parent, hOptions):
		w = hOptions.get('width', 640)
		h = hOptions.get('height', 580)
		bgcolor = hOptions.get('bg', '#cccccc')
		return tk.Canvas(parent, bg=bgcolor, width=w, height=h)

	def setValue(self, value):
		raise Exception("Cannot call setValue() on a canvas widget")

	def getValue(self):
		raise Exception("Cannot call getValue() on a canvas widget")

	def getBounds(self):
		# --- return (xmin, ymin, xmax, ymax)
		canvas = self.tkWidget
		return (-10, -10, 120, 120)

	def create_line(self, *args, **kwargs):
		self.tkWidget.create_line(*args, **kwargs)

# ---------------------------------------------------------------------------

class TurtleWidget(CanvasWidget):

	def newTKWidget(self, parent, hOptions):
		return super().newTKWidget(parent, hOptions)

	def initialize(self, hOptions):
		self.screen = TurtleScreen(self.tkWidget)
		self.tkTurtle = RawTurtle(self.screen)
		self.screen.mode('world')

		self.tkTurtle.setheading(90)

		if 'speed' in hOptions:
			self.curSpeed = int(hOptions['speed'])
		else:
			self.curSpeed = 1
		self.lSaveStack = []   # stack to save/restore state on

	def setBounds(self, xmin, ymin, xmax, ymax, padding=15):
		width = xmax - xmin
		height = ymax - ymin
		if (width > height):
			halfdiff = (width - height) / 2
			ymin -= halfdiff
			ymax += halfdiff
		else:
			halfdiff = (height - width) / 2
			xmin -= halfdiff
			xmax += halfdiff
		self.screen.setworldcoordinates(
				xmin - padding,
				ymin - padding,
				xmax + padding,
				ymax + padding,
				)

	def reset(self):
		self.screen.reset()

	def move(self, n):
		tkTurtle = self.tkTurtle
		assert isinstance(tkTurtle, RawTurtle)
		tkTurtle.speed(self.curSpeed)
		tkTurtle.forward(n)

	def turn(self, d):
		tkTurtle = self.tkTurtle
		assert isinstance(tkTurtle, RawTurtle)
		tkTurtle.speed(self.curSpeed)
		tkTurtle.right(d)

	# --- Turtle state includes these fields:
	#     xpos, ypos, heading, isvisible, isdown

	def saveState(self):

		tkTurtle = self.tkTurtle
		assert isinstance(tkTurtle, RawTurtle)
		self.lSaveStack.append([
				tkTurtle.xcor(),
				tkTurtle.ycor(),
				tkTurtle.heading(),
				tkTurtle.isvisible(),
				tkTurtle.isdown(),
				])

	def restoreState(self):

		tkTurtle = self.tkTurtle
		assert isinstance(tkTurtle, RawTurtle)
		if len(self.lSaveStack) == 0:
			raise Exception("restoreState(): No saved state to restore")
		lState = self.lSaveStack.pop()
		saved_x = lState[0]
		saved_y = lState[1]

		cur_x = tkTurtle.xcor()
		cur_y = tkTurtle.ycor()

		# --- determine whether we need to hide the turtle
		if tkTurtle.isvisible():
			dist = hypot(saved_x - cur_x, saved_y - cur_y)
			mustHide = (dist > 1)
		else:
			mustHide = False

		if mustHide:
			tkTurtle .hideturtle()

		tkTurtle.penup()
		tkTurtle.setposition(saved_x, saved_y)
		tkTurtle.setheading(lState[2])

		if lState[3] and mustHide:
			tkTurtle.showturtle()
		if lState[4]:
			tkTurtle.pendown()

	def moveTo(self, x, y):
		tkTurtle = self.tkTurtle
		tkTurtle.penup()
		tkTurtle.hideturtle()
		tkTurtle.setposition(x, y)
		tkTurtle.setheading(90)
		tkTurtle.pendown()
		tkTurtle.showturtle()

	def drawAt(self, x, y, func):

		# --- Must not draw or show movement
		tkTurtle = self.tkTurtle

		self.saveState()
		self.moveTo(x, y)
		func(self)
		self.restoreState()

# ---------------------------------------------------------------------------

class NotebookWidget(_Widget):

	def newTKWidget(self, parent, hOptions):
		tkWidget = ttk.Notebook(parent)
		plusTab = ProgramEditorWidget(tkWidget, {
				'width': 25,
				'height': 18,
				})
		tkWidget.add(plusTab.tkWidget, text='+')

		tkWidget.enable_traversal()
		n = tkWidget.index('end')
		print(f"There are {n} tabs in the Notebook")
		return tkWidget

	def allowOption(self, option):
		return option in {
			'width',
			'height',
			'padding',
			}

	def add(self, name, text):
		self.tkWidget.add(widget, text=name)

	def setValue(self, value):
		raise Exception("Cannot call setValue() on a canvas widget")

	def getValue(self):
		return self.tkWidget.tab('current')

	def numTabs(self):
		return self.tkWidget.index('end')

# ---------------------------------------------------------------------------

def getHandler(type, label, hOptions):
	# --- returns a callback function
	#     if hOptions['emit'] is defined, handler emits that signal
	#     else, handler just prints the fact this was called

	emitName = hOptions.get('emit', None)
	if emitName:
		return lambda *args, **kwargs: ss.emit(emitName, *args, **kwargs)
	else:
		return lambda *args, **kwargs: print(f"{type} '{label}' activated")

# ---------------------------------------------------------------------------
#                 Unit Tests
# ---------------------------------------------------------------------------

root = None

def test_1():
	import tkutils
	global root

	root = tkutils.getAppWindow('''
			App
				*title
					My App
				*menubar
					File
						Exit
						Draw
				*layout
					col
						label   This is a test
							sticky = w
							background = red
						label   of my app
							sticky = e
							background = light blue
						Turtle
							name = turtle
							width = 320
							height = 320
							background = light blue
						editField Name
							value = John Deighan
						button  Exit
						button Draw
						button Reset
			''', globals())

	turtle = findWidgetByName('turtle')
	assert turtle
	assert isinstance(turtle, TurtleWidget)

	tk.mainloop()

def test_2():
	import tkutils
	global root

	root = tkutils.getAppWindow('''
			App
				*title
					Test of Notebook widget
				*menubar
					File
						Exit
						Draw
				*layout
					col
						label   This is a test
							sticky = w
							background = red
						label   of my app
							sticky = e
							background = light blue
						row
							notebook
								name = notebook
							Turtle
								name = turtle
								width = 320
								height = 320
								background = light blue
						row
							button  Exit
							button Draw
							button Reset
			''', globals())

	notebook = findWidgetByName('notebook')
	assert notebook
	assert isinstance(notebook, NotebookWidget)

	tk.mainloop()

# ----- Handlers -----

def cmdDraw():
	turtle = findWidgetByName('turtle')
	turtle.drawAt(0, 0, doSquare)
	turtle.drawAt(50, 50, doSquare)

def cmdReset():
	turtle = findWidgetByName('turtle')
	turtle.reset()

def cmdExit():
	global root
	root.destroy()

def doSquare(turtle):
	for i in range(4):
		turtle.move(30)
		turtle.turn(90)
