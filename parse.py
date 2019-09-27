# parse.py

from PLLParser import parsePLL

s = '''
	*menubar
		size = 23
		file
			new
			open
		edit
			undo
	*layout
		row
			EditField
			SelectField
'''

(tree, hSubTrees) = parsePLL(s, debug=False)

print("Keys in main node:")
for (key, value) in tree.items():
	print(f"   {key}")

if hSubTrees:
	print("Sub Trees:")
	for key in hSubTrees.keys():
		print(f"   {key}")

menubar = hSubTrees['menubar']
print("MENUBAR:")
menubar.printTree()
if menubar:
	n = menubar.numChildren()
	print(f"menubar has {n} children")
else:
	raise Exception("menubar does not exist!!!")
