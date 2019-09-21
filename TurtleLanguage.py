# TurtleLanguage.py

from PLLParser import parsePLL
from TurtleNode import TurtleNode
from PythonNode import PythonNode
from MockTurtle import MockTurtle

def compile(turtleCode):
	# --- returns Python Code as a string

	assert type(turtleCode) == str
	(tNode, hSubTrees) = parsePLL(turtleCode, TurtleNode)
	assert isinstance(tNode, TurtleNode)

	pNode = tNode.pythonify()
	assert isinstance(pNode, PythonNode)
	return pNode.asString()

def computeBounds(turtleCode, pythonCode=None):
	if not pythonCode:
		pythonCode = compile(turtleCode)
	mock = MockTurtle()
	exec(pythonCode, {'turtle': mock})
	return mock.bounds()

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
