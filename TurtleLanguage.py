# TurtleLanguage.py

from math import degrees, radians, sin, cos

from PLLParser import parsePLL
from TurtleNode import TurtleNode
from PythonNode import PythonNode

def compile(turtleCode):
	# --- returns Python Code as a string

	assert type(turtleCode) == str
	(tNode, hSubTrees) = parsePLL(turtleCode, TurtleNode)
	assert isinstance(tNode, TurtleNode)

	pNode = tNode.pythonify()
	assert isinstance(pNode, PythonNode)
	return pNode.asString()

def computeBounds(turtleCode):
	pythonCode = compile(turtleCode)
	result = exec(pythonCode, {'turtle': MockTurtle()})
	print(result)
	return (0, 0, 10, 10)

# --- The mock turtle, like the real turtle, remembers its
#     position and orientation. It also keeps track of the
#     min and max x and y position

class MockTurtle:
	def __init__(self, debug=False):

		self.debug = debug

		# --- h is heading in degrees, where 0 is upward
		(self.x, self.y, self.h) = (0, 0, 0)

		(self.xmin, self.ymin, self.xmax, self.ymax) = (0, 0, 0, 0)
		print()
		self.printPos()

	def printPos(self):
		if self.debug:
			print(f"MOCK ({format(self.x, '.2f')}, {format(self.y, '.2f')})")

	def move(self, dist):
		(x, y, h) = (self.x, self.y, self.h)
		rads = radians(h)
		newx = self.x + (dist * sin(rads))
		newy = self.y + (dist * cos(rads))
		self.moveTo(newx, newy)

	def turn(self, deg):
		self.h += deg
		self.printPos()

	def moveTo(self, x, y):
		self.x = x
		self.y = y
		self.update()
		self.printPos()

	def update(self):
		if self.x < self.xmin: self.xmin = self.x
		if self.y < self.ymin: self.ymin = self.y

		if self.x > self.xmax: self.xmax = self.x
		if self.y > self.ymax: self.ymax = self.y

	def bounds(self, decPlaces=2):
		return (
				round(self.xmin, decPlaces),
				round(self.ymin, decPlaces),
				round(self.xmax, decPlaces),
				round(self.ymax, decPlaces),
				)

	def printBounds(self):
		(xmin, ymin, xmax, ymax) = self.bounds()
		print(f"X = {xmin} .. {xmax}")
		print(f"Y = {ymin} .. {ymax}")

	def saveState(self):
		pass

	def restoreState(self):
		pass

# ---------------------------------------------------------------------------
#                 UNIT TESTS
# ---------------------------------------------------------------------------

def test_1():
	# --- Test the MockTurtle
	mock = MockTurtle()
	mock.move(10)
	mock.turn(45)
	mock.move(10)

	(xmin, ymin, xmax, ymax) = mock.bounds()
	assert xmin == 0
	assert ymin == 0
	assert xmax == 7.07
	assert ymax == 17.07

	assert 1 == 1

def test_2():
	# --- Test the MockTurtle
	mock = MockTurtle()
	mock.move(15)
	mock.turn(45)
	mock.move(10)
	mock.turn(-90)
	mock.move(100)
	mock.turn(180)
	mock.move(150)

	(xmin, ymin, xmax, ymax) = mock.bounds()
	assert xmin == -63.64
	assert ymin == -13.28
	assert xmax == 42.43
	assert ymax == 92.78

	assert 1 == 1

def not_test_1():

	(xmin, ymin, xmax, ymax) = computeBounds('''
			move 10
			turn 90
			move 10
			''')
	assert xmin == 0
	assert ymin == 0
	assert xmax == 10
	assert ymax == 10
