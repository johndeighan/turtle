# hello.py

import wx
from wx import EVT_BUTTON

class MainPanel(wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)
		button = wx.Button(self, label='Press Me',
		                         pos=(100, 100))
		button.Bind(EVT_BUTTON, self.onButtonPress)

	def onButtonPress(self, event):
		print("You pressed a button")

class MainFrame(wx.Frame):
	def __init__(self):
		super().__init__(None, title='Hello, World!')
		panel = MainPanel(self)
		self.Show()

class MyApp(wx.App):
	def __init__(self):
		super().__init__(True)
		self.frame = MainFrame()

app = MyApp()
app.MainLoop()
