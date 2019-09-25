# notebook.py

import smokesignal as ss
from TKApplication import TKApplication

app = TKApplication('''
		Notebook Test App
			*menubar
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
		''')

@ss.on('exit')
def ExitApp(event):
	app.exit()

notebook = app.findWidgetByName('notebook')
assert notebook
assert isinstance(notebook, NotebookWidget)

app.run()
