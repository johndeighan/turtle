# GUIApplication.py

from abc import ABC, abstractmethod
import re

from TreeNode import TreeNode
from PLLParser import parsePLL

root = None   # disallow creating more than one instance
reWidgetDef = re.compile(r'^\s*(\S+)\s*(.*)$')

class GUIApplication(ABC):

	def __init__(self, appDesc):
		global root

		if root:
			raise Exception("You can only create one GUIApplication")
		self.hWidgets = {}   # widgets saved by name

		# --- Parse the app description into an appNode, and a hash
		#     holding any tagged subtrees
		(appNode, hSubTrees) = parsePLL(appDesc)

		root = self.getMainWindow(appNode, hSubTrees)
		self.mainWindow = root

		if getattr(self, 'centerWindow', None):
			self.centerWindow()

	# ---------------------------------------------------------------------------

	@abstractmethod
	def getMainWindow(self, node, hSubTrees):

		assert isinstance(node, TreeNode)
		assert isinstance(hSubTrees, dict)

	# ---------------------------------------------------------------------------

	@abstractmethod
	def run(self):
		raise Exception("You cannot call super().run()")

	# ---------------------------------------------------------------------------

	@abstractmethod
	def exit(self):
		pass

	# ------------------------------------------------------------------------

	@abstractmethod
	def getWidgetConstructor(self, type):
		pass

	# ---------------------------------------------------------------------------

	def widgetFromNode(self, window, node):

		global reWidgetDef

		hOptions = self.getNodeOptions(node)

		# --- Extract widget type and label
		result = reWidgetDef.search(node['label'])
		if result:
			type = result.group(1)
			label = hOptions['label'] = result.group(2)
		else:
			raise Exception(f"Invalid Widget Def: '{traceStr(label)}'")

		return self.newWidget(window, type, hOptions)

	# ------------------------------------------------------------------------

	def getNodeOptions(self, node):
		# --- Override this if your options syntax is not 'x = val'

		return node.getOptions()

	# ------------------------------------------------------------------------

	def newWidget(self, parent, type, hOptions={}, *, debug=False):

		if debug:
			print(f"newWidget('{type}')")
			for (key, value) in hOptions.items():
				print(f"   {key} => '{value}'")

		constructor = self.getWidgetConstructor(type)
		if not constructor:
			raise Exception(f"Unknown widget type: '{type}'")

		# --- For some odd reason, in Python, you don't supply a
		#     self parameter in this case
		widget = constructor(parent, hOptions)
		if 'name' in hOptions:
			self.saveWidget(hOptions['name'], widget)
		return widget

	# ------------------------------------------------------------------------

	def saveWidget(self, name, widget):
		# --- This is called for any widget created
		#     that has a 'name' key

		if name in self.hWidgets:
			raise Exception(f"saveWidget(): There is already a widget"
								 f" named '{name}'")
		self.hWidgets[name] = widget

	# ------------------------------------------------------------------------

	def findWidgetByName(self, name):

		if name in self.hWidgets:
			return self.hWidgets[name]
		else:
			raise Exception(f"findWidgetByName():"
								 f" There is no widget named '{name}'")
