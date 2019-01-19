import pygame
import zgui
import PaintResource as pr
# import PaintCompiled as pc
import PaintConfig as pcfg
import time
import random
from pygame.locals import *
from pygame import gfxdraw
from zgui.guiglobal import *
from math import *
CurrentColor = BLACK

class TransRect(Rectangle):
	"""Draw a Transparent Rectangle, GUIObject"""

	def __init__(self,**args):
		super().__init__(**args)
		default = {}
		default['color'] = WHITE
		default['alpha'] = 100
		default['size'] = (100,100)
		self.setDefault(default,args)
		self['surface'] = ExSurface(self['size'])
		self['surface'].fill(self['color'])
		self['surface'].set_alpha(self['alpha'])

	def resize(self,size):
		self['size'] = size
		self['surface'] = ExSurface(self['size'])
		self['surface'].fill(self['color'])
		self['surface'].set_alpha(self['alpha'])

class Slider(GUIObject):
	"""Allow user to slide block and get value, GUIObject"""

	def __init__(self,**args):
		super().__init__(**args)
		default = {}
		default['bgcolor'] = BLACK
		default['range'] = (0,100)
		default['value'] = 0
		default['objects'] = []
		self.setDefault(default,args)
		self['block'] = TransRect(color = BLACK,alpha = 100)
		self['length'] = self['range'][1]-self['range'][0]
		self.reset()
		self.SslideDown= Slot(self.slideDown)
		self.SslidePress = Slot(self.slidePress)
		self.SslideUp = Slot(self.slideUp)
		self['block'].mouseLeftDown.connectSlot(self.SslideDown)
		self.valueChanged = Signal(int)

	def slideDown(self):
		local.gui.mouseLeftPress.connectSlot(self.SslidePress)
		local.gui.mouseLeftUp.connectSlot(self.SslideUp)
		self.oldpos = local.mouse.pos

	def slidePress(self):
		pos = local.mouse.pos
		shift = pos[0]-self.oldpos[0]
		pre = shift/self['size'][0]
		val = self['value']+self['length']*pre
		self.setValue(val)
		self.oldpos = pos
		self.resetBlock()

	def slideUp(self):
		local.gui.mouseLeftUp.disconnectSlot(self.SslideUp)
		local.gui.mouseLeftPress.disconnectSlot(self.SslidePress)

	def setValue(self,val):
		"""set value of slider"""
		if val<self['range'][0]:
			self['value'] = self['range'][0]
		elif val>self['range'][1]:
			self['value'] = self['range'][1]
		else:
			self['value'] = val
		self.valueChanged(self['value'])

	def reset(self):
		self['background'] = ExSurface((512,512),self['bgcolor'])
		self.resetBlock()

	def resize(self,size):
		self['size'] = size
		self['background'] = ResizeImage(self['background'],size)
		self.resetBlock()

	def resetBlock(self):
		pre = (self['value']-self['range'][0])/self['length']
		leng = self['size'][0]
		x = leng*pre+self['pos'][0]-7
		y = self['pos'][1]-7
		h = self['size'][1]+14
		w = 14
		self['block']['pos'] = x,y
		self['block'].resize((w,h))

	def draw(self,screen):
		screen.blit(self['background'],self['pos'])
		self['block'].draw(screen)

	def _update(self,pos,fks):
		self['onfocus'] = fks
		newp = pos[0]+self['pos'][0],pos[1]+self['pos'][1]
		self['screenpos'] = newp
		self['rect'] = pygame.Rect(newp,self['size'])
		self['block']._update(pos,fks)
		self.basicEvent()

class ColorEdit(Container):
	"""Color Editor, get color from R,G,B, Container"""

	def __init__(self,**args):
		default = {}
		default['r']=0
		default['g']=0
		default['b']=0
		default['size'] = (400,150)
		self.setDefault(default,args)
		super().__init__(**args)
		self.square = Rectangle(color = (self['r'],self['g'],self['b']),bordercolor = BLACK)
		self.setLayout(HBoxLayout())
		self['layout'].add(self.square)
		l2 = VBoxLayout()
		self['layout'].add(l2)
		layr = HBoxLayout(spacing = 15)
		layg = HBoxLayout(spacing = 15)
		layb = HBoxLayout(spacing = 15)
		self.rs = Slider(bgcolor = RED,range = (0,255),sizehint = [50,10])
		self.gs = Slider(bgcolor = GREEN,range = (0,255),sizehint = [50,10])
		self.bs = Slider(bgcolor = BLUE,range = (0,255),sizehint = [50,10])
		self.rl = TextArea(text = '0',fontsize = 18)
		self.gl = TextArea(text = '0',fontsize = 18)
		self.bl = TextArea(text = '0',fontsize = 18)

		def changer(r):
			r = int(r)
			self.rl.setText(r)
			self['r'] = r
			self.resetSquare()

		def changeg(g):
			g = int(g)
			self.gl.setText(g)
			self['g'] = g
			self.resetSquare()

		def changeb(b):
			b = int(b)
			self.bl.setText(b)
			self['b'] = b
			self.resetSquare()
		self.rs.valueChanged.connect(changer)
		self.gs.valueChanged.connect(changeg)
		self.bs.valueChanged.connect(changeb)
		layr.add(self.rs)
		layr.add(self.rl)
		layg.add(self.gs)
		layg.add(self.gl)
		layb.add(self.bs)
		layb.add(self.bl)
		l2.add(layr)
		l2.add(layg)
		l2.add(layb)
		l2['sizehint'] = [21,10]
		l2['margintop'] = 10
		l2['spacing'] = 20
		l2['marginbot'] = 10
		l2['marginleft'] = 10
		self.resize(self['size'])

	def resetSquare(self):
		self['color'] = self['r'],self['g'],self['b']
		self.square.recolor(self['color'])

	def setColor(self,color):
		"""set colow of editor"""
		self.rs.setValue(color[0])
		self.gs.setValue(color[1])
		self.bs.setValue(color[2])

class ColorEditDialog(Dialog):
	"""Dialog of color editor, Dialog"""

	def __init__(self,**args):
		args['size'] = (420,250)
		super().__init__(**args)
		default = {}
		default['title'] = 'Color Editor'
		default['color'] = BLACK
		default['return'] = BLACK
		self.setDefault(default,args)
		self.buttonOk = Button(text = 'Ok')
		self.buttonOk.mouseLeftUp.connect(self.onOk)
		self.buttonCancel = Button(text = 'Cancel')
		self.buttonCancel.mouseLeftUp.connect(self.onCancel)
		self.ce = ColorEdit()
		self.ce['sizehint'] = [10,35]
		self.ce.setColor(CurrentColor)
		layout = VBoxLayout()
		layout.add(self.ce)
		bl = zgui.layout.HBoxLayout()
		bl.add(self.buttonOk)
		bl.add(self.buttonCancel)
		layout.add(bl)
		bl['marginleft'] = 150
		bl['marginright'] = 30
		bl['spacing'] = 10
		self.setLayout(layout)

	def onOk(self):
		self['return'] = self.ce['color']
		global CurrentColor
		CurrentColor = self.ce['color']
		self.close()

	def onCancel(self):
		self['return'] = CurrentColor
		self.close()

class ColorSelect(Image):
	"""Select a color from color chart, Contaienr"""

	def __init__(self,**args):
		args['surface'] = pr.resMgr.LoadImage('res/color.jpg')
		super().__init__(**args)
		self['color'] = CurrentColor
		self['select'] = (0,0)
		self['sight'] = ExSurface(ResizeImage(pr.resMgr.LoadImage('res/sight.png'),(20,20)))
		self.mouseOver.connect(self.over)
		self.mouseLeftPress.connect(self.press)
		self.colorChanged = Signal(tuple)

	def press(self):
		self['color'] = self.getColor()
		self.colorChanged(self['color'])

	def over(self):

		self['select'] = pos_minus(local.mouse.pos,self['screenpos'])

	def getColor(self):
		"""get color of current cursor"""
		return self['surface'].get_at(self['select'])

	def getSelect(self):
		"""get cursor position"""
		return pos_plus(self['pos'],self['select'])

	def draw(self,screen):
		super().draw(screen)
		screen.blit(self['sight'],pos_minus(self.getSelect(),(10,10)))

class ColorSelectDialog(Dialog):
	"""Dialog of color selecter"""

	def __init__(self,**args):
		args['size'] = (400,340)
		super().__init__(**args)
		default = {}
		default['title'] = 'Color Select'
		default['select'] = (0,0)
		default['return'] = BLACK
		self.setDefault(default,args)
		self.buttonOk = Button(text = 'Ok')
		self.buttonOk.mouseLeftUp.connect(self.onOk)
		self.buttonCancel = Button(text = 'Cancel')
		self.buttonCancel.mouseLeftUp.connect(self.onCancel)
		self.cs = ColorSelect()
		self.cs['sizehint'] = [10,30]
		self.square = Rectangle(color = CurrentColor)
		self.cs.colorChanged.connect(self.square.recolor)
		layout = VBoxLayout()
		layout.add(self.cs)
		bl = zgui.layout.HBoxLayout()
		bl.add(self.square)
		bl.add(self.buttonOk)
		bl.add(self.buttonCancel)
		layout.add(bl)
		self.setLayout(layout)

	def onOk(self):
		self['return'] = self.cs['color']
		global CurrentColor
		CurrentColor = self.cs['color']
		self.close()

	def onCancel(self):
		self['return'] = CurrentColor
		self.close()

class PaintTool(GUIObject):
	"""Abstract Base class of Paint Tools"""

	def __init__(self,**args):
		super().__init__(**args)
		default = {}
		default['state'] = 'up'
		default['border'] = 0.1
		default['iconname'] = ""
		default['toolimage'] = None
		default['name'] = ""
		default['option'] = VBoxLayout()
		default['selected'] = False
		img = {}
		img['over'] = ExSurface((256,256),CORAL)
		img['down'] = ExSurface((256,256),BROWN)
		img['up'] = ExSurface((256,256),SILVER)
		default['images'] = img
		self.setDefault(default,args)

		def mo():
			self['state'] = 'over'

		def mp():
			self['state'] = 'down'


		self.mouseOver.connect(mo)
		self.mouseLeftPress.connect(mp)
		self.mouseLeftUp.connect(self.active)
		self.Spress = Slot(self.press)
		self.Sdown = Slot(self.down)
		self.Sup = Slot(self.up)
		self.Sover = Slot(self.over)

		self.actived = Signal()

	def active(self):
		"""when tool active"""
		self['canvas'].setTool(self)
		self.actived(self)
		self.onActive()

	def onActive(self):
		pass

	def over(self):

		pass

	def down(self):
		pass

	def press(self):
		pass

	def up(self):
		pass

	def update(self):
		self['state'] = 'up'

	def resize(self,size):
		self['size'] = size
		left = int(size[0]*self['border'])
		top = int(size[1]*self['border'])
		x = int(size[0]*(1-self['border']*2))
		y = int(size[1]*(1-self['border']*2))
		self['toolimage'].resize((x,y))
		self['toolimage']['pos']= (left,top)
		for key in self['images']:
			self['images'][key] = ResizeImage(self['images'][key],size)

	def draw(self,screen):
		surf = self['images'][self['state']].copy()
		self['toolimage'].draw(surf)
		if self['selected']:
			pygame.draw.rect(surf.surface,(98,162,228),pygame.Rect((0,0),pos_minus(self['size'],(1,1))),2)
		screen.blit(surf,self['pos'])

	def setCanvas(self,c):
		"""assign canvas to tool"""
		self['canvas'] = c

	def valid(self,pos):
		"""if mouse inside canvas"""
		if self['canvas']['surface'].get_rect().collidepoint(pos):
			return True
		return False

	def cleanup(self):
		return


class PencilTool(PaintTool):
	"""Paint Toool:Pencil, draw pencil line"""

	def __init__(self,**args):
		super().__init__(**args)
		self['toolimage'] = Image(filename ="res/pencil.png")
		self['name'] = "Pencil"
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

		wl = Label(text = 'SIZE: 1',fontsize = 20)
		def changetoolsize(w):
			self['toolsize'] = int(w)
			wl.setText('SIZE: %d'%w)

		changetoolsize(1)

		ws = Slider(bgcolor = local.theme['DIALOGBACKGROUND'],range = (1,10),value = self['toolsize'])
		ws.valueChanged.connect(changetoolsize)

		self['option'].add(wl)
		self['option'].add(ws)
		self['option'].add(Spacing(sizehint = [10,20]))

	def down(self):
		self.oldpos = self['canvas'].canvasPos()
		local.gui.mouseLeftPress.connectSlot(self.Spress)
		local.gui.mouseLeftUp.connectSlot(self.Sup)

	def press(self):
		newp = self['canvas'].canvasPos()
		sf = self['canvas']['surface'].surface
		pygame.draw.circle(sf, CurrentColor, newp, self['toolsize'])
		dist = (( newp[0]-self.oldpos[0])**2 + (newp[1]-self.oldpos[1])**2)**0.5
		if dist == 0:  dist = 1
		sx,sy = pos_div(pos_minus(newp,self.oldpos),dist)
		for i in range(int(dist)):
			pygame.draw.circle(sf, CurrentColor, (int(self.oldpos[0]+ i*sx), int(self.oldpos[1] + i*sy)),  self['toolsize'])
		self.oldpos = newp

	def up(self):
		local.gui.mouseLeftPress.disconnectSlot(self.Spress)
		local.gui.mouseLeftUp.disconnectSlot(self.Sup)
		self['canvas'].addHistory()

class EraserTool(PaintTool):
	"""Paint Tool: Eraser, erase area"""

	def __init__(self,**args):
		super().__init__(**args)
		self['name'] = "Eraser"
		self['toolimage'] = Image(filename ="res/eraser.png")
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

		wl = Label(text = 'SIZE: 1',fontsize = 20)
		def changetoolsize(w):
			self['toolsize'] = int(w),int(w)
			wl.setText('SIZE: %d'%w)

		changetoolsize(10)

		ws = Slider(bgcolor = local.theme['DIALOGBACKGROUND'],range = (5,20),value = self['toolsize'][0])
		ws.valueChanged.connect(changetoolsize)

		self['option'].add(wl)
		self['option'].add(ws)
		self['option'].add(Spacing(sizehint = [10,20]))


	def over(self):

		newp = pos_minus(self['canvas'].canvasPos(),self['toolsize'])
		pygame.draw.rect(self['canvas']['overlay'].surface,CurrentColor,(newp,pos_mul(self['toolsize'],2)),1)

	def down(self):
		self.oldp = self['canvas'].canvasPos()
		local.gui.mouseLeftPress.connectSlot(self.Spress)
		local.gui.mouseLeftUp.connectSlot(self.Sup)

	def press(self):
		pos = self['canvas'].canvasPos()
		newul = pos_minus(pos,self['toolsize'])
		newur = pos_minus(pos,(-self['toolsize'][0],self['toolsize'][1]))
		newdr = pos_plus(pos,self['toolsize'])
		newdl = pos_plus(pos,(-self['toolsize'][0],self['toolsize'][1]))
		oldul = pos_minus(self.oldp,self['toolsize'])
		oldur = pos_minus(self.oldp,(-self['toolsize'][0],self['toolsize'][1]))
		olddr = pos_plus(self.oldp,self['toolsize'])
		olddl = pos_plus(self.oldp,(-self['toolsize'][0],self['toolsize'][1]))
		pygame.draw.polygon(self['canvas']['surface'].surface,WHITE,convex_hull([newul,newur,newdr,newdl,oldul,oldur,olddr,olddl]))
		self.oldp = pos

	def up(self):
		local.gui.mouseLeftPress.disconnectSlot(self.Spress)
		local.gui.mouseLeftUp.disconnectSlot(self.Sup)
		self['canvas'].addHistory()

class ClearTool(PaintTool):
	"""Paint Tool: Clear canvas"""

	def __init__(self,**args):
		super().__init__(**args)
		self['name'] = "Clear Screen"
		self['toolimage'] = Label(fontsize = 30,text = 'Clear')
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

	def onActive(self):
		self['canvas'].clear()
		self['canvas'].addHistory()

class RectTool(PaintTool):
	"""Paint Tool: draw rectangle"""

	def __init__(self,**args):
		super().__init__(**args)
		self['name'] = "Rectangle"
		surf = ExSurface((256,256),pygame.SRCALPHA)
		pygame.draw.rect(surf.surface,BLACK,(25,25,203,203),10)
		self['toolimage'] = Image(surface = surf)
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

		wl = Label(text = 'SIZE: 1',fontsize = 20)
		def changetoolsize(w):
			self['toolsize'] = int(w)
			wl.setText('SIZE: %d'%w)

		changetoolsize(1)

		ws = Slider(bgcolor = local.theme['DIALOGBACKGROUND'],range = (1,10),value = self['toolsize'])
		ws.valueChanged.connect(changetoolsize)

		self['option'].add(wl)
		self['option'].add(ws)

		bot = HBoxLayout(sizehint = [10,20])
		fb = Button(text = 'Fill')
		ufb = Button(text = 'Unfill')


		def changetoolmode(m):
			self['toolmode'] = m
			if m == 'fill':
				fb['state'] = 'selected'
				ufb['state'] = 'up'
			else:
				ufb['state'] = 'selected'
				fb['state'] = 'up'

		changetoolmode('fill')

		def fill():
			changetoolmode('fill')

		def unfill():
			changetoolmode('unfill')


		fb.mouseLeftUp.connect(fill)
		ufb.mouseLeftUp.connect(unfill)

		bot.add(fb)
		bot.add(ufb)
		self['option'].add(bot)

	def down(self):
		self.oldpos = self['canvas'].canvasPos()
		local.gui.mouseLeftPress.connectSlot(self.Spress)
		local.gui.mouseLeftUp.connectSlot(self.Sup)

	def press(self):
		rect = pygame.Rect(self.oldpos,pos_minus( self['canvas'].canvasPos(),self.oldpos))
		rect.normalize()
		if self['toolmode'] == 'fill':
			pygame.draw.rect(self['canvas']['overlay'].surface,CurrentColor,rect)
		else:
			pygame.draw.rect(self['canvas']['overlay'].surface,CurrentColor,rect,self['toolsize'])


	def up(self):
		rect = pygame.Rect(self.oldpos,pos_minus( self['canvas'].canvasPos(),self.oldpos))
		rect.normalize()
		if self['toolmode'] == 'fill':
			pygame.draw.rect(self['canvas']['surface'].surface,CurrentColor,rect)
		else:
			pygame.draw.rect(self['canvas']['surface'].surface,CurrentColor,rect,self['toolsize'])
		local.gui.mouseLeftPress.disconnectSlot(self.Spress)
		local.gui.mouseLeftUp.disconnectSlot(self.Sup)
		self['canvas'].addHistory()

class SelectTool(PaintTool):
	"""Paint Tool: select area and move"""
	def __init__(self,**args):
		super().__init__(**args)
		self['name'] = "Select and Move"
		self['toolimage'] = Image(surface = pr.resMgr.LoadImage('res/select.png'))
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

		self.Sdown2 = Slot(self.down2)
		self.Spress2 = Slot(self.press2)
		self.Sup2 = Slot(self.up2)

		bot = HBoxLayout(sizehint = [10,20])
		ctb = Button(text = 'Cut')
		cpb = Button(text = 'Copy')


		def changetoolmode(m):
			self['toolmode'] = m
			if m == 'cut':
				ctb['state'] = 'selected'
				cpb['state'] = 'up'
			else:
				cpb['state'] = 'selected'
				ctb['state'] = 'up'

		changetoolmode('cut')

		def copy():
			changetoolmode('copy')

		def cut():
			changetoolmode('cut')

		ctb.mouseLeftUp.connect(cut)
		cpb.mouseLeftUp.connect(copy)

		bot.add(ctb)
		bot.add(cpb)

		self['option'].add(bot)

	def down(self):
		self.oldpos = self['canvas'].canvasPos()
		local.gui.mouseLeftPress.connectSlot(self.Spress)
		local.gui.mouseLeftUp.connectSlot(self.Sup)

	def press(self):
		rect = pygame.Rect(self.oldpos,pos_minus( self['canvas'].canvasPos(),self.oldpos))
		rect.normalize()
		pygame.draw.rect(self['canvas']['overlay'].surface,BLACK,rect,1)

	def up(self):
		local.gui.mouseLeftPress.disconnectSlot(self.Spress)
		local.gui.mouseLeftUp.disconnectSlot(self.Sup)
		self['canvas'].mouseLeftDown.disconnectSlot(self.Sdown)
		self['canvas'].mouseLeftDown.connectSlot(self.Sdown2)

		rect = pygame.Rect(self.oldpos,pos_minus( self['canvas'].canvasPos(),self.oldpos))
		rect.normalize()
		self.sf = self['canvas']['surface'].subsurface(rect).copy()
		self.sfrect = rect


	def down2(self):
		self.oldpos = self['canvas'].canvasPos()
		local.gui.mouseLeftPress.connectSlot(self.Spress2)
		local.gui.mouseLeftUp.connectSlot(self.Sup2)

	def press2(self):
		move = pos_minus(self['canvas'].canvasPos(),self.oldpos)
		rect = self.sfrect.move(move)
		if self['toolmode'] == 'cut':
			self['canvas']['overlay'].subsurface(self.sfrect).fill(self['canvas']['backgroundcolor'])
		self['canvas']['overlay'].blit(self.sf,rect)
		pygame.draw.rect(self['canvas']['overlay'].surface,BLACK,rect,1)

	def up2(self):
		local.gui.mouseLeftPress.disconnectSlot(self.Spress2)
		local.gui.mouseLeftUp.disconnectSlot(self.Sup2)
		self['canvas'].mouseLeftDown.disconnectSlot(self.Sdown2)
		self['canvas'].mouseLeftDown.connectSlot(self.Sdown)

		move = pos_minus(self['canvas'].canvasPos(),self.oldpos)
		rect = self.sfrect.move(move)
		if self['toolmode'] == 'cut':
			self['canvas']['surface'].subsurface(self.sfrect).fill(self['canvas']['backgroundcolor'])
		self['canvas']['surface'].blit(self.sf,rect)
		self['canvas'].addHistory()

	def cleanup(self):
		local.gui.mouseLeftPress.disconnectSlot(self.Spress)
		local.gui.mouseLeftPress.disconnectSlot(self.Spress2)
		local.gui.mouseLeftUp.disconnectSlot(self.Sup)
		local.gui.mouseLeftUp.disconnectSlot(self.Sup2)
		self['canvas'].mouseLeftDown.disconnectSlot(self.Sdown)
		self['canvas'].mouseLeftDown.disconnectSlot(self.Sdown2)


class TextTool(PaintTool):
	"""Paint TOol: Draw text"""
	def __init__(self,**args):
		super().__init__(**args)
		default = {}
		default['fontsize'] = 20
		default['fontname'] = 'Arial'
		default['text'] = ""
		default['start'] = False
		self.setDefault(default,args)

		self['name'] = "Text Edit"
		self['toolimage'] = Image(surface = pr.resMgr.LoadImage('res/text.png'))
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

		self.Srt = Slot(self.rt)

		wl = Label(text = 'SIZE: 1',fontsize = 20)
		def changetoolsize(w):
			self['toolsize'] = int(w)
			self['fontsize'] = self['toolsize']
			wl.setText('SIZE: %d'%w)

		changetoolsize(15)

		ws = Slider(bgcolor = local.theme['DIALOGBACKGROUND'],range = (15,70),value = self['toolsize'])
		ws.valueChanged.connect(changetoolsize)

		self['option'].add(wl)
		self['option'].add(ws)
		self['option'].add(Spacing(sizehint = [10,20]))

	def down(self):
		self.oldpos = self['canvas'].canvasPos()
		self['start'] = True

		self['canvas'].mouseLeftDown.disconnectSlot(self.Sdown)
		self['canvas'].keyDown[pygame.K_RETURN].connectSlot(self.Srt)

	def rt(self):
		"""when press return key"""

		self['canvas']['surface'].blit(
			Label(text = self['text'][:-1],fontname = self['fontname'],
				fontsize=self['fontsize'],textcolor= CurrentColor)['surface'],self.oldpos)
		self['canvas'].keyDown[pygame.K_RETURN].disconnectSlot(self.Srt)
		self['canvas'].mouseLeftDown.connectSlot(self.Sdown)

		self['start'] = False
		self['text']= ""

	def addText(self,ks):
		"""add text to text editor"""
		text = self['text']
		for i in ks:
			if i.key == 8:
				text = text[:-1]
			elif i.key == 9:
				text +="	"
			elif i.key < 256:
				c = i.unicode
				text+=c
		self['text'] = text

	def update(self):
		super().update()

		if self['start']:
			self.addText(local.keyboard.getInput())
			ta = Label(text = self['text'],fontname = self['fontname'],
				fontsize=self['fontsize'],textcolor= CurrentColor)
			sf = ta['surface']
			self['canvas']['overlay'].blit(sf,self.oldpos)
			pygame.draw.rect(self['canvas']['overlay'].surface,BLACK,(self.oldpos,sf.get_size()),1)

class LineTool(PaintTool):
	"""Paint Tool: Draw Line"""

	def __init__(self,**args):
		super().__init__(**args)
		self['name'] = "Line"
		surf = ExSurface((256,256),pygame.SRCALPHA)
		pygame.draw.line(surf.surface,BLACK,(25,25),(203,203),15)
		self['toolimage'] = Image(surface = surf)
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

		wl = Label(text = 'SIZE: 1',fontsize = 20)
		def changetoolsize(w):
			self['toolsize'] = int(w)
			wl.setText('SIZE: %d'%w)

		changetoolsize(1)

		ws = Slider(bgcolor = local.theme['DIALOGBACKGROUND'],range = (1,10),value = self['toolsize'])
		ws.valueChanged.connect(changetoolsize)

		self['option'].add(wl)
		self['option'].add(ws)
		self['option'].add(Spacing(sizehint = [10,20]))

	def down(self):
		self.oldpos = self['canvas'].canvasPos()
		local.gui.mouseLeftPress.connectSlot(self.Spress)
		local.gui.mouseLeftUp.connectSlot(self.Sup)

	def press(self):
		pygame.draw.line(self['canvas']['overlay'].surface,CurrentColor,
			self.oldpos,self['canvas'].canvasPos(),self['toolsize'])

	def up(self):
		pygame.draw.line(self['canvas']['surface'].surface,CurrentColor,
			self.oldpos,self['canvas'].canvasPos(),self['toolsize'])
		local.gui.mouseLeftPress.disconnectSlot(self.Spress)
		local.gui.mouseLeftUp.disconnectSlot(self.Sup)
		self['canvas'].addHistory()

class CircleTool(PaintTool):
	"""Paint Tool: Draw circle"""

	def __init__(self,**args):
		super().__init__(**args)
		self['name'] = "Ellipse"
		self['toolimage'] = Image(surface = pr.resMgr.LoadImage('res/circle.png'))
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

		wl = Label(text = 'SIZE: 1',fontsize = 20)
		def changetoolsize(w):
			self['toolsize'] = int(w)
			wl.setText('SIZE: %d'%w)

		changetoolsize(1)

		ws = Slider(bgcolor = local.theme['DIALOGBACKGROUND'],range = (1,10),value = self['toolsize'])
		ws.valueChanged.connect(changetoolsize)

		self['option'].add(wl)
		self['option'].add(ws)

		bot = HBoxLayout(sizehint = [10,20])
		fb = Button(text = 'Fill')
		ufb = Button(text = 'Unfill')


		def changetoolmode(m):
			self['toolmode'] = m
			if m == 'fill':
				fb['state'] = 'selected'
				ufb['state'] = 'up'
			else:
				ufb['state'] = 'selected'
				fb['state'] = 'up'

		changetoolmode('fill')

		def fill():
			changetoolmode('fill')

		def unfill():
			changetoolmode('unfill')


		fb.mouseLeftUp.connect(fill)
		ufb.mouseLeftUp.connect(unfill)

		bot.add(fb)
		bot.add(ufb)
		self['option'].add(bot)

	def down(self):
		self.oldpos = self['canvas'].canvasPos()
		local.gui.mouseLeftPress.connectSlot(self.Spress)
		local.gui.mouseLeftUp.connectSlot(self.Sup)

	def press(self):
		rect = pygame.Rect(self.oldpos,pos_minus(self['canvas'].canvasPos(),self.oldpos))
		rect.normalize()

		if self['toolmode'] == 'fill':
			pygame.draw.ellipse(self['canvas']['overlay'].surface,CurrentColor,rect)
		elif rect[2]>2*self['toolsize'] and rect[3]>2*self['toolsize']:
			pygame.draw.ellipse(self['canvas']['overlay'].surface,CurrentColor,rect,self['toolsize'])

	def up(self):
		rect = pygame.Rect(self.oldpos,pos_minus(self['canvas'].canvasPos(),self.oldpos))
		rect.normalize()

		if self['toolmode'] == 'fill':
			pygame.draw.ellipse(self['canvas']['surface'].surface,CurrentColor,rect)
		elif rect[2]>2*self['toolsize'] and rect[3]>2*self['toolsize']:
			pygame.draw.ellipse(self['canvas']['surface'].surface,CurrentColor,rect,self['toolsize'])

		local.gui.mouseLeftPress.disconnectSlot(self.Spress)
		local.gui.mouseLeftUp.disconnectSlot(self.Sup)
		self['canvas'].addHistory()

class AirbrushTool(PaintTool):
	"""Paint Tool: Draw Airbrush/Spray"""

	def __init__(self,**args):
		super().__init__(**args)
		self['name'] = "Airbrush"
		self['toolimage'] = Image(filename ="res/spray.png")
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

		wl = Label(text = 'SIZE: 1',fontsize = 20)
		def changetoolsize(w):
			self['toolsize'] = int(w)
			wl.setText('SIZE: %d'%w)

		changetoolsize(20)

		ws = Slider(bgcolor = local.theme['DIALOGBACKGROUND'],range = (10,40),value = self['toolsize'])
		ws.valueChanged.connect(changetoolsize)

		self['option'].add(wl)
		self['option'].add(ws)
		self['option'].add(Spacing(sizehint = [10,20]))

	def down(self):
		local.gui.mouseLeftPress.connectSlot(self.Spress)
		local.gui.mouseLeftUp.connectSlot(self.Sup)

	def press(self):
		r = self['toolsize']
		for i in range(30):
			cx,cy = self['canvas'].canvasPos()
			x = random.randint(-r,r)
			ty = sqrt(r**2-x**2)
			y = int(random.random()*2*ty-ty)
			self['canvas']['surface'].set_at((cx+x,cy+y),CurrentColor)

	def up(self):
		local.gui.mouseLeftPress.disconnectSlot(self.Spress)
		local.gui.mouseLeftUp.disconnectSlot(self.Sup)
		self['canvas'].addHistory()

class FillTool(PaintTool):
	"""Paint Tool: Flood fill area"""

	def __init__(self,**args):
		super().__init__(**args)
		self['name'] = "Fill"
		self['toolimage'] = Image(filename = 'res/fill.png')
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

	def down(self):
		if not self.valid(self['canvas'].canvasPos()): return
		pc.flood_fill(self['canvas']['surface'].surface,self['canvas'].canvasPos(),CurrentColor)
		self['canvas'].addHistory()

class ColorPickerTool(PaintTool):
	"""Paint Tool: Pick a color from screen"""

	def __init__(self,**args):
		super().__init__(**args)
		self['name'] = "Color Picker"
		self['toolimage'] = Image(filename = 'res/colorpicker.png')
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

	def down(self):
		local.gui.mouseLeftPress.connectSlot(self.Spress)
		local.gui.mouseLeftUp.connectSlot(self.Sup)

	def press(self):
		pos = self['canvas'].canvasPos()
		if not self.valid(pos): return
		col = self['canvas']['surface'].get_at(pos)
		ol = self['canvas']['overlay'].surface
		pygame.draw.circle(ol,col,pos,15,1)
		pygame.draw.line(ol,BLACK,pos_minus(pos,(15,0)),pos_plus(pos,(15,0)))
		pygame.draw.line(ol,BLACK,pos_minus(pos,(0,15)),pos_plus(pos,(0,15)))
		ol.set_at(pos,col)

	def up(self):
		global CurrentColor
		CurrentColor = self['canvas']['surface'].get_at(SafeSize(self['canvas'].canvasPos()))
		local.gui.mouseLeftPress.disconnectSlot(self.Spress)
		local.gui.mouseLeftUp.disconnectSlot(self.Sup)


class NoneTool(PaintTool):
	"""Paint Tool: Empty tool just for test"""

	def __init__(self,**args):
		super().__init__(**args)
		self['toolimage'] = Image()
		size = self['toolimage']['size'][0]/(1-self['border']*2),self['toolimage']['size'][1]/(1-self['border']*2)
		if 'size' in args: size = args['size']
		self.resize(size)

class PaintCanvas(GUIObject):
	"""class of Paint Canvas, GUIObject"""

	def __init__(self,**args):
		default = {}
		default['size'] = 512,512
		default['backgroundcolor'] = WHITE
		default['background'] = ExSurface(default['size'],default['backgroundcolor'])
		default['surface'] = default['background'].copy()
		default['overlay'] = ExSurface(default['size'],pygame.SRCALPHA)
		default['tool'] = NoneTool()
		default['undostack'] = []
		default['redostack'] = []
		default['maxundo'] = 30
		default['filename'] = ""
		self.setDefault(default,args)
		super().__init__(**args)
		self.setTool(NoneTool())
		self.addHistory()
		self['saved'] = True
		self.imageSaved = Signal()

	def askForSave(self):
		"""save current image"""
		mb = YesNoCancelBox(text = 'Do you want to save changed to current image?',title = 'Save Confirm')
		mb.yes.mouseLeftUp.connect(self.saveFile)
		return mb

	def openFile(self):
		"""open a new image"""

		def _openFile():
			fn = pc.getopenfilename()
			if fn:
				try:
					sf = pygame.image.load(fn)
				except:
					MessageBox(text = 'Cannot Open File')
					return
				self.clear()
				self['surface'].blit(sf,(0,0))
				self['filename'] = fn
				pcfg.FILENAME = fn.split('/')[-1]
			self['saved'] = True
		if not self['saved']:
			mb = self.askForSave()
			mb.no.mouseLeftUp.connect(_openFile)
			mb.yes.mouseLeftUp.connect(_openFile)
		else:
			_openFile()

	def saveFile(self):
		"""save current image"""
		if self['filename']:
			pygame.image.save(self['surface'].surface,self['filename'])
		else:
			self.saveAs()
		self.imageSaved()
		self['saved'] = True

	def saveAs(self):
		"""save current image as new image"""
		fn = pc.getsavefilename()
		if fn:
			pygame.image.save(self['surface'].surface,fn)
			self['filename'] = fn
			pcfg.FILENAME = fn.split('/')[-1]
			self['saved'] = True

	def new(self):
		"""create new image"""

		def _new():
			self.clear()
			self['filename'] = ""
			self['undostack'] = []
			pcfg.FILENAME = ""
			self.addHistory()
		if not self['saved']:
			mb = self.askForSave()
			mb.yes.mouseLeftUp.connect(_new)
			mb.no.mouseLeftUp.connect(_new)
		else:
			_new()

	def addHistory(self):
		"""add history action to undo list"""
		self['undostack'].append(self['surface'].copy())
		if len(self['undostack']) > self['maxundo']: del self['undostack'][0]
		self['saved'] = False
		self['redostack'] = []

	def update(self):
		self['overlay'] = ExSurface(self['size'],pygame.SRCALPHA)
		return

	def draw(self,screen):
		screen.blit(self['surface'],self['pos'])
		screen.blit(self['overlay'],self['pos'])

	def resize(self,size):
		self['size'] = size
		old = self['surface'].copy()
		new = ExSurface(self['size'],self['backgroundcolor'])
		new.blit(old,(0,0))
		self['surface'] = new

	def clear(self):
		"""clear canvas"""
		self['surface'] = ExSurface(self['size'],self['backgroundcolor'])

	def setTool(self,tool):
		"""set active tool"""
		self.mouseLeftDown.disconnectSlot(self['tool'].Sdown)
		self.mouseOver.disconnectSlot(self['tool'].Sover)
		self['tool'].cleanup()
		self['tool'] = tool
		tool.setCanvas(self)
		self.mouseLeftDown.connectSlot(tool.Sdown)
		self.mouseOver.connectSlot(tool.Sover)
		if tool['name']:
			local.gui.statusBar.setText(tool['name']+" Tool")

	def canvasPos(self):
		"""get position of canvas"""
		pos = pos_minus(local.mouse.pos,self['screenpos'])
		pos = SafeSize(pos)
		pos = min(pos[0],self['size'][0]-1),min(pos[1],self['size'][1]-1)
		return pos

	def undo(self):
		"""undo last action"""
		if len(self['undostack']) < 2: return
		self['surface'].blit(self['undostack'][-2],(0,0))
		self['redostack'].append(self['undostack'].pop())

	def redo(self):
		"""redo last undo"""
		if not self['redostack']: return
		self['surface'].blit(self['redostack'][-1],(0,0))
		self['undostack'].append(self['redostack'].pop())

class CanvasWindow(Window):
	"""class of Canvas Window, Window"""

	def __init__(self,**args):
		args['bgcolor'] = local.theme['MENUBORDER']
		args['title'] = 'Paint Canvas'
		args['closeable'] = True
		super().__init__(**args)

		l = HBoxLayout()
		self.setLayout(l)
		self.canvas = PaintCanvas()
		self.add(self.canvas)

	def close(self):
		"""when window close"""
		self['visible'] = False


class ColorDisplay(GUIObject):
	"""Small block to display current Color"""

	def __init__(self,**args):
		super().__init__(**args)

		default = {}
		default['size'] = (512,512)
		self.setDefault(default,args)

		self.setColor(CurrentColor)

		self.mouseLeftUp.connect(ColorSelectDialog)
		self.mouseRightUp.connect(ColorEditDialog)

	def setColor(self,col):
		"""set color to new color"""
		self['color'] = CurrentColor
		self.rect = ExSurface(self['size'],self['color'])

	def resize(self,size):
		self['size'] = pos_mul(size,0.8)
		delta = pos_minus(size,self['size'])
		self['pos'] = pos_plus(self['pos'],(delta[0]//2,delta[1]//2))
		self.rect = ExSurface(self['size'],self['color'])

	def update(self):
		if self['color']!= CurrentColor:
			self.setColor(CurrentColor)

	def draw(self,screen):
		screen.blit(self.rect,self['pos'])
		pygame.draw.rect(screen.surface,BLACK,self.rect.get_rect().move(self['pos']),1)

class ToolBox(Window):
	"""Window contain Paint Tools"""

	def __init__(self,**args):
		args['resizeable'] = False
		args['title'] = 'Tool Box'
		args['size'] = (154,550)
		args['bgcolor'] = local.theme['MENUBORDER']
		args['closeable'] = True
		args['closesize'] = 'SMALL'
		super().__init__(**args)

		self.mainLay = VBoxLayout()


		l = GridLayout(grid = (5,2),sizehint = [10,50])
		l['margintop']=5
		l['marginbot']=5
		l['marginleft']=5
		l['marginright']=5
		l['spacing'] = 5

		color = ColorDisplay()
		option = Spacing(sizehint = [10,20])

		self.mainLay.add(l)
		self.mainLay.add(color)
		self.mainLay.add(option)

		self.setLayout(self.mainLay)

	def active(self,obj):
		"""active a tool"""
		obj['option']['sizehint'] = [10,20]
		self.mainLay[2]=obj['option']
		for i in self.mainLay[0]['objects']:
			if isinstance(i,PaintTool):
				i['selected'] = False
		obj['selected'] = True

	def add(self,obj,pos):
		"""add a tool """
		self['layout'][0].add(obj,pos)
		obj.actived.connect(self.active)
		obj.setCanvas(self['canvas'])

	def setCanvas(self,c):
		"""set canvas to all the tools"""
		self['canvas'] = c

	def close(self):
		"""when close"""
		self['visible'] = False



# Minesweeper
faceimg = pr.resMgr.LoadImage('res/minesweeper/face.bmp')
mineimg = pr.resMgr.LoadImage('res/minesweeper/mines.bmp')
numimg = pr.resMgr.LoadImage('res/minesweeper/num.bmp')
mineimgs = {}
minename = ["up","flag","?","touchmine","wrongflag","mine","dk",8,7,6,5,4,3,2,1,0]
for i in range(16): mineimgs[minename[i]] = mineimg.subsurface((0,i*16,16,16))
mineimgs['down'] = mineimgs[0].copy()
faceimgs = {}
facename = ["down","sunglasses","sad",":O","smile"]
for i in range(5): faceimgs[facename[i]] = faceimg.subsurface((0,i*24,24,24))

class Minesweeper(Window):
	"""a classic Minesweeper game, Window"""

	def __init__(self,**args):
		args['size'] = (200,280)
		args['title'] = "Minesweeper"
		args['resizeable'] = False
		args['bgcolor'] = (192,192,192)
		args['closeable'] = True
		super().__init__(**args)
		default = {}
		default['over'] = False
		default['minesnum'] = 10
		default['minesleft'] = 10
		default['inittime'] = time.time()
		default['timeused'] = 0
		default['minechanged'] = False
		self.setDefault(default,args)
		self['minesleft'] = self['minesnum']
		mainLay = VBoxLayout()
		topLay = HBoxLayout(sizehint= [10,15])
		mineLay = GridLayout(grid = (9,9),spacing=0,sizehint = [10,60])
		botLay = HBoxLayout()
		self.mines = []
		for i in range(9):
			l = []
			for j in range(9):
				m = Mine(number = (i,j))
				m.left.connect(self.leftClick)
				m.right.connect(self.rightClick)
				l.append(m)
			self.mines.append(l)
		for i in range(9):
			for j in range(9):
				mineLay.add(self.mines[i][j],(i,j))
		self.mineLeft = Label(text = self['minesleft'],fontsize = 20,textcolor = RED)
		self.face = MineFace()
		self.timeUse = Label(text = self['timeused'],fontsize = 20, textcolor = RED)

		topLay.add(self.mineLeft)
		topLay.add(self.face)
		topLay.add(self.timeUse)
		mainLay.add(topLay)
		mainLay.add(mineLay)
		self.setLayout(mainLay)
		self.restart()
		self.face.mouseLeftUp.connect(self.restart)

	def restart(self):
		"""restart game"""
		self['over'] = False
		self['started'] = False
		self['opened'] = 0
		self['minesleft'] = self['minesnum']
		self['minechanged'] = True
		self.face['state'] = 'smile'
		mine = random.sample(range(81), 10)
		for n,m in self.getMines():
			m['state'] = 'up'
			m['flag'] = ''
			if n in mine: m['flag'] = 'mine'
		d =[0,1, 1,1, 1,0, 1,-1, 0,-1, -1,-1, -1,0, -1,1]
		for x in range(9):
			for y in range(9):
				if not self.mines[x][y]['flag']:
					s = 0
					for i in range(8):
						tx,ty = x+d[i*2],y+d[i*2+1]
						if tx>=0 and ty>=0 and tx<9 and ty<9 and self.mines[tx][ty]['flag'] == 'mine':
							s+=1
					self.mines[x][y]['flag'] = s

	def getMines(self):
		"""generator of mines"""
		for i in range(9):
			for j in range(9):
				yield (i*9+j,self.mines[i][j])

	def update(self):
		self['layout'].update()
		t = 0
		if self['started']:
			t = int(time.time()-self['inittime'])
		if t!= self['timeused']:
			if not self['over']:
				self['timeused'] = t
				self.timeUse.setText(t)
		if self['opened']+ self['minesnum'] == 9*9:
			self.gamewin()
		if self['minechanged']:
			self.mineLeft.setText(self['minesleft'])
			self['minechanged'] = False

	def startgame(self):
		"""start new game"""
		self['inittime'] = time.time()
		self['timeused'] = 0
		self['started'] = True

	def leftClick(self,num):
		"""if left click on a block"""
		if self['over']: return
		if not self['started']: self.startgame()
		x = num[0]
		y = num[1]
		m = self.mines[x][y]
		if m['state'] == 'flag': return
		if m['flag'] == 'mine':
			self.mines[x][y]['state'] = 'touchmine'
			self.gameover()
			return
		if m['state'] == 'up' or m['state'] == 'down':
			if isinstance(m['flag'],int):
				self['opened']+=1
		m['state'] = m['flag']
		if m['flag'] == 0:
			d =[0,1, 1,1, 1,0, 1,-1, 0,-1, -1,-1, -1,0, -1,1]
			for i in range(8):
				tx,ty = x+d[i*2],y+d[i*2+1]
				if tx>=0 and ty>=0 and tx<9 and ty<9 and self.mines[tx][ty]['state'] == 'up':
					self.mines[tx][ty].mouseLeftUp()

	def rightClick(self,num):
		"""if right click on a block"""
		if self['over']: return
		x = num[0]
		y = num[1]
		m = self.mines[x][y]
		if not m['state'] in ['up','flag','?']: return
		if m['state'] == 'up':
			m['state'] = 'flag'
			self['minesleft'] -=1
		elif m['state'] == 'flag':
			m['state'] = '?'
			self['minesleft'] +=1
		elif m['state'] == '?':
			m['state'] = 'up'
		self['minechanged'] = True

	def gamewin(self):
		"""when win the game"""
		self['opened'] = 0
		self['over'] = True
		self['started'] = False
		self.face['state'] = 'sunglasses'
		self.openAll()
		MessageBox(title = 'You Win',text = 'Good job!\nYou win!\nTime: %d second'%self['timeused'])

	def gameover(self):
		"""when lose the game"""
		self['over'] = True
		self['started'] = False
		self.face['state'] = 'sad'
		self.openAll()
		MessageBox(title = 'Game Over',text = 'HAHAHAAHHA\nGame Over!')

	def openAll(self):
		"""open all the mines"""
		for n,m in self.getMines():
			if m['state'] == 'flag' and m['flag']!='mine':
				m['state'] = 'wrongflag'
			elif m['flag'] == 'mine' and m['state']!='touchmine':
				m['state'] = 'mine'
			elif m['state'] != 'touchmine':
				m['state'] = m['flag']

class Mine(GUIObject):
	"""class of mine, GUIObject"""

	def __init__(self,**args):
		super().__init__(**args)
		default = {}
		default['state'] = 'up'
		default['flag'] = 0
		default['number'] = (0,0)
		self.setDefault(default,args)
		self.left = Signal()
		self.right = Signal()

		def mp():
			if self['state'] == 'up':
				self['state'] = 'down'

		def mu():
			self.left(self['number'])

		def ru():
			self.right(self['number'])
		self.mouseRightUp.connect(ru)
		self.mouseLeftUp.connect(mu)
		self.mouseLeftPress.connect(mp)
		self['size'] = (18,18)

	def resize(self,size):
		delta = pos_minus(size,self['size'])
		self['pos'] = pos_plus(self['pos'],(delta[0]//2,delta[1]//2))

	def update(self):
		if self['state'] == 'down':
			self['state'] = 'up'

	def draw(self,screen):
		screen.blit(mineimgs[self['state']],self['pos'])

class MineFace(GUIObject):
	"""class of smiling face , GUIObject"""

	def __init__(self,**args):
		super().__init__(**args)
		default = {}
		default['filename'] = ""
		default['state'] = 'smile'
		self.setDefault(default,args)
		self['size'] = (24,24)

		def mp():
			if self['state'] == 'smile':
				self['state'] = 'down'
		self.mouseLeftPress.connect(mp)

	def update(self):
		if self['state'] == 'down':
			self['state'] = 'smile'

	def resize(self,size):
		delta = pos_minus(size,self['size'])
		self['pos'] = pos_plus(self['pos'],(delta[0]//2,delta[1]//2))

	def draw(self,screen):
		screen.blit(faceimgs[self['state']],self['pos'])
