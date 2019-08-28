# test_pll.py

import sys
from PLLParser import parsePLL
from more_itertools import ilen
import pytest

# ---------------------------------------------------------------------------

str = '''
	top
		peach
			fuzzy
					navel
			pink
		apple
			red
'''


tree = parsePLL(str, debug=False)

def test1():
	n = ilen(tree.children())
	assert n == 2

def test2():
	n = ilen(tree.descendents())
	assert n == 6

def test3():
	assert ilen(tree.firstChild.children()) == 2

def test4():
	assert tree['label'] == 'top'

def test5():
	assert tree.firstChild['label'] == 'peach'

def test6():
	node = tree.firstChild.firstChild
	node['label'] == 'fuzzy navel'

# ---------------------------------------------------------------------------
# Test some invalid input

def test7():
	str = '''
		main
			  peach
			apple
	'''
	with pytest.raises(SyntaxError):
		parsePLL(str)

def test8():
	str = '''
main
   peach
   apple
	'''
	with pytest.raises(SyntaxError):
		parsePLL(str)

