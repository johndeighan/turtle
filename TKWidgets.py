# TKWidgets.py

import os, sys
import tkinter as tk
from tkinter import ttk, font as tkfont
from pprint import pprint

# --- Generally supported keys in hOptions:
#        label - a text string
#        text  - user editable text
#        handler - function to handle clicking

current_dir = os.getcwd()    # current working directory

# --- This maps user provided names to widgets created in this file
#     adding widget with duplicate name raises an exception
hSavedWidgets = {}

_hConstructors = {}   # string name => widget constructor

# ---------------------------------------------------------------------------

def findWidgetByName(name):

	if name in hSavedWidgets:
		return hSavedWidgets[name]
	else:
		raise Exception(f"getSavedWidget():"
		                f" There is no widget named '{name}'")

# ---------------------------------------------------------------------------

def getNewWidget(type, parent, hOptions, *, debug=False):

	if debug:
		print(f"getWidget('{type}')")
		for (key, value) in hOptions.items():
			print(f"   {key} => '{value}'")

	constructor = _hConstructors.get(type, None)
	if not constructor:
		raise Exception(f"Unknown widget type: '{type}'")
	return constructor(parent, hOptions)

# ---------------------------------------------------------------------------

class _Widget():

	def __init__(self, parent, hOptions):
		super().__init__()
		self.parent = parent
		self.tkWidget = None     # holds reference to a tk widget, if any
		self.handler = None
		if 'sticky' in hOptions:
			self.sticky = hOptions['sticky']
		else:
			self.sticky = None

		# --- If the widget has a name, save it in a dictionary
		#     so it can later be retrieved by name

		if 'name' in hOptions:
			_saveWidget(hOptions['name'], self)

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

		# --- You can specify a handler for events on the widget
		#     It's required for the ButtonWidget

		if 'handler' in hOptions:
			func = hOptions['handler']
			if not callable(func):
				raise Exception("Handler must be callable")
			self.handler = hOptions['handler']
		else:
			self.handler = None

		self.tkWidget = self.newTKWidget(parent, hOptions)
		self.configWidget(hOptions)
		self.initialize(hOptions)

	def newTKWidget(parent, hOptions):
		raise Exception("You must define a newTKWidget() method!")

	def allowConfig(self, option):
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
			if self.allowConfig(key):
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

	def invoke(self):
		if 'handler' in self and self.handler:
			if not callable(func):
				raise Exception("Handler must be callable")
			return self.handler()
		else:
			raise Exception("invoke(): No handler defined")

# ---------------------------------------------------------------------------

def _saveWidget(name, widget):
	# --- This is called for any widget created
	#     that has a 'name' key

	if name in hSavedWidgets:
		raise Exception(f"_saveWidget(): There is already a widget"
		                f" named '{name}'")
	hSavedWidgets[name] = widget

# ---------------------------------------------------------------------------
#             Individual Widgets
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
		if not self.handler:
			# --- Create one that simply prints that the button was activated
			self.handler = lambda: print(f"Button {label} activated")
		return ttk.Button(parent, text=label, command=self.handler)

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
		return ttk.Checkbutton(parent, text=self.label, command=self.handler)

	def setValue(self, value):
		raise Exception("Cannot call setValue() on a checkbox widget")

	def getValue(self):
		raise Exception("Cannot call getValue() on a checkbox widget")

# ---------------------------------------------------------------------------

class RadioButtonWidget(_Widget):

	def newTKWidget(self, parent, hOptions):
		return ttk.Radiobutton(parent, text=self.label,
		                               command=self.handler)

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

		global current_dir

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

	def getCanvas(self):
		return self.tkWidget

# ---------------------------------------------------------------------------

_hConstructors = {
	'label': LabelWidget,
	'button': ButtonWidget,
	'editField': EditFieldWidget,
	'checkbox': CheckBoxWidget,
	'radiobutton': RadioButtonWidget,
	'ProgramEditor': ProgramEditorWidget,
	'Canvas': CanvasWidget,
	}

# ---------------------------------------------------------------------------
#                 Unit Tests
# ---------------------------------------------------------------------------

test_root = None

def test_1():
	import tkutils
	global test_root

	test_root = tkutils.getAppWindow('''
			App
				*Title
					My App
				*MenuBar
					File
						Exit
				*Layout
					col
						label   This is a test
							sticky = w
							background = red
						label   of my app
							sticky = e
							background = light blue
						ProgramEditor
							height = 16
							file = turtle.txt
						Canvas
							width = 160
							height = 160
						editField Name
							value = John Deighan
						button  Exit
			''', globals())

	tk.mainloop()

# ----- Handlers -----

def cmdExit():
	global test_root
	test_root.destroy()
