# MyTurtle.py

from turtle import TurtleScreen, RawTurtle, TK

class MyTurtle(RawTurtle):
	def __init__(self, screen):
		super().__init__(screen)
		self.speed(1)
		self.shape('turtle')
		self.resetHeading()
		self.lSaved = []

	def resetHeading(self):
		self.setheading(90)

	def _move(self, x, y, head=None):
		self.hideturtle()
		self.penup()
		self.setpos(x, y)
		if head:
			self.setheading(head)
		else:
			self.resetHeading()
		self.showturtle()
		self.pendown()

	def moveTo(self, x, y):
		self.lSaved.append([
				self.xcor(),
				self.ycor(),
				self.heading(),
				])
		self._move(x, y)

	def restore(self):
		if len(self.lSaved) == 0:
			raise Exception("restore(): Save stack is empty")

		lState = self.lSaved.pop()
		self._move(*lState)
		self.pendown()
