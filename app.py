# app.py

from tkutils import getAppWindow, go, stop
import tkinter as tk

root = None

def main():
	global root
	root = getAppWindow('''
				App
					*Title
						My App
					*MenuBar
						File
							New
							Open...
							Save
							-----
							Exit
					*Layout
						col
							label   This is a test
							label   of my app
							checkbox Please check me!
							radiobutton Please radio me!
							editField Enter a name
								text = Sample Name
							button  Exit
				''', globals())

	tk.mainloop()

def cmdExit():
	global root
	root.destroy()

main()
