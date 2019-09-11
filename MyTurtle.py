# MyTurtle.py

from turtle import TurtleScreen, RawTurtle, TK

from TurtleNode import TurtleNode
from PLLParser import parsePLL
from PythonNode import PythonNode

class MyTurtle(RawTurtle):
	def __init__(self, canvas, screen):
		self.canvas = canvas
		canvas.config(bg='#cccccc')
		self.screen = screen

		super().__init__(screen)
		self.speed(1)  # turtle.cfg doesn't appear to support this
		self.lSaved = []

	def execute(self, program):
		turtleTree = parsePLL(program,
		                      asTree='Turtle', constr=TurtleNode)
		assert isinstance(turtleTree, TurtleNode)

		pythonTree = turtleTree.pythonify()
		assert isinstance(pythonTree, PythonNode)

		hGlobals = {
			'turtle': self,
			}
		pythonTree.execute(hGlobals)

	def clear(self):
		self.screen.reset()

	def moveTo(self, x, y):
		self.lSaved.append([
				self.xcor(),
				self.ycor(),
				self.heading(),
				])
		self._move(x, y)

	def restore(self, show=True):
		if len(self.lSaved) == 0:
			raise Exception("restore(): Save stack is empty")

		lState = self.lSaved.pop()
		self._move(*lState, show)

	def center(self):
		canvas = self.canvas

	def mainloop(self):
		self.screen.mainloop()

	# --- Private functions

	def _move(self, x, y, head=None, show=True):
		self.hideturtle()
		self.penup()
		self.setpos(x, y)
		if head:
			self.setheading(head)
		else:
			self.setheading(0)
		self.pendown()
		if show:
			self.showturtle()

