# tkutils.py

import sys, re
from turtle import TK

from myutils import rmPrefix, reSep, getMethod, cleanup_testcode
from PLLParser import parsePLL

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
		window,        # the window to add the menubar to, or None
		str,           # string description of the menu
		*,             # --- following arguments must be called by name
		handlers=None, # a class or module (class methods won't get self)
		debug=False,
		tk=TK):

	menubar = None
	if window:
		window.option_add('*tearOff', False)   # no tearoff menus
		menubar = tk.Menu(window)

	# --- I don't think we need to call rmPrefix() ---
	tree = parsePLL(rmPrefix(str), debug=False)
	if tree['label'] != 'MenuBar':
		raise Exception("Top level label in menu bar must be 'MenuBar'")

	for child in tree.children():
		addMenu(menubar, handlers, child)

	if menubar:
		window['menu'] = menubar
	return menubar

# ---------------------------------------------------------------------------

def addMenu(parent, handlers, node):

	label = node['label']
	isSep = reSep.match(label)

	if node.hasChildren():
		if isSep:
			raise Exception("separator cannot have children")
		menu = TK.Menu(parent)
		parent.add_cascade(menu=menu, label=label)
		for child in node.children():
			addMenu(menu, handlers, child)
	elif isSep:
		parent.add_separator()
	else:
		func = None
		if handlers:
			name = getCmdMethodName(label)
			func = getMethod(handlers, name)
			if func:
				parent.add_command(label=label, command=func)
			else:
				parent.add_command(label=label, state=TK.DISABLED)
		else:
			func = lambda: print(f"Invoke MENU ITEM '{label}'")
			parent.add_command(label=label, command=func)

# ---------------------------------------------------------------------------

def getCmdMethodName(str):

	newstr = re.sub(r'[^A-Za-z0-9]+', '', str)
	return 'cmd' + newstr

# ---------------------------------------------------------------------------
#                     UNIT TESTS
# ---------------------------------------------------------------------------

def test_0():
	assert getCmdMethodName('New Program') == 'cmdNewProgram'
	assert getCmdMethodName('About...') == 'cmdAbout'
	assert getCmdMethodName('A New Menu Item') == 'cmdANewMenuItem'
	assert getCmdMethodName('? A New Menu Item...') == 'cmdANewMenuItem'


def test_1():
	root = TK.Tk()
	root.title('Menu Test')

	test_str = '''
			MenuBar
				Exit
				File      # <---
					New
					Open...
					Close
					-----
					Save
					-----
					Exit'''
	addMenuBar(root, test_str, debug=True)

	root.mainloop()
	root.quit()

cleanup_testcode(globals())   # remove unit tests when not testing
