# ImageViewerApp.py

import os, glob, wx
from wx import (
		VERTICAL, HORIZONTAL, ALL, CENTER,
		EVT_BUTTON, EVT_MENU,
		ID_ANY, ID_OPEN, ID_OK,
		BITMAP_TYPE_ANY,
		ART_FILE_OPEN, ART_TOOLBAR,
		DD_DEFAULT_STYLE)

# ---------------------------------------------------------------------------

class ImagePanel(wx.Panel):

	def __init__(self, parent, maxW=600, maxH=600):
		super().__init__(parent)

		self.maxWidth = maxW
		self.maxHeight = maxH

		self.curPhoto = None   # normally an integer
		self.lPhotos = []

		# --- Create the main Sizer - organizes things vertically
		mainSizer = wx.BoxSizer(VERTICAL)

		# --- Create and add the image control
		self.imageCtrl = wx.StaticBitmap(self, size=(600,600))
		mainSizer.Add(self.imageCtrl, 0, ALL, 5)

		# --- Create and add navigation buttons
		navSizer = wx.BoxSizer(HORIZONTAL)

		self.addButton('Previous', navSizer, self.cmdPrev)
		self.addButton('Slide Show', navSizer, self.cmdSlideShow)
		self.addButton('Next', navSizer, self.cmdNext)

		mainSizer.Add(navSizer, 0, ALL, 5)

		# --- Create and add the "load file" control
		fileSizer = wx.BoxSizer(HORIZONTAL)

		self.loadBtn = wx.Button(self, label='Load...')
		self.loadBtn.Bind(EVT_BUTTON, self.cmdLoad)
		fileSizer.Add(self.loadBtn, 0, ALL, 5)

		self.pathCtrl = wx.TextCtrl(self, size=(400, -1))
		fileSizer.Add(self.pathCtrl, 0, ALL, 5)

		mainSizer.Add(fileSizer, 0, ALL, 5)

		self.SetSizer(mainSizer)
		mainSizer.Fit(parent)
		self.Layout()

		self.loadPhoto()   # load a blank image

	def cmdLoad(self, event):
		with wx.FileDialog(None,
				"Choose a File",
				wildcard = "JPEG files (*.jpg)|*.jpg",
				style = ID_OPEN
				) as dialog:
			if dialog.ShowModal() == ID_OK:
				self.lPhotos.append(dialog.GetPath())
				self.loadPhoto()

	def cmdPrev(self, event):
		if (self.curPhoto > 1):
			self.loadPhoto(self.curPhoto - 1)

	def cmdSlideShow(self, event):
		print("cmdSlideShow")

	def cmdNext(self, event):
		if (self.curPhoto < len(self.lPhotos)-1):
			self.loadPhoto(self.curPhoto + 1)

	def setPhotos(self, lPhotos):
		assert isinstance(lPhotos, list)
		if (len(lPhotos) == 0):
			self.lPhotos = []
			self.loadPhoto()
		else:
			self.lPhotos = lPhotos
			self.loadPhoto(0)

	def loadPhoto(self, pos=None):
		# --- If pos is None, then
		#        if lPhotos is empty, display a blank image
		#        if lPhotos is non-empty, display the last image

		(maxW, maxH) = (self.maxWidth, self.maxHeight)
		numPhotos = len(self.lPhotos)

		# --- Create the bitmap, scaled if necessary
		if (pos == None) and (numPhotos == 0):
			self.pathCtrl.SetValue('')
			bitmap = wx.Bitmap(wx.Image(maxW, maxH))
			self.curPhoto = None
		else:
			if (pos == None):
				pos = numPhotos - 1
			self.curPhoto = pos
			path = self.lPhotos[pos]
			self.pathCtrl.SetValue(path)
			img = wx.Image(path, BITMAP_TYPE_ANY)
			bitmap = wx.Bitmap(scaleImage(img, maxW, maxH))

		self.imageCtrl.SetBitmap(bitmap)
		self.Refresh()

	def addButton(self, label, sizer, handler):

		btn = wx.Button(self, label=label)
		btn.Bind(EVT_BUTTON, handler)
		sizer.Add(btn, 0, ALL|CENTER, 5)

# ---------------------------------------------------------------------------

class ImageFrame(wx.Frame):

	def __init__(self, title):
		super().__init__(None, title=title)
		self.createToolbar()
		self.panel = ImagePanel(self)
		self.Show()

	def createToolbar(self):
		toolbar = self.toolbar = self.CreateToolBar()
		toolbar.SetToolBitmapSize((16, 16))
		openIcon = wx.ArtProvider.GetBitmap(
				ART_FILE_OPEN, ART_TOOLBAR, (16,16))
		openTool = toolbar.AddTool(
				ID_ANY, "open", openIcon, "Open an Image Directory")
		self.Bind(EVT_MENU, self.onOpenDir, openTool)
		toolbar.Realize()

	def onOpenDir(self, event):
		with wx.DirDialog(self, "Choose a directory",
		                        style=DD_DEFAULT_STYLE) as dlg:
			if dlg.ShowModal() == ID_OK:
				dir = self.dir = dlg.GetPath()
				lPhotos = glob.glob(os.path.join(dir, '*.jpg'))
				self.panel.setPhotos(lPhotos)

# ---------------------------------------------------------------------------

class ImageViewerApp(wx.App):
	def __init__(self):
		super().__init__(False)
		self.frame = ImageFrame('Image Viewer')

# ---------------------------------------------------------------------------
#             Utility Functions
# ---------------------------------------------------------------------------

def scaleImage(img, wMax, hMax):

	w = img.GetWidth()
	h = img.GetHeight()
	wScale = wMax / w
	hScale = hMax / h
	if wScale < hScale:
		wNew = w * wScale
		hNew = h * wScale
	else:
		wNew = w * hScale
		hNew = h * hScale
	return img.Scale(wNew, hNew)

# ---------------------------------------------------------------------------
