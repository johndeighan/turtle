# image_viewer.py

import sys
from ImageViewerApp import ImageViewerApp

try:
	app = ImageViewerApp()
	app.MainLoop()
except Exception as ex:
	print("An exception occurred")
	(type, obj, tb) = sys.exc_info()
	fname = os.path.split(tb.tb_frame.f_code.co_filename)[1]
	print(type, fname, tb.tb_lineno)

