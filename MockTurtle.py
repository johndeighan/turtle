# MockTurtle.py

from math import degrees, radians, sin, cos

# --- The mock turtle, like the real turtle, remembers its
#     position and orientation. It also keeps track of the
#     min and max x and y position

class MockTurtle:
	def __init__(self, debug=False):

		self.debug = debug

		# --- h is heading in degrees, where 0 is upward
		(self.x, self.y, self.h) = (0, 0, 0)

		(self.xmin, self.ymin, self.xmax, self.ymax) = (0, 0, 0, 0)
		if debug: print()
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

