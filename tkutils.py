# tkutils.py

import sys, re
import tkinter as TK

from TreeNode import TreeNode
from myutils import (rmPrefix, isSeparator, getMethod, cleanup_testcode,
                     splitAssignment)
from PLLParser import parsePLL
from ProgramEditor import ProgramEditor

hWidgets = {}   # maps user provided names to widgets created in this file
                # adding widget with duplicate name raises an exception

# ---------------------------------------------------------------------------

def saveWidget(name, widget):

	if name in hWidgets:
		raise Exception(f"saveWidget(): There is already a widget"
		                f" named '{name}'")
	hWidgets[name] = widget

# ---------------------------------------------------------------------------

def getWidget(name):

	if name in hWidgets:
		return hWidgets[name]
	else:
		raise Exception(f"getWidget(): There is no widget named '{name}'")

# ---------------------------------------------------------------------------

def getAppWindow(appDesc, hHandlers={}, *, tk=TK):

	(appTree, hSubTrees) = parsePLL(appDesc)

	appWindow = tk.Tk()
	appWindow.resizable(False, False)
	title = hSubTrees['Title'].firstChild['label']
	appWindow.title(title)
	saveWidget('root', appWindow)

	addMenuBar(appWindow, hSubTrees['MenuBar'], hHandlers)
	addContent(appWindow, hSubTrees['Layout'],  hHandlers)

	centerWindow(appWindow)  # must grid everything before calling

	return appWindow

# ---------------------------------------------------------------------------

def addContent(
		window,         # the window to add the menubar to, or None
		layoutTree,     # tree description of the window content
		hHandlers=None, # a dictionary containing functions as values
		*,              # --- following arguments must be called by name
		debug=False,
		tk=TK):

	assert layoutTree['label'] == 'Layout'
	for child in layoutTree.children():
		layoutType = child['label']
		if layoutType == 'row':
			col = 0
			for widgetTree in child.children():
				widget = createWidget(window, widgetTree, TK)
				widget.grid(row = 0, column=col)
				col += 1
		elif layoutType == 'col':
			pass
		elif layoutType == 'grid':
			pass
		else:
			raise Exception(f"addContent():"
			                f" unknown layout type: '{layoutType}'")

# ---------------------------------------------------------------------------

def createWidget(parent, tree, tk=TK):

	# --- Accumulate all named options
	hOptions = {}
	for child in tree.children():
		label = child['label']
		try:
			(key, value) = splitAssignment(label)
			hOptions[key] = value
		except Exception as ex:
			pass

	type = tree['label']
	widget = None
	if (type == 'ProgramEditor'):
		defFile = hOptions.get('file', 'turtle.txt')
		widget = ProgramEditor(parent, defFileName=defFile)
	elif (type == 'Canvas'):
		w = hOptions.get('width', 640)
		h = hOptions.get('height', 580)
		bgcolor = hOptions.get('bg', '#cccccc')
		widget = tk.Canvas(parent, bg=bgcolor, width=w, height=h)
	else:
		raise Exception(f"Unknown widget type: '{type}'")

	if 'name' in hOptions:
		saveWidget(hOptions['name'], widget)

	return widget

# ---------------------------------------------------------------------------

def addMenuBar(
		window,         # the window to add the menubar to, or None
		menuTree,       # tree description of the menu
		hHandlers=None, # a dictionary containing functions as values
		*,              # --- following arguments must be called by name
		debug=False,
		tk=TK):

	assert isinstance(menuTree, TreeNode)
	menubar = None
	if window:
		window.option_add('*tearOff', False)   # no tearoff menus
		menubar = tk.Menu(window)

	assert isinstance(menuTree, TreeNode)
	if menuTree['label'] != 'MenuBar':
		raise Exception("Top level label in menu bar must be 'MenuBar'")

	for subtree in menuTree.children():
		assert isinstance(subtree, TreeNode)
		addMenu(menubar, subtree, hHandlers)

	if menubar:
		window['menu'] = menubar
	return menubar

# ---------------------------------------------------------------------------

def addMenu(parent, node, hHandlers, *,
            tk=TK):

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
		name = getCmdFuncName(label)
		func = None
		if hHandlers and name in hHandlers:
			func = hHandlers[getCmdFuncName(label)]
			if func:
				parent.add_command(label=label, command=func)
			else:
				parent.add_command(label=label, state=tk.DISABLED)
		else:
			func = lambda: print(f"Invoke MENU ITEM '{label}'")
			parent.add_command(label=label, command=func)

# ---------------------------------------------------------------------------

def getCmdFuncName(str):

	newstr = re.sub(r'[^A-Za-z0-9]+', '', str)
	return 'cmd' + newstr

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
	root = TK.Tk()
	root.title('Menu Test')

	test_str = '''
			MenuBar
				Help
				File      # <---
					New
					Open...
					Close
					-----
					Save
					-----
					Exit'''
	def doExit():
		root.destroy()

	hHandlers = {
		'cmdExit': doExit,
		}
	(tree, h) = parsePLL(test_str)
	addMenuBar(root, tree, debug=True, hHandlers=hHandlers)

	root.mainloop()
	root.quit()

def cmdExit():
	global root
	if root:
		root.destroy()    # this will cleanly exit the app

cleanup_testcode(globals())   # remove unit tests when not testing
