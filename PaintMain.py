import pygame
from pygame.locals import *
import zgui
from zgui.guiglobal import *
from PaintCore import *
import PaintConfig as pcfg
import time
# import PaintCompiled as pc


class Paint:
	"""Main class of Paint"""

	def __init__(self):

		st = time.time()

		pygame.init()
		self.screen = pygame.display.set_mode(pcfg.SIZE)
		self.running = True
		self.gui = zgui.init(theme = 'WINDOWS8GRAY')
		self.init()
		self.clock = pygame.time.Clock()
		zgui.guilocal.logger.info("init time: %f"%(time.time()-st))

		pygame.event.set_grab(False)

	def init(self):

		pygame.display.set_caption(pcfg.TITLE)


		menuBar = MenuBar()
		statusBar = StatusBar()

		f = Menu(text = 'File')

		new = MenuItem(text = 'New')
		op = MenuItem(text = 'Open')
		sv = MenuItem(text = 'Save')
		svs = MenuItem(text ='Save As')
		ex = MenuItem(text = 'Exit')

		f.add(new)
		f.add(op)
		f.add(sv)
		f.add(svs)
		f.add(ex)

		menuBar.add(f)
		e = Menu(text = 'Edit')
		cs = MenuItem(text = 'Color Select')
		ce = MenuItem(text = 'Color Slider')
		mc = MenuItem(text = 'Clear')
		ud = MenuItem(text = 'Undo')
		rd = MenuItem(text = 'Redo')
		e.add(ud)
		e.add(rd)
		e.add(mc)
		e.add(cs)
		e.add(ce)

		menuBar.add(e)

		vw = Menu(text = 'View')
		stb = MenuItem(text = 'Show ToolBox')
		scv = MenuItem(text = 'Show Canvas')
		cbg = MenuItem(text = 'Change Background')
		ms = MenuItem(text = 'Play Minesweeper')

		vw.add(stb)
		vw.add(scv)
		vw.add(cbg)
		vw.add(ms)

		menuBar.add(vw)


		t = Menu(text = 'Tools')
		msm = MenuItem(text = 'Select and Move')
		mp = MenuItem(text = 'Pencil')
		me = MenuItem(text = 'Eraser')
		mr = MenuItem(text = 'Rectangle')
		mtx = MenuItem(text = 'Text')
		mcir = MenuItem(text = 'Circle')
		mab = MenuItem(text = 'Airbrush')
		ml = MenuItem(text = 'Line')
		mf = MenuItem(text = 'Fill')
		mcp = MenuItem(text = 'Color Picker')


		t.add(msm)
		t.add(ml)
		t.add(mp)
		t.add(me)
		t.add(mtx)
		t.add(mr)
		t.add(mcir)
		t.add(mab)
		t.add(mf)
		t.add(mcp)

		menuBar.add(t)
		h = Menu(text = 'Help')
		th = MenuItem(text = 'Tool Helps')
		hp = MenuItem(text = 'Small Bug')
		ab = MenuItem(text = 'About Paint')
		h.add(th)
		h.add(hp)
		h.add(ab)

		menuBar.add(h)


		self.gui.setStatusBar(statusBar)
		self.gui.setMenuBar(menuBar)

		self.gui.statusBar.setText(pcfg.TITLE)

		canvasWin = CanvasWindow(size = (800,600))

		self.gui.add(canvasWin,(200,50))

		canvas = canvasWin.canvas



		ce.mouseLeftUp.connect(ColorEditDialog)
		cs.mouseLeftUp.connect(ColorSelectDialog)

		def quit():
			if not canvas['saved']:
				mb = canvas.askForSave()
				mb.no.mouseLeftUp.connect(self.quit)
				canvas.imageSaved.connect(self.quit)
			else:
				self.quit()

		def thelp():
			mb = MessageBox(text = "Pencil: press to draw pencil line\nEraser: press to erase area\n"
				"Rectangle: Left click and drag, draw a rectangle on screen\nEllipse: Left click and drag, draw a Ellipse\n"
				"Airbrush/Spray: press, draw random dot on screen.\nLine: click and drag,draw a line.\n"
				"Fill: click canvas, flood fill canvas\nColor Picker: pick a color from canvas\n"
				"select&move:  left click and drag to select, drag selection to other place\n"
				"Text: click to open text editor, Enter to finish",title = 'Tool Helps',size = (350,450),ratio = 0.2)

		def nohelp():
			mb = MessageBox(text = "This program is desinged for Windows.\nRecommend using Windows 8.\nBug: Some functions will not work properly on Mac OS and Linux.\nNew version is comming soon!",title = 'I Hate Bug',size = (300,270))
		def about():
			MessageBox(text = "This is not a Paint\nIt's a Operating System with Paint\nCopyright: Zihao Zhang 2013",title = 'About')
		th.mouseLeftUp.connect(thelp)
		hp.mouseLeftUp.connect(nohelp)
		ab.mouseLeftUp.connect(about)

		self.gui.Quit.connect(quit)
		ex.mouseLeftUp.connect(quit)

		new.mouseLeftUp.connect(canvas.new)
		op.mouseLeftUp.connect(canvas.openFile)
		sv.mouseLeftUp.connect(canvas.saveFile)
		svs.mouseLeftUp.connect(canvas.saveAs)


		def showCv():
			if not canvasWin['visible']:
				canvasWin['visible'] = True
			local.gui.changeFocus(canvasWin)


		scv.mouseLeftUp.connect(showCv)


		tb = ToolBox()
		tb.setCanvas(canvas)

		def showTb():
			if not tb['visible']:
				tb['visible'] = True
			local.gui.changeFocus(tb)

		stb.mouseLeftUp.connect(showTb)

		st = SelectTool()
		pt = PencilTool()
		rt = RectTool()
		er = EraserTool()
		ab = AirbrushTool()
		ct = CircleTool()
		cl = ClearTool()
		lt = LineTool()
		ft = FillTool()
		cp = ColorPickerTool()
		tt = TextTool()

		mc.mouseLeftUp.connect(canvas.clear)
		msm.mouseLeftUp.connect(st.active)
		mp.mouseLeftUp.connect(pt.active)
		me.mouseLeftUp.connect(er.active)
		mr.mouseLeftUp.connect(rt.active)
		mcir.mouseLeftUp.connect(ct.active)
		mab.mouseLeftUp.connect(ab.active)
		ml.mouseLeftUp.connect(lt.active)
		mf.mouseLeftUp.connect(ft.active)
		mcp.mouseLeftUp.connect(cp.active)
		mtx.mouseLeftUp.connect(tt.active)


		tb.add(pt,(0,0))
		tb.add(er,(0,1))
		tb.add(rt,(1,0))
		tb.add(ct,(1,1))
		tb.add(ab,(2,0))
		tb.add(lt,(2,1))
		tb.add(ft,(3,0))
		tb.add(cp,(3,1))
		tb.add(st,(4,0))
		tb.add(tt,(4,1))
		self.gui.add(tb,(20,50))

		ud.mouseLeftUp.connect(canvas.undo)
		rd.mouseLeftUp.connect(canvas.redo)

		def mama():
			self.gui.add(Minesweeper(),(60,60))
		ms.mouseLeftUp.connect(mama)



		def loadbg(fn):
			self.bg = ResizeImage(pr.resMgr.LoadImage(fn).convert(),pcfg.SIZE)

		loadbg(pcfg.BACKGROUND)

		def changebg():
			fn = pc.getopenfilename()
			if fn:
				try:
					pr.resMgr.LoadImage(fn)
				except:
					MessageBox(text = 'Load Background Failed',title = 'Error')
					return
				loadbg(fn)

		cbg.mouseLeftUp.connect(changebg)



	def run(self):
		"""Enter main loop"""

		total = 0
		update = 0
		draw = 0

		while self.running:
			self.clock.tick()
			if pcfg.FILENAME:fn = pcfg.FILENAME
			else: fn = "untitled"
			pygame.display.set_caption(fn+ ' - '+pcfg.TITLE)
			self.screen.blit(self.bg.surface,(0,0))
			evt = pygame.event.get()
			self.gui.update(evt)
			self.gui.draw(self.screen)
			pygame.display.flip()

		pygame.quit()

	def quit(self):
		"""Exit program"""

		self.running = False

if __name__ == '__main__':

	paint = Paint()
	paint.run()

