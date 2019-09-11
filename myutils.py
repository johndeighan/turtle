# myutils.py

import sys, re, io, pytest
from mydecorators import unittest

reAllWS    = re.compile(r'^\s*$')
reLeadWS   = re.compile(r'^([\t\ ]+)')   # don't consider '\n'
reLeadTabs = re.compile(r'^(\t*)')
reTrailWS  = re.compile(r'\s+$')
reTrailNL  = re.compile(r'\n$')
reSep      = re.compile(r'^-+$')
hSpecial = {
	"\t": "\\t",
	"\n": "\\n",
	" " : ".",
	}

# ---------------------------------------------------------------------------

def rmPrefix(lLines, *, debug=False, skipEmptyLines=True):
	# --- Normally lLines is a list of strings, but you can pass in
	#        a string with internal '\n' characters
	#
	# --- A  line consisting of only whitespace, is considered empty
	#     leading and trailing empty lines don't appear in output
	#     internal empty lines appear as empty lines, but
	#        no exception for the missing prefix

	# --- Check the type of the parameter ---
	if isinstance(lLines, str):
		if debug:
			print(f"DEBUG: String passed, splitting into lines")
		lNewLines = rmPrefix(io.StringIO(lLines).readlines())
		return ''.join(lNewLines)
	elif type(lLines) is not list:
		typ = type(lLines)
		raise TypeError(f"rmPrefix(): Invalid parameter, type = {typ}")

	if len(lLines) == 0:
		if debug:
			print(f"DEBUG: Zero lines - return empty list")
		return []

	firstLine = lLines[0]             # first line
	nextPos = 1
	if debug:
		print(f"DEBUG:    firstLine set to '{traceStr(firstLine)}'")

	lNewLines = []     # this will be returned

	# --- Skip past any empty lines
	#     NOTE: If skipEmptyLines is False, the empty lines are
	#           included, but not considered for determining the prefix

	while reAllWS.match(firstLine) and (nextPos < len(lLines)):
		if skipEmptyLines:
			if debug:
				print(f"DEBUG: Line at pos {nextPos-1} '{traceStr(firstLine)}'"
						 " is empty - skipping")
		else:
			if line[-1] == '\n':
				lNewLines.append('\n')
				if debug:
					print(f"DEBUG: Add line at pos {nextPos-1} '\\n'")
			else:
				lNewLines.append('')
				if debug:
					print(f"DEBUG: Add line at pos {nextPos-1} ''")

		firstLine = lLines[nextPos]
		if debug:
			print(f"DEBUG:    firstLine reset to '{traceStr(firstLine)}'")
		nextPos += 1

	if (reAllWS.match(firstLine)):
		if debug:
			print(f"DEBUG: All lines empty - return empty list")
		return []

	if debug:
		print(f"DEBUG: First non-empty line '{traceStr(firstLine)}'"
		      f" found at pos {nextPos-1}")

	result = reLeadWS.match(firstLine)
	if not result:
		if debug:
			print(f"DEBUG: No prefix found - return remaining lines,"
			      f" sripping trailing empty lines")
		lNewLines = lLines[nextPos:]
		while (len(lNewLines) > 0) and reAllWS.match(lNewLines[-1]):
			del lNewLines[-1]
		return lNewLines             # nothing to strip off

	leadWS = result.group(1)
	nChars = len(leadWS)
	assert nChars > 0    # due to regexp used
	if debug:
		print(f"DEBUG: Prefix '{traceStr(leadWS)}'"
		      f" consists of {nChars} chars")

	# --- Create an entirely new array
	#     Add first line, with prefix stripped off
	lNewLines.append(firstLine[nChars:])
	if debug:
		print(f"DEBUG: Add line '{traceStr(firstLine[nChars:])}'")

	for line in lLines[nextPos:]:
		if reAllWS.match(line):
			if skipEmptyLines:
				if debug:
					print(f"DEBUG: Skip empty line")
			else:
				if line[-1] == '\n':
					lNewLines.append('\n')
					if debug:
						print(f"DEBUG: Add line '\\n'")
				else:
					lNewLines.append('')
					if debug:
						print(f"DEBUG: Add line ''")
		else:
			pos = line.find(leadWS)
			if pos == 0:
				# --- remove the prefix
				lNewLines.append(line[nChars:])
				if debug:
					print(f"DEBUG: Add line '{traceStr(line[nChars:])}'")
			else:
				raise SyntaxError("rmPrefix(): Bad indentation")

	if skipEmptyLines:
		# --- Strip off trailing WS lines
		while (len(lNewLines) > 0) and reAllWS.match(lNewLines[-1]):
			del lNewLines[-1]
			if debug:
				print(f"DEBUG: Remove last line")

	if debug:
		print(lNewLines)

	return lNewLines

# ---------------------------------------------------------------------------

def getHereDoc(fh):
	# --- Allow passing in a string
	if isinstance(fh, str):
		fh = io.StringIO(fh)

	lLines = []
	line = fh.readline()
	while line and not reAllWS.match(line):
		lLines.append(line)
		line = fh.readline()
	return rmPrefix(lLines)

# ---------------------------------------------------------------------------

def getMethod(aClass, methodName):

	try:
		return getattr(aClass, methodName)
	except AttributeError:
		return None

# ---------------------------------------------------------------------------

def getFunc(aModule, funcName):

	try:
		return getattr(aModule, funcName)
	except AttributeError:
		return None

# ---------------------------------------------------------------------------

def traceStr(str, *, maxchars=10, detailed=False):

	nTabs = 0
	nChars = 0
	outstr = ''
	result = reLeadTabs.search(str)
	totTabs = len(result.group(1))
	for ch in str:
		if maxchars and (nChars >= maxchars): break
		if (ch == '\t'):
			if (nChars == totTabs-1):
				outch = '. '
			elif (nChars == 0):
				outch = '.'
			else:
				outch = '.'
			nTabs += 1
		elif ch in hSpecial:
			outch = hSpecial[ch]
		else:
			outch = ch
		if detailed:
			print(f"CHAR: '{outch}'")
		outstr += outch
		nChars += 1
	return outstr

# ---------------------------------------------------------------------------

def cleanup_testcode(glob, *, debug=False):
	# --- If not running unit tests, remove unneeded functions and data
	#     to save memory
	if sys.argv[0].find('pytest') == -1:
		if debug:
			print(f"Running normally - clean up {glob['__file__']} test functions/data")
		reTest = re.compile(r'^test_')
		for name in [name for name in glob.keys() if reTest.match(name)]:
			if debug:
				print(f"Clean up {name}")
			globals()[name] = None
	else:
		if debug:
			print("Running unit tests")

# ---------------------------------------------------------------------------
#                  UNIT TESTS
# ---------------------------------------------------------------------------

def test_1():
	with pytest.raises(TypeError):
		s = rmPrefix(5)

def test_2():
	with pytest.raises(TypeError):
		s = rmPrefix((3,4,5))

def test_21():
	from TreeNode import TreeNode
	with pytest.raises(TypeError):
		s = rmPrefix(TreeNode('label'))

# --- Make sure these things are tested - for strings & lists of strings
#     1. By default, any whitespace lines are removed
#     2. Internal whitespace lines are included
#     3. Trailing newlines are untouched

def test_3():
	# --- Basic example - find leading whitespace in first line
	#                     and strip that from all other lines
	lNewLines = rmPrefix([
		"\t\tabc",
		"\t\t\tdef",
		"\t\t\t\tghi",
		])
	assert lNewLines == [
		"abc",
		"\tdef",
		"\t\tghi",
		]

def test_30():
	assert rmPrefix([]) == []

def test_31():
	# --- leading and trailing all-whitespace lines are removed
	lNewLines = rmPrefix([
		"",
		"\t \t",
		"\t\t\n",
		"\t\tabc",
		"\t\t\tdef",
		"\t\t\t\tghi",
		"\t\t",
		])
	assert lNewLines == [
		"abc",
		"\tdef",
		"\t\tghi",
		]

def test_4():
	s = '''
			abc
				def
					ghi
'''
	lNewStr = rmPrefix(s)
	assert lNewStr == 'abc\n\tdef\n\t\tghi\n'

def test_5():
	# --- test the utility function getHereDoc()
	s = '''
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
	fh = io.StringIO(s)
	line1 = fh.readline()   # a blank line
	line2 = fh.readline()   # MenuBar
	line3 = fh.readline()   # file
	line4 = fh.readline()   # new
	line5 = fh.readline()   # handler <<<
	assert line5.find('<<<') == 13
	lLines = getHereDoc(fh)
	assert len(lLines) == 3
	line6 = fh.readline()   # open
	assert(line6.find('open') == 4)


cleanup_testcode(globals())