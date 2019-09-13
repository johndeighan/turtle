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

reLine     = re.compile(r'^(\s*)')
reComment  = re.compile(r'(?<!\\)#.*$')  # ignore escaped '#' char
hMySpecial = {
	'hereDocStr': '<<<',
	'keyStr':     '*',
	}

# ---------------------------------------------------------------------------

def _generatorFunc(fh, asTree=None):

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

def splitLine(line, hSpecial=hMySpecial):
	# --- returns (level, label, key, numHereDoc)
	#     label will have keyStr removed, but hereDocStr's will remain

	hereDocStr = hSpecial.get('hereDocStr', hMySpecial['hereDocStr'])
	keyStr     = hSpecial.get('keyStr',     hMySpecial['keyStr'])

	result = reLine.search(line)
	if result:

		# --- Get indentation, if any, to determine level
		indent = result.group(1)
		if ' ' in indent:
			raise SyntaxError(f"Indentation '{traceStr(indent)}'"
			                   " cannot contain space chars")
		level = len(indent)

		# --- Check if the key string is present
		#     If so, strip it to get label, then set key = label
		key = None
		if keyStr:
			if line.find(keyStr, level) == level:
				label = key = line[level + len(keyStr):]
			else:
				label = line[level:]
		else:
			label = line[level:]

		# --- Check if there are any HereDoc strings
		numHereDoc = 0
		if hereDocStr:
			pos = label.find(hereDocStr, 0)
			while pos != -1:
				numHereDoc += 1
				pos += len(hereDocStr)
				pos = label.find(hereDocStr, pos)

		return (level, label, key, numHereDoc)
	else:
		raise Exception("What! This cannot happen (reLine fails to match)")

# ---------------------------------------------------------------------------

def parsePLL(fh, debug=False,
                 asTree=None,
                 constructor=TreeNode,
                 hSpecial=hMySpecial):
	# --- If parameter 'asTree' is provided, it becomes the top-level node
	#     and the text in fh can be a sequence of nodes
	#
	#     hSpecial contains special strings, default is:
	#        hereDocStr = '<<<'
	#        keyStr = '*'

	numLines = 0
	lReturns = []    # first item will be root, other keys possible
	curLevel = None

	gen = _generatorFunc(fh, asTree)  # allows us to get HEREDOC lines
	for line in gen:
		numLines += 1

		if debug:
			print(f"LINE {numLines}: '{traceStr(line)}'", end='')

		(newLevel, label, key, numHereDoc) = splitLine(line, hSpecial)

		if debug:
			print(f" [{newLevel},{numHereDoc}] '{label}'")

		if numHereDoc > 0:
			print(f"DEBUG: numHereDoc = {numHereDoc}")
			try:
				for i in range(numHereDoc):
					hereLine = next(gen)
					print(f"DEBUG: hereLine = '{traceStr(hereLine)}'")
					while not reAllWS.match(hereLine):
						print(f"DEBUG: NOT ALL WHITESPACE")
						hereLine = next(gen)
						print(f"DEBUG: hereLine = '{traceStr(hereLine)}'")
					numHereDoc -= 1
			except:
				raise SyntaxError("Unexpected EOF in HEREDOC string")

		# --- process first non-empty line
		if len(lReturns) == 0:
			curNode = constructor(label)
			lReturns.append(curNode)
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
			curNode = constructor(label).makeChildOf(curNode)
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
			curNode = constructor(label).makeSiblingOf(curNode)
		elif diff == 0:
			# --- create new sibling node
			if debug:
				print(f"   - new sibling of {curNode.asDebugString()}")
			assert not curNode.nextSibling
			curNode = constructor(label).makeSiblingOf(curNode)

		else:
			raise Exception("What! This cannot happen")

	if numLines == 0:
		if asTree:
			return constructor(asTree)
		else:
			raise Exception("parsePLL(): No text to parse")

	if len(lReturns) == 0:
		raise Exception("parsePLL(): return value is empty")

	return lReturns

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

(test_tree,) = parsePLL(test_str, debug=False)

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


(test_tree2,) = parsePLL(test_str2, asTree="Turtle")

def test_1():
	n = ilen(test_tree.children())
	assert n == 2

def test_2():
	n = ilen(test_tree.descendents())
	assert n == 6


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

(test_tree3,) = parsePLL(test_str3, debug=False)

def test_9():
	label = test_tree3['label']
	assert label == 'MenuBar'

def test_10():
	n = ilen(test_tree3.children())
	assert n == 2

def test_11():
	n = ilen(test_tree3.descendents())
	assert n == 7

# ---------------------------------------------------------------------------
#     Test if it will parse fragments

test_str4 = '''
	MenuBar
		file
			new
			open
		edit
			undo
	Layout
		row
			EditField
			SelectField
'''

(test_tree4,) = parsePLL(test_str4, debug=False)

def test_12():
	n = ilen(test_tree4.descendents())
	assert n == 6

def test_13():
	n = ilen(test_tree4.followingNodes())
	assert n == 10

# ---------------------------------------------------------------------------

cleanup_testcode(globals())   # remove unit tests when not testing

# ---------------------------------------------------------------------------

# To Do:
#    1. Allow spaces for indentation
