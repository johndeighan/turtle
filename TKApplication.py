# TKApplication.py

import os, sys, re
import tkinter as tk
from tkinter import ttk, font as tkfont
from pprint import pprint
from turtle import TurtleScreen, RawTurtle
import smokesignal as ss

from myutils import isSeparator
from GUIApplication import GUIApplication
from PLLParser import parsePLL
from TreeNode import TreeNode
from TurtleNode import TurtleNode
from PythonNode import PythonNode
import TKWidgets

# --- Generally supported keys in hOptions:
#        label - a text string
#        text  - user editable text
#        handler - function to handle clicking

current_dir = os.getcwd()    # current working directory
reWidgetDef = re.compile(r'^\s*(\S+)\s*(.*)$')

class TKApplication(GUIApplication):

	def __init__(self, appDesc):   # we probably don't need this
		super().__init__(appDesc)

	# ------------------------------------------------------------------------

	def getMainWindow(self, appNode, hSubTrees, *, debug=False):
		# --- base constructor will call this to create the main window

		root = tk.Tk()
		root.resizable(False, False)
		root.title(appNode['label'])
		root.option_add('*tearOff', False)   # no tearoff menus

		# --- Set up the menu bar, if any
		menuBarNode = hSubTrees.get('menubar', None)
		if menuBarNode:
			self.addMenuBar(root, menuBarNode)

		# --- layout window content, if any
		layoutNode = hSubTrees.get('layout', None)
		if layoutNode:
			self.addLayout(root, layoutNode)

		return root    # will become self.mainWindow

	# ---------------------------------------------------------------------------

	def run(self):
		tk.mainloop()

	# ---------------------------------------------------------------------------

	def exit(self):
		self.mainWindow.destroy()

	# ------------------------------------------------------------------------

	def addMenuBar(
			self,
			window,   # the window to add the menubar to, or None
			node,     # tree description of the menu
			*,        # --- following arguments must be called by name
			debug=False):

		assert isinstance(node, TreeNode)
		if debug:
			node.printTree("Menu Bar")

		self.menubar = tk.Menu(window)
		for subtree in node.trueChildren():
			self.addMenu(self.menubar, subtree)

		# --- Set as the window's menu bar
		window['menu'] = self.menubar

	# ------------------------------------------------------------------------

	def addMenu(
			self,
			parent,
			node,
			*,
			debug=False):

		assert isinstance(node, TreeNode)
		label = node['label']
		hOptions = node.getOptions()
		emitName = hOptions.get('emit', None)
		isSep = isSeparator(label, '-')

		if debug:
			print(f"CALL addMenu('{label}')")

		if node.hasTrueChildren():
			if debug:
				print(f"...has children")
			if isSep:
				raise Exception("separator cannot have children")
			menu = tk.Menu(parent)
			parent.add_cascade(menu=menu, label=label)
			for child in node.trueChildren():
				self.addMenu(menu, child)
		elif isSep:
			if debug:
				print(f"...is separator")
			parent.add_separator()
		else:
			if debug:
				print(f"...emitName = '{emitName}'")

			if emitName:
				# --- All handlers will expect an "event" argument,
				#     so we just pass None here
				handler = lambda *args, **kwargs: (
					ss.emit(emitName, None, *args, **kwargs)
					)
			else:
				handler = lambda *args, **kwargs: (
					print(f"{type} '{label}' activated")
					)
			# handler = TKWidgets.getHandler('Menu Item', label, hOptions)
			assert handler and callable(handler)

			# handler = lambda: ss.emit(emitName)
			parent.add_command(label=label, command=handler)

	# ------------------------------------------------------------------------

	def addLayout(
			self,
			window,   # the window to add content to, or None
			node,     # tree description of the window content
			*,        # --- following arguments must be called by name
			debug=False):

		if debug:
			node.printTree("Layout")

		child = node.firstChild
		if child:
			label = child['label']
			if label == 'row':
				self.addRow(window, child, debug=debug)
			elif label == 'col':
				self.addCol(window, child, debug=debug)
			else:
				raise Exception(f"Bad layout label: '{label}'")

	# ------------------------------------------------------------------------

	def addRow(self, window, rowNode, *, debug=False):

		if debug:
			rowNode.printTree('Row')

		# --- We already know that rowNode's label is 'row'
		r, c = 0, 0
		for child in rowNode.children():
			label = child['label']
			if isSeparator(label, '-'):
				c += 1
			elif isSeparator(label, '='):
				r += 1
				c = 0
			else:
				if label == 'row':
					widget = self.newWidget(window, 'frame', debug=debug)
					self.addRow(widget.tkWidget, child)
				elif label == 'col':
					widget = self.newWidget(window, 'frame', debug=debug)
					self.addCol(widget.tkWidget, child)
				else:
					widget = self.widgetFromNode(window, child)
				widget.grid(r, c)
				c += 1

	# ------------------------------------------------------------------------

	def addCol(self, window, colNode, *, debug=False):

		if debug:
			colNode.printTree('Col')

		# --- We already know that rowNode's label is 'col'
		r, c = 0, 0
		for child in colNode.children():
			label = child['label']
			if isSeparator(label, '-'):
				r += 1
			elif isSeparator(label, '='):
				c += 1
				r = 0
			else:
				if label == 'row':
					widget = self.newWidget(window, 'frame', debug=debug)
					self.addRow(widget.tkWidget, child)
				elif label == 'col':
					widget = self.newWidget(window, 'frame', debug=debug)
					self.addCol(widget.tkWidget, child)
				else:
					widget = self.widgetFromNode(window, child)
				widget.grid(r, c)
				r += 1

	# ------------------------------------------------------------------------

	def centerWindow(self, window=None):

		if not window:
			window = self.mainWindow
		window.update_idletasks()

		# Gets the requested values of the height and width.
		windowWidth = window.winfo_reqwidth()
		windowHeight = window.winfo_reqheight()

		# Gets both half the screen width/height and window width/height
		positionRight = int(window.winfo_screenwidth()/2 - windowWidth/2)
		positionDown = int(window.winfo_screenheight()/2 - windowHeight/2)

		# --- Positions the window in the center of the page.
		window.geometry("+{}+{}".format(positionRight, positionDown))

	# ------------------------------------------------------------------------

	def getWidgetConstructor(self, type):

		return {
			'frame':       TKWidgets.FrameWidget,
			'label':       TKWidgets.LabelWidget,
			'button':      TKWidgets.ButtonWidget,
			'editfield':   TKWidgets.EditFieldWidget,
			'checkbox':    TKWidgets.CheckBoxWidget,
			'radiobutton': TKWidgets.RadioButtonWidget,
			'canvas':      TKWidgets.CanvasWidget,
			'editor':      TKWidgets.ProgramEditorWidget,
			'turtle':      TKWidgets.TurtleWidget,
			'notebook':    TKWidgets.NotebookWidget,
			}.get(type, None)

# ---------------------------------------------------------------------------
#                 Unit Tests
# ---------------------------------------------------------------------------

