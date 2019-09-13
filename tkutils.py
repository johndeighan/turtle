# tkutils.py

import sys, re
from turtle import TK

from myutils import rmPrefix, reSep, getMethod, cleanup_testcode
from PLLParser import parsePLL

# ---------------------------------------------------------------------------

def getWindow(desc, *, parent=None):

	pass

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

def addMenuBar(
		window,         # the window to add the menubar to, or None
		desc,           # string description of the menu
		hHandlers=None, # a dictionary containing functions as values
		*,              # --- following arguments must be called by name
		debug=False,
		tk=TK):

	menubar = None
	if window:
		window.option_add('*tearOff', False)   # no tearoff menus
		menubar = tk.Menu(window)

	# --- I don't think we need to call rmPrefix() ---
	(tree,) = parsePLL(rmPrefix(desc), debug=False)
	if tree['label'] != 'MenuBar':
		raise Exception("Top level label in menu bar must be 'MenuBar'")

	for child in tree.children():
		addMenu(menubar, hHandlers, child)

	if menubar:
		window['menu'] = menubar
	return menubar

# ---------------------------------------------------------------------------

def addMenu(parent, hHandlers, node):

	label = node['label']
	isSep = reSep.match(label)

	if node.hasChildren():
		if isSep:
			raise Exception("separator cannot have children")
		menu = TK.Menu(parent)
		parent.add_cascade(menu=menu, label=label)
		for child in node.children():
			addMenu(menu, hHandlers, child)
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
				parent.add_command(label=label, state=TK.DISABLED)
		else:
			func = lambda: print(f"Invoke MENU ITEM '{label}'")
			parent.add_command(label=label, command=func)

# ---------------------------------------------------------------------------

def getCmdFuncName(str):

	newstr = re.sub(r'[^A-Za-z0-9]+', '', str)
	return 'cmd' + newstr

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
	addMenuBar(root, test_str, debug=True, hHandlers=hHandlers)

	root.mainloop()
	root.quit()

def cmdExit():
	global root
	if root:
		root.destroy()    # this will cleanly exit the app

cleanup_testcode(globals())   # remove unit tests when not testing
