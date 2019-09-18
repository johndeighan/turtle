# WidgetStorage.py

_hSavedWidgets = {}

# ---------------------------------------------------------------------------

def saveWidget(name, widget):
	# --- This is called for any widget created
	#     that has a 'name' key

	global _hSavedWidgets
	if name in _hSavedWidgets:
		raise Exception(f"saveWidget(): There is already a widget"
		                f" named '{name}'")
	_hSavedWidgets[name] = widget

# ---------------------------------------------------------------------------

def findWidgetByName(name):

	global _hSavedWidgets
	if name in _hSavedWidgets:
		return _hSavedWidgets[name]
	else:
		raise Exception(f"findWidgetByName():"
		                f" There is no widget named '{name}'")

# ---------------------------------------------------------------------------

def removeSavedWidgets():

	global _hSavedWidgets
	_hSavedWidgets = {}

# ---------------------------------------------------------------------------

def numSavedWidgets():

	global _hSavedWidgets
	n = len(_hSavedWidgets)
	return n

# ---------------------------------------------------------------------------
