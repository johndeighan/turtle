# PLLParser.py

"""
parse a 'Python-like language'
"""

import sys, io, re, pytest
from more_itertools import ilen

from myutils import (rmPrefix, reLeadWS, reTrailWS, reAllWS,
                    traceStr, cleanup_testcode)
from TreeNode import TreeNode

# --- Some pre-compiled regular expressions

reLine     = re.compile(r'^(\t*)(.*)$')
reComment  = re.compile(r'(?<!\\)#.*$')  # ignore escaped '#' char
strHereDoc = '<<<'

# ---------------------------------------------------------------------------

def _iterator(fh, asTree=None):
	# --- Allow passing in a string
	if isinstance(fh, str):
		fh = io.StringIO(fh)

	# --- We'll need the first line to determine
	#     if there's any leading whitespace, which will
	#     be stripped from ALL lines (and therefore must
	#     be there for every subsequent line)
	line = nextNonBlankLine(fh)
	if not line:
		return

	# --- Check if there's any leading whitespace
	leadWS = ''
	leadLen = 0
	result = reLeadWS.search(line)
	if result:
		leadWS = result.group(1)
		leadLen = len(leadWS)

	# --- If asTree is set, it must be a string
	#     and it will be returned as if it were the first line, with a \n
	#     Then each subsequent line will be indented once
	if asTree:
		assert isinstance(asTree, str)
		yield asTree
		if leadWS:
			while line:
				# --- Check if the required leadWS is present
				if (line[:leadLen] != leadWS):
					raise SyntaxError("Missing leading whitespace")
				yield '\t' + line[leadLen:]
				line = nextNonBlankLine(fh)
		else:
			while line:
				yield '\t' + line
				line = nextNonBlankLine(fh)
	else:
		if leadWS:
			while line:
				# --- Check if the required leadWS is present
				if (line[:leadLen] != leadWS):
					raise SyntaxError("Missing leading whitespace")
				yield line[leadLen:]
				line = nextNonBlankLine(fh)
		else:
			while line:
				yield line
				line = nextNonBlankLine(fh)

# ---------------------------------------------------------------------------

def nextNonBlankLine(fh):
	line = fh.readline()
	if not line: return None
	line = re.sub(reComment, '', line)
	line = re.sub(reTrailWS, '', line)
	while line == '':
		line = fh.readline()
		if not line: return None
		line = re.sub(reComment, '', line)
		line = re.sub(reTrailWS, '', line)
	return line

# ---------------------------------------------------------------------------

def parsePLL(fh, debug=False, asTree=None, constr=TreeNode):
	# --- If parameter 'asTree' is provided, it becomes the top-level node
	#     and the text in fh can be a sequence of nodes
	numLines = 0
	root = None
	curLevel = None

	for line in _iterator(fh, asTree):
		numLines += 1

		if debug:
			print(f"LINE {numLines}: '{traceStr(line)}'")

		# --- Determine lines's level and label
		#        (regexp search will always succeed)
		result = reLine.search(line)
		newLevel = len(result.group(1))
		label = result.group(2)

		if debug:
			print(f"LINE {numLines}: [{newLevel}] '{label}'")

		if reLeadWS.search(label):
			raise SyntaxError('Invalid Indentation')

		# --- process first non-empty line
		if not root:
			root = curNode = constr(label)
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
				print(f"   - new child of {curNode.asDebugString()}")
			assert not curNode.firstChild
			curNode = constr(label).makeChildOf(curNode)
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
			curNode = constr(label).makeSiblingOf(curNode)
		elif diff == 0:
			# --- create new sibling node
			if debug:
				print(f"   - new sibling of {curNode.asDebugString()}")
			assert not curNode.nextSibling
			curNode = constr(label).makeSiblingOf(curNode)

		else:
			raise Exception("What! This cannot happen")

	if numLines == 0:
		if asTree:
			return constr(asTree)
		else:
			raise Exception("parsePLL(): No text to parse")

	if not root:
		raise Exception("parsePLL(): return value is empty")

	return root

# ---------------------------------------------------------------------------
#                   UNIT TESTS
# ---------------------------------------------------------------------------

test_str = '''
	top
		peach
			fuzzy
					navel
			pink
		apple
			red
'''

test_tree = parsePLL(test_str, debug=False)

def test_1():
	n = ilen(test_tree.children())
	assert n == 2

def test_2():
	n = ilen(test_tree.descendents())
	assert n == 6

def test_3():
	assert ilen(test_tree.firstChild.children()) == 2

def test_4():
	assert test_tree['label'] == 'top'

def test_5():
	assert test_tree.firstChild['label'] == 'peach'

def test_6():
	node = test_tree.firstChild.firstChild
	node['label'] == 'fuzzy navel'

# ---------------------------------------------------------------------------
# Test some invalid input

def test_7():
	s = '''
		main
			  peach
			apple
	'''
	with pytest.raises(SyntaxError):
		parsePLL(s)

def test_8():
	s = '''
main
   peach
   apple
	'''
	with pytest.raises(SyntaxError):
		parsePLL(s)

# ---------------------------------------------------------------------------
# --- Test option asTree

test_str2 = '''
	move 15
	turn 90
	move 15
	turn 90
	'''


test_tree2 = parsePLL(test_str2, asTree="Turtle")

#def test_1():
#	n = ilen(test_tree.children())
#	assert n == 2

#def test_2():
#	n = ilen(test_tree.descendents())
#	assert n == 6


# ---------------------------------------------------------------------------
# --- Test HEREDOC syntax

test_str3 = '''
	MenuBar
		file
			new
				handler <<<
					my $evt = $_[0];
					$evt.createNewFile();
					return undef;

			open
		edit
			undo
'''

test_tree3 = parsePLL(test_str3, debug=False)

def test_9():
	label = test_tree3['label']
	assert label == 'MenuBar'

def test_10():
	n = ilen(test_tree3.children())
	assert n == 2

def test_11():
	n = ilen(test_tree3.descendents())
	assert n == 10


# ---------------------------------------------------------------------------

cleanup_testcode(globals())   # remove unit tests when not testing

# ---------------------------------------------------------------------------

# To Do:
#    1. Allow spaces for indentation
