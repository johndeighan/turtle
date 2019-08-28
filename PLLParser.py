# PLLParser.py

"""
parse a 'Python like language'
"""

import io
import re

from TreeNode import TreeNode

# --- Some pre-compiled regular expressions

reLeadWS  = re.compile(r'^\s+')
reTrailWS = re.compile(r'\s+$')
reLine    = re.compile(r'^(\t*)(.*)$')
reComment = re.compile(r'#.*$')

# ---------------------------------------------------------------------------

def parsePLL(fh, debug=False):
	numLines = 0
	root = None
	curLevel = None

	# --- Allow passing in a string
	if isinstance(fh, str):
		fh = io.StringIO(fh)

	for line in fh:
		numLines += 1

		# --- strip off any '#' and rest of the line
		line = re.sub(reComment, '', line)

		# --- string off any trailing whitespace
		line = re.sub(reTrailWS, '', line)

		# --- skip empty lines
		if line == '':
			if debug:
				print(f"LINE {numLines}:")
				print("   - skip empty line")
			continue

		# --- Determine lines's level and label
		#        (regexp match will always succeed)
		result = reLine.match(line)
		newLevel = len(result.group(1))
		label = result.group(2)

		if debug:
			print(f"LINE {numLines}: [{newLevel}] '{label}'")

		if reLeadWS.match(label):
			raise SyntaxError('Invalid Indentation')

		# --- process first non-empty line
		if not root:
			root = curNode = TreeNode(label)
			curLevel = newLevel
			if debug:
				print(f"   - root node set to '{label}'")
			continue

		diff = newLevel - curLevel

		if diff > 1:
			# --- continuation line - append to current node's label
			if debug:
				print('   - continuation')

			curNode['label'] += ' ' + label

			# --- Don't change curLevel

		elif diff == 1:
			# --- create new child node
			if debug:
				assert isinstance(curNode, TreeNode)
				print(f"   - new child of {curNode.asString()}")
			assert not curNode.firstChild
			curNode = TreeNode(label, childOf=curNode)
			curLevel += 1

		elif diff < 0:    # i.e. newLevel < curLevel
			# --- Move up -diff levels, then create sibling node
			if debug:
				n = -diff
				desc = 'level' if n==1 else 'levels'
				print(f'   - go up {n} {desc}')
			while (curLevel > newLevel):
				curLevel -= 1
				curNode = curNode.parent
				assert curNode
			curNode = TreeNode(label, siblingOf=curNode)
		elif diff == 0:
			# --- create new sibling node
			if debug:
				print(f"   - new sibling of {curNode.asString()}")
			assert not curNode.nextSibling
			curNode = TreeNode(label, siblingOf=curNode)

		else:
			raise Exception("What! This cannot happen")

	return root

# ---------------------------------------------------------------------------

# To Do:
#    1. Allow spaces for indentation
