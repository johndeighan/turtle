# PLLParser.py

"""
parse a 'Python-like language'
"""

import sys, io, re, pytest
from more_itertools import ilen
from pprint import pprint

from myutils import (rmPrefix, reLeadWS, reTrailWS, reAllWS,
                    traceStr, cleanup_testcode)
from TreeNode import TreeNode

# --- Some pre-compiled regular expressions

reLine     = re.compile(r'^(\s*)')
reComment  = re.compile(r'(?<!\\)#.*$')  # ignore escaped '#' char
hMySpecial = {
	'hereDocStr': '<<<',
	'markStr':     '*',
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

	flag = None   # might become 'any'

	if asTree:
		assert isinstance(asTree, str)
		flag = yield asTree
		if leadWS:
			while line:
				# --- Check if the required leadWS is present
				if not flag and (line[:leadLen] != leadWS):
					raise SyntaxError("Missing leading whitespace")
				flag = yield '\t' + line[leadLen:]
				if flag:
					line = nextAnyLine(fh)
				else:
					line = nextNonBlankLine(fh)
		else:
			while line:
				flag = yield '\t' + line
				if flag:
					line = nextAnyLine(fh)
				else:
					line = nextNonBlankLine(fh)
	else:
		if leadWS:
			while line:
				# --- Check if the required leadWS is present
				if not flag and (line[:leadLen] != leadWS):
					raise SyntaxError("Missing leading whitespace")
				flag = yield line[leadLen:]
				if flag:
					line = nextAnyLine(fh)
				else:
					line = nextNonBlankLine(fh)
		else:
			while line:
				flag = yield line
				if flag:
					line = nextAnyLine(fh)
				else:
					line = nextNonBlankLine(fh)

# ---------------------------------------------------------------------------

def splitLine(line, hSpecial=hMySpecial):
	# --- returns (level, label, marked, numHereDoc)
	#     label will have markStr removed, but hereDocStr's will remain

	hereDocStr = hSpecial.get('hereDocStr', hMySpecial['hereDocStr'])
	markStr    = hSpecial.get('markStr',    hMySpecial['markStr'])

	marked = False
	result = reLine.search(line)
	if result:

		# --- Get indentation, if any, to determine level
		indent = result.group(1)
		if ' ' in indent:
			raise SyntaxError(f"Indentation '{traceStr(indent)}'"
			                   " cannot contain space chars")
		level = len(indent)

		# --- Check if the mark string is present
		#     If so, strip it to get label, then set key = label
		if markStr:
			if line.find(markStr, level) == level:
				label = line[level + len(markStr):].lstrip()
				if len(label) == 0:
					raise SyntaxError("Marked lines cannot be empty")
				marked = True
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

		return (level, label, marked, numHereDoc)
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
	#        markStr = '*'

	numLines = 0
	lReturns = []    # first item will be root, other keys possible
	curLevel = None

	gen = _generatorFunc(fh, asTree)  # allows us to get HEREDOC lines
	for line in gen:
		numLines += 1

		if debug:
			print(f"LINE {numLines}: '{traceStr(line)}'", end='')

		(newLevel, label, marked, numHereDoc) = splitLine(line, hSpecial)

		if debug:
			print(f" [{newLevel},{numHereDoc}] '{label}'")

		# --- Extract HEREDOC strings, if any
		lHereDoc = None
		if numHereDoc > 0:
			lHereDoc = []
			try:
				text = ''
				for i in range(numHereDoc):
					hereLine = gen.send('any')
					while not reAllWS.match(hereLine):
						text += hereLine
						hereLine = gen.send('any')
					lHereDoc.append(rmPrefix(text))
					numHereDoc -= 1
			except:
				raise SyntaxError("Unexpected EOF in HEREDOC string")

		# --- process first non-empty line
		if len(lReturns) == 0:
			curNode = constructor(label, lHereDoc)
			if lHereDoc:
				curNode['lHereDoc'] = lHereDoc
			lReturns.append(curNode)

			# --- This wouldn't make any sense, but in case someone does it
			if marked:
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
			if lHereDoc:
				curNode['lHereDoc'] = lHereDoc
			if marked:
				lReturns.append(curNode)
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
			if lHereDoc:
				curNode['lHereDoc'] = lHereDoc
			if marked:
				lReturns.append(curNode)
		elif diff == 0:
			# --- create new sibling node
			if debug:
				print(f"   - new sibling of {curNode.asDebugString()}")
			assert not curNode.nextSibling
			curNode = constructor(label).makeSiblingOf(curNode)
			if lHereDoc:
				curNode['lHereDoc'] = lHereDoc
			if marked:
				lReturns.append(curNode)

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

def nextAnyLine(fh):

	line = fh.readline()
	if line:
		return line
	else:
		return None

# ---------------------------------------------------------------------------

def nextNonBlankLine(fh):

	line = fh.readline()
	if not line:
		return None
	line = re.sub(reComment, '', line)
	line = re.sub(reTrailWS, '', line)
	while line == '':
		line = fh.readline()
		if not line: return None
		line = re.sub(reComment, '', line)
		line = re.sub(reTrailWS, '', line)
	return line

# ---------------------------------------------------------------------------
#                   UNIT TESTS
# ---------------------------------------------------------------------------

def test_1():
	s = '''
		top
			peach
				fuzzy
						navel
				pink
			apple
				red
	'''
	(tree,) = parsePLL(s, debug=False)

	n = ilen(tree.children())
	assert n == 2

	n = ilen(tree.descendents())
	assert n == 6

	assert ilen(tree.firstChild.children()) == 2

	assert tree['label'] == 'top'

	assert tree.firstChild['label'] == 'peach'

	node = tree.firstChild.firstChild
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

def test_2():
	s = '''
		move 15
		turn 90
		move 15
		turn 90
		'''
	(tree,) = parsePLL(s, asTree="Turtle")

	n = ilen(tree.children())
	assert n == 4

	n = ilen(tree.descendents())
	assert n == 5


# ---------------------------------------------------------------------------
# --- Test HEREDOC syntax

def test_3():
	s = '''
		MenuBar
			file
				new
					*handler <<<
						my $evt = $_[0];
						$evt.createNewFile();
						return undef;

				open
			edit
				undo
	'''
	(tree, handler) = parsePLL(s, debug=False)

	label = tree['label']
	assert label == 'MenuBar'

	n = ilen(tree.children())
	assert n == 2

	n = ilen(tree.descendents())
	assert n == 7

	assert 'lHereDoc' in handler
	assert (handler['lHereDoc'][0]
		== 'my $evt = $_[0];\n$evt.createNewFile();\nreturn undef;\n')

# ---------------------------------------------------------------------------
#     Test if it will parse fragments

def test_4():
	s = '''
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
	(tree,) = parsePLL(s, debug=False)

	n = ilen(tree.descendents())
	assert n == 6

	n = ilen(tree.followingNodes())
	assert n == 10

# ---------------------------------------------------------------------------
#     Test marked subtrees

def test_5():
	s = '''
		App
			* MenuBar
				file
					new
					open
				edit
					undo
			* Layout
				row
					EditField
					SelectField
	'''
	(tree, subtree1, subtree2) = parsePLL(s, debug=False)

	n = ilen(tree.descendents())
	assert n == 11

	assert (subtree1['label'] == 'MenuBar')
	n = ilen(subtree1.descendents())
	assert n == 6

	assert (subtree2['label'] == 'Layout')
	n = ilen(subtree2.descendents())
	assert n == 4

	n = ilen(tree.followingNodes())
	assert n == 11

# ---------------------------------------------------------------------------

cleanup_testcode(globals())   # remove unit tests when not testing

# ---------------------------------------------------------------------------

# To Do:
#    1. Allow spaces for indentation
