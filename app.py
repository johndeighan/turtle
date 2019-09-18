# app.py

from tkutils import getAppWindow
import tkinter as tk

def cmdExit():
	root.destroy()

root = getAppWindow('''
		App
			*title
				My App
			*menubar
				File
					New
					Open...
					Save
					-----
					Exit
			*layout
				col
					label This is a test
						background = light blue
					label of my app
						background = light green
					row
						label X
						label Y
					button  Exit
		''', globals())

tk.mainloop()

