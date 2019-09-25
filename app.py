# app.py

import smokesignal as ss
from TKApplication import TKApplication

app = TKApplication('''
		Turtle Graphics
			*menubar
				File
					Exit
						emit = exit
			*layout
				col
					label This is a test of my Turtle Graphics Package
						background = light blue
					label of my app
						background = light green
					canvas
						emit = draw
						name = canvas
					row
						button Draw
							emit = draw
						button  Exit
							emit = exit
		''')

@ss.on('exit')
def ExitApp(event):
	app.exit()

@ss.on('draw')
def Draw(event):
	canvas = app.findWidgetByName('canvas')
	assert canvas
	canvas.create_line( 25,  25, 225,  25)
	canvas.create_line(225,  25, 225, 225)
	canvas.create_line(225, 225,  25, 225)
	canvas.create_line( 25, 225,  25,  25)

app.run()


'''
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
'''
