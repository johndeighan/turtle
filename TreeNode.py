# TreeNode.py

import re

class TreeNode:
	# --- These are a Class variables ----------------------

	#     Modify this to affect how indentation is printed
	#     NOTE: Does NOT affect parsing

	indent = "\t"

	#     labels matching this are NOT quoted

	reSimpleLabel = re.compile(r'^[A-Za-z0-9_]+$')

	# ------------------------------------------------------

	def __init__(self, label,
			childOf=None,
			siblingOf=None,
			):

		self.hData = {
			'label': label,
			}

		self.parent = None
		self.nextSibling = None
		self.firstChild = None

		# --- You can't specify both of these
		assert not (childOf and siblingOf)

		if childOf:
			assert isinstance(childOf, TreeNode)

			self.parent = childOf

			lastChild = childOf.firstChild
			if (lastChild):
				while (lastChild.nextSibling):
					lastChild = lastChild.nextSibling

				# --- Now, lastChild has no nextSibling
				lastChild.nextSibling = self
			else:
				childOf.firstChild = self

		elif siblingOf:
			assert isinstance(siblingOf, TreeNode)
			assert siblingOf.parent
			assert not siblingOf.nextSibling

			self.parent = siblingOf.parent
			siblingOf.nextSibling = self

	# -----------------------------------------------------------
	# --- These methods allow us to treat a TreeNode object as a dict

	def __getitem__(self, key):
		return self.hData[key]

	def __setitem__(self, key, value):
		self.hData[key] = value

	def __delitem__(self, key):
		del self.hData[key]

	# -----------------------------------------------------------
	# --- These methods allow us to iterate over all of a
	#     TreeNode's children or descendents

	def children(self):
		child = self.firstChild
		while (child):
			yield child
			child = child.nextSibling

	def descendents(self, level=0):
		# --- First, visit the node itself
		yield (level, self)

		# --- Next, visit all of the node's descendents
		child = self.firstChild
		while (child):
			yield from child.descendents(level+1)
			child = child.nextSibling

	# -----------------------------------------------------------

	def printTree(self, level=0, debug=False, indent=None):
		for (level,node) in self.descendents():
			node.printNode(level, debug, indent)

	def printNode(self, level=0, debug=True, indent=None):
		indentStr = (indent or self.indent) * level
		if debug:
			print('-' * 40)
		print(f"{indentStr}{self.asString()}")
		if debug:
			print(f"{indentStr} -parent      = {nodeStr(self.parent)}")
			print(f"{indentStr} -nextSibling = {nodeStr(self.nextSibling)}")
			print(f"{indentStr} -firstChild  = {nodeStr(self.firstChild)}")
			print('-' * 40)
		return

	def asString(self):
		# --- This should also "escape" any control characters
		label = self['label']
		if self.reSimpleLabel.match(label):
			return label
		else:
			return "'" + label + "'"

# ---------------------------------------------------------------------------

def nodeStr(node):
	# --- Cannot be a method because node can be None
	#     e.g. nodeStr(somenode.nextSibling)
	if node:
		assert isinstance(node, TreeNode)
		return node.asString()
	else:
		return '(None)'
