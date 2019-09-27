# NodeTest.py

import sys, re, pytest, collections
from more_itertools import ilen

from myutils import rmPrefix, isAllWhiteSpace

class NodeTest(collections.abc.MutableMapping):

	def __init__(self, label):
		super().__init__()

		self.hData = {
			'label': label,
			}

		self.parent = None
		self.nextSibling = None
		self.firstChild = None

	# ------------------------------------------------------------------------
	#    Multiple ways to build up a tree structure
	# ------------------------------------------------------------------------

	def makeChildOf(self, node):
		assert isinstance(node, TreeNode)

		self.parent = node

		lastChild = node.firstChild
		if lastChild != None:
			while lastChild.nextSibling:
				lastChild = lastChild.nextSibling

			# --- Now, lastChild has no nextSibling
			lastChild.nextSibling = self
		else:
			node.firstChild = self
		return self    # allow chaining

	def makeSiblingOf(self, node):
		assert isinstance(node, TreeNode)
		assert not self.parent
		# assert node.parent

		parent = node.parent
		cur = node
		while cur.nextSibling:
			cur = cur.nextSibling
			assert cur.parent == parent
		cur.nextSibling = self
		self.parent = parent
		return self    # allow chaining

	def appendNode(self, newNode):
		node = self
		while node.nextSibling:
			node = node.nextSibling
		node.nextSibling = newNode
		return self    # allow chaining

	def appendChildNode(self, newNode):
		if self.firstChild:
			self.firstChild.appendNode(newNode)
		else:
			self.firstChild = newNode
		return self    # allow chaining

	def append(self, label):
		self.appendNode(TreeNode(label))
		return self    # allow chaining

	def appendChild(self, label):
		self.appendChildNode(TreeNode(label))
		return self    # allow chaining

	# ------------------------------------------------------------------------
	# --- These methods allow us to treat a TreeNode object as a dict

	def __getitem__(self, key):
		return self.hData[key]

	def __setitem__(self, key, value):
		self.hData[key] = value

	def __delitem__(self, key):
		del self.hData[key]

#	def __contains__(self, key):
#		return key in self.hData

	def __len__(self):
		return (self.hData)

	def __iter__(self):
		return iter(self.hData)

#	def keys(self):
#		return self.hData.keys()

#	def get(self, name, defVal=None):
#		return self.hData.get(name, defVal)

#	def set(self, name, value):
#		return self.hData.set(name, value)

	# ------------------------------------------------------------------------
	# --- These methods allow us to iterate over all of a
	#     TreeNode's children or descendents

	def hasChildren(self):

		return self.firstChild != None

	def numChildren(self):

		n = 0
		node = self.firstChild
		while node:
			++n
			node = node.nextSibling
		return n

	def children(self):

		child = self.firstChild
		while (child):
			yield child
			child = child.nextSibling

	def numNodes(self):

		return ilen(self.descendents())

	def asString(self, level=0, indent='\t'):

		s = ''
		cur = self
		while cur:
			for (level,node) in cur.descendents():
				s += (indent * level) + node.hData['label'] + '\n'
			cur = cur.nextSibling
		return s

# ---------------------------------------------------------------------------
#                   UNIT TESTS
# ---------------------------------------------------------------------------
