# tkutils.py

import sys, re
import tkinter as tk
from tkinter import ttk, font

from TreeNode import TreeNode
from myutils import (rmPrefix, isSeparator, getMethod, cleanup_testcode,
                     traceStr, firstWordOf, splitAssignment)
from PLLParser import parsePLL
from TKWidgets import getNewWidget, findWidgetByName, FrameWidget
from WidgetStorage import (removeSavedWidgets, numSavedWidgets,
                           findWidgetByName)
# ---------------------------------------------------------------------------

def getAppWindow(appDesc, hHandlers=None, *, debug=False):

	removeSavedWidgets()
	assert numSavedWidgets() == 0
	(appTree, hSubTrees) = parsePLL(appDesc)

	appWindow = tk.Tk()

	appWindow.resizable(False, False)
	title = hSubTrees['title'].firstChild['label']
	appWindow.title(title)

	menuBarNode = hSubTrees['menubar']
	layoutNode = hSubTrees['layout']

	addMenuBar(appWindow, menuBarNode, hHandlers)
	addLayout(appWindow, layoutNode,  hHandlers, debug=debug)

	centerWindow(appWindow)  # must grid everything before calling

	return appWindow

# ---------------------------------------------------------------------------

def addLayout(
		window,         # the window to add content to, or None
		layoutNode,     # tree description of the window content
		hHandlers=None, # a dictionary containing functions as values
		*,              # --- following arguments must be called by name
		debug=False):

	assert layoutNode, "Missing layoutNode parameter"

	if debug:
		layoutNode.printTree("Layout")

	label = layoutNode['label']
	msg = f"Invalid layoutNode label '{label}'"
	assert layoutNode['label'] == 'layout', msg

	n = layoutNode.numChildren()
	assert layoutNode.firstChild
	assert not layoutNode.firstChild.nextSibling
#	assert n == 1, f"Invalid layoutNode: {n} children"

	child = layoutNode.firstChild
	label = child['label']
	assert label in ('row','col'), f"Invalid layoutNode child: '{label}'"

	if label == 'row':
		addRow(window, child, hHandlers, debug=debug)
	else:
		addCol(window, child, hHandlers, debug=debug)

# ---------------------------------------------------------------------------

def addRow(window, rowNode, hHandlers, *, debug=False):

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
				widget = FrameWidget(window)
				addRow(widget.tkWidget, child, hHandlers)
			elif label == 'col':
				widget = FrameWidget(window)
				addCol(widget.tkWidget, child, hHandlers)
			else:
				widget = createWidget(window, child, hHandlers)
			widget.grid(r, c)
			c += 1

# ---------------------------------------------------------------------------

def addCol(window, colNode, hHandlers, *, debug=False):

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
				widget = FrameWidget(window)
				addRow(widget.tkWidget, child, hHandlers)
			elif label == 'col':
				widget = FrameWidget(window)
				addCol(widget.tkWidget, child, hHandlers)
			else:
				widget = createWidget(window, child, hHandlers)
			widget.grid(r, c)
			r += 1

# ---------------------------------------------------------------------------

reWidgetDef = re.compile(r'^\s*(\S+)\s*(.*)$')

def createWidget(window, node, hHandlers={}):

	# --- Accumulate all named options for the widget
	hOptions = {}
	for child in node.children():
		try:
			# --- label will always be there
			(key, value) = splitAssignment(child['label'])
			hOptions[key] = value
		except Exception as ex:
			pass

	# --- Extract widget type and label
	result = reWidgetDef.search(node['label'])
	if result:
		type = result.group(1)
		label = hOptions['label'] = result.group(2)
	else:
		raise Exception(f"Invalid Widget Def: '{traceStr(label)}'")

	handler = getHandlerFunc(label, hHandlers)
	if handler:
		hOptions['handler'] = handler

	return getNewWidget(type, window, hOptions)

# ---------------------------------------------------------------------------

def getCmdFuncName(str):

	newstr = re.sub(r'[^A-Za-z0-9]+', '', str)
	return 'cmd' + newstr

# ---------------------------------------------------------------------------

def getHandlerFunc(label, hHandlers=None, force=False):

	if not label or (type(label) != str) or (len(label) == 0):
		if force:
			raise Exception("getHandlerFunc() No label with force = True")
		else:
			return None
	name = getCmdFuncName(label)
	if (hHandlers
			and name in hHandlers
			and hHandlers[name]
			and callable(hHandlers[name])
			):
		return hHandlers[name]
	if force:
		return lambda: print(f"MISSING HANDLER '{name}' (label = '{label}')")
	return None

# ---------------------------------------------------------------------------

def addMenuBar(
		window,         # the window to add the menubar to, or None
		menuBarNode,    # tree description of the menu
		hHandlers=None, # a dictionary containing functions as values
		*,              # --- following arguments must be called by name
		debug=False):

	assert menuBarNode
	if debug:
		menuBarNode.printTree("Menu Bar")

	assert isinstance(menuBarNode, TreeNode)
	menubar = None
	if window:
		window.option_add('*tearOff', False)   # no tearoff menus
		menubar = tk.Menu(window)

	assert isinstance(menuBarNode, TreeNode)
	if menuBarNode['label'] != 'menubar':
		raise Exception("Top level label in menu bar must be 'menubar'")

	for subtree in menuBarNode.children():
		assert isinstance(subtree, TreeNode)
		addMenu(menubar, subtree, hHandlers)

	if menubar:
		window['menu'] = menubar
	return menubar

# ---------------------------------------------------------------------------

def addMenu(parent, node, hHandlers={}):

	assert isinstance(node, TreeNode)
	label = node['label']
	isSep = isSeparator(label)

	if node.hasChildren():
		if isSep:
			raise Exception("separator cannot have children")
		menu = tk.Menu(parent)
		parent.add_cascade(menu=menu, label=label)
		for child in node.children():
			addMenu(menu, child, hHandlers)
	elif isSep:
		parent.add_separator()
	else:
		func = getHandlerFunc(label, hHandlers)
		parent.add_command(label=label, command=func)

# ---------------------------------------------------------------------------

def centerWindow(window):

	window.update_idletasks()

	# Gets the requested values of the height and width.
	windowWidth = window.winfo_reqwidth()
	windowHeight = window.winfo_reqheight()

	# Gets both half the screen width/height and window width/height
	positionRight = int(window.winfo_screenwidth()/2 - windowWidth/2)
	positionDown = int(window.winfo_screenheight()/2 - windowHeight/2)

	# --- Positions the window in the center of the page.
	window.geometry("+{}+{}".format(positionRight, positionDown))

# ---------------------------------------------------------------------------
#                     UNIT TESTS
# ---------------------------------------------------------------------------

def test_0():
	assert getCmdFuncName('New Program') == 'cmdNewProgram'
	assert getCmdFuncName('About...') == 'cmdAbout'
	assert getCmdFuncName('A New Menu Item') == 'cmdANewMenuItem'
	assert getCmdFuncName('? A New Menu Item...') == 'cmdANewMenuItem'


def test_1():
	root = tk.Tk()
	root.title('Menu Test')

	test_str = '''
			menubar
				File      # <---
					New
					Open...
					Close
					-----
					Save
					-----
					Exit
				Help
					About...
			'''
	def doExit():
		root.destroy()

	(tree, h) = parsePLL(test_str)
	addMenuBar(root, tree, hHandlers={'cmdExit': doExit})

	root.mainloop()
	root.quit()

cleanup_testcode(globals())   # remove unit tests when not testing
