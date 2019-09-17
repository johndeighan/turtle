# TKTurtle.py

from math import hypot
from turtle import TurtleScreen, RawTurtle, TK

from TurtleNode import TurtleNode
from PLLParser import parsePLL
from PythonNode import PythonNode

class TKTurtle(RawTurtle):
	def __init__(self, canvasWidget):
		self.canvas = canvasWidget.getCanvas()
		self.canvas.config(bg='#cccccc')
		self.screen = screen = TurtleScreen(self.canvas)

		super().__init__(screen)
		self.lSaved = []

	def execute(self, program, *, speed=1):
		(turtleNode, h) = parsePLL(program, constructor=TurtleNode)
		assert isinstance(turtleNode, TurtleNode)

		pythonNode = turtleNode.pythonifyProgram()
		assert isinstance(pythonNode, PythonNode)

		self.speed(speed)
		pythonNode.execute({'turtle': self})

	def clear(self):
		self.screen.reset()

	def moveTo(self, x, y):
		# --- Save current position, to enable restoring later
		self.lSaved.append([
				self.xcor(),
				self.ycor(),
				self.heading(),
				])
		self._moveTo(x, y)

	def restore(self, show=True):
		if len(self.lSaved) == 0:
			raise Exception("restore(): Save stack is empty")

		lState = self.lSaved.pop()
		self._moveTo(*lState, show)

	def center(self):
		canvas = self.canvas

	def mainloop(self):
		self.screen.mainloop()

	# --- Private functions

	def _moveTo(self, x, y, head=None, show=True):
		# --- should NEVER draw a line
		#     turtle should be hidden during move

		curx = self.xcor()
		cury = self.ycor()

		# --- determine whether we need to hide the turtle
		if self.isvisible():
			dist = hypot(x - curx, y - cury)
			hide = (dist > 1)
		else:
			hide = False

		if hide:
			self.hideturtle()

		self.penup()
		self.setpos(x, y)
		self.pendown()

		if hide or show:
			self.showturtle()

		if head:
			self.setheading(head)
		else:
			self.setheading(0)

