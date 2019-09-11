# ProgramEditor.py

import os, sys, re
import tkinter as tk
import tkinter.font as tkfont

dir = os.getcwd()
path = None

class ProgramEditor:
	def __init__(self, parent, *, defFileName=None, width=36, height=36):
		global dir, path

		widget = self.textWidget = tk.Text(parent,
		                                   width=width, height=height)
		self.font = tkfont.Font(font=widget['font'])
		widget.config(tabs=self.font.measure('   '))

		if defFileName:
			try:
				path = os.path.join(dir, defFileName)
				with open(path) as fh:
					text = fh.read()
					self.setText(text)
			except IOError:
				path = None

	def grid(self, row=0, column=0):
		self.textWidget.grid(row=row, column=column)

	def clear(self):
		self.textWidget.delete('1.0', 'end')

	def setText(self, text):
		self.textWidget.insert('1.0', text)

	def getText(self):
		return self.textWidget.get('1.0', 'end')
