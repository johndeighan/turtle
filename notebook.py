# notebook.py

import tkinter as tk
from tkutils import getAppWindow
from TKWidgets import (getNewWidget, findWidgetByName, removeSavedWidgets,
		NotebookWidget)

def cmdExit():
	global root
	root.destroy()

root = getAppWindow('''
		App
			*Title
				Test of Notebook widget
			*MenuBar
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
						Turtle
							name = turtle
							width = 320
							height = 320
							background = light blue
						notebook
							name = notebook
					button  Exit
					button Draw
					button Reset
		''', globals())

notebook = findWidgetByName('notebook')
assert notebook
assert isinstance(notebook, NotebookWidget)

tk.mainloop()
