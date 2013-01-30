#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <pygame/pygame.h>

static PyObject* fill_surface(PyObject* self, PyObject* args)
{
	PyObject* surface = NULL;
	if( !PyArg_ParseTuple(args, "O", &surface) )
	return NULL;
	PySurfaceObject* c_surface = (PySurfaceObject*) surface;
	SDL_FillRect( c_surface->surf, 0, SDL_MapRGB(c_surface->surf->format, 255, 0, 0) );
	Py_RETURN_NONE;
}

static int bpp;
typedef Uint32 Pixel;
typedef int bool;
typedef struct {int y, xl, xr, dy;} Segment;

Pixel pixelread(SDL_Surface *surface, int x, int y)
{
	Uint8 *p = (Uint8 *)surface->pixels + y * surface->pitch + x * bpp;
	switch(bpp) {
	case 1:
		return *p;
		break;

	case 2:
		return *(Uint16 *)p;
		break;

	case 3:
		if(SDL_BYTEORDER == SDL_BIG_ENDIAN)
		return p[0] << 16 | p[1] << 8 | p[2];
		else
		return p[0] | p[1] << 8 | p[2] << 16;
		break;

	case 4:
		return *(Uint32 *)p;
		break;

	default:
		return 0;   
	}
}

void pixelwrite(SDL_Surface *surface, int x, int y, Uint32 pixel)
{
	Uint8 *p = (Uint8 *)surface->pixels + y * surface->pitch + x * bpp;
	switch(bpp) {
	case 1:
		*p = pixel;
		break;

	case 2:
		*(Uint16 *)p = pixel;
		break;

	case 3:
		if(SDL_BYTEORDER == SDL_BIG_ENDIAN) {
			p[0] = (pixel >> 16) & 0xff;
			p[1] = (pixel >> 8) & 0xff;
			p[2] = pixel & 0xff;
		} else {
			p[0] = pixel & 0xff;
			p[1] = (pixel >> 8) & 0xff;
			p[2] = (pixel >> 16) & 0xff;
		}
		break;
	case 4:
		*(Uint32 *)p = pixel;
		break;
	}
}

#define MAXDEPTH 1000000
Segment stack[MAXDEPTH];
#define PUSH(Y, XL, XR, DY)\
	if (sp<stack+MAXDEPTH && Y+(DY)>=0 && Y+(DY)<=sf->h) \
	{sp->y = Y; sp->xl = XL; sp->xr = XR; sp->dy = DY; sp++;}
#define POP(Y, XL, XR, DY)\
	{sp--; Y = sp->y+(DY = sp->dy); XL = sp->xl; XR = sp->xr;}
void fill(SDL_Surface* sf,int x, int y,Pixel nv)
{
	int l, x1, x2, dy;
	Pixel ov;
	Segment *sp = stack;	
	ov = pixelread(sf,x, y);
	if (ov==nv || x<0 || x>sf->w || y<0 || y>sf->h) return;
	PUSH(y, x, x, 1);
	PUSH(y+1, x, x, -1);	
	while (sp>stack) {
		POP(y, x1, x2, dy);
		for (x=x1; x>=0 && pixelread(sf,x, y)==ov; x--)
		pixelwrite(sf,x, y, nv);
		if (x>=x1) goto skip;
		l = x+1;
		if (l<x1) PUSH(y, l, x1-1, -dy);
		x = x1+1;
		do {
			for (; x<=sf->w && pixelread(sf,x, y)==ov; x++)
			pixelwrite(sf,x, y, nv);
			PUSH(y, l, x-1, dy);
			if (x>x2+1) PUSH(y, x2+1, x-1, -dy);
skip:		for (x++; x<=x2 && pixelread(sf,x, y)!=ov; x++);
			l = x;
		} while (x<=x2);
	}
}

typedef struct P{int x,y;} PT;
#define MAXSTACK 100000
PT STACK[MAXSTACK];
int sn = 0;

void emptyStack()
{
	sn = 0;
	memset(STACK,0,sizeof(STACK));
}

int push(int x,int y)
{
	STACK[sn].x = x;
	STACK[sn].y = y;
	sn++;
	if (sn>MAXSTACK) return 0;
	return 1;
}

int pop(int *x,int *y)
{
	sn-=1;
	if(sn<0)
	{
		sn = 0;
		return 0;
	}
	*x = STACK[sn].x;
	*y = STACK[sn].y;
	return 1;
}
	

void new_ff(SDL_Surface * sf,int x, int y, int newColor)
{
	Uint32 oldColor = pixelread(sf,x,y);
    if(oldColor == newColor) return;
    emptyStack();
    
	int h = sf->h;
	int w = sf->w;
    int y1; 
    bool spanLeft, spanRight;
    
    push(x, y);
    
    while(pop(&x, &y))
    {    
        y1 = y;
        while(y1 >= 0 && pixelread(sf,x,y1) == oldColor) y1--;
        y1++;
        spanLeft = spanRight = 0;
        while(y1 < h && pixelread(sf,x,y1) == oldColor )
        {
            pixelwrite(sf,x,y1,newColor);
            if(!spanLeft && x > 0 && pixelread(sf,x - 1,y1) == oldColor) 
            {
                if(!push(x - 1, y1)) return;
                spanLeft = 1;
            }
            else if(spanLeft && x > 0 && pixelread(sf,x - 1,y1) != oldColor)
            {
                spanLeft = 0;
            }
            if(!spanRight && x < w - 1 && pixelread(sf,x + 1,y1) == oldColor) 
            {
                if(!push(x + 1, y1)) return;
                spanRight = 1;
            }
            else if(spanRight && x < w - 1 && pixelread(sf,x + 1,y1) != oldColor)
            {
                spanRight = 0;
            } 
            y1++;
        }
    }
}


typedef struct
{
    PyObject_HEAD
    /* RGBA */
    Uint8 r;
    Uint8 g;
    Uint8 b;
    Uint8 a;
    Uint8 len;
} PyColor;

FILE* out;

static int
ObjToColor(PyObject* obj,Uint8* rgba)
{
	if(PyTuple_Check(obj))
	{
		rgba[0] = PyLong_AsLong(PyTuple_GetItem(obj,0));
		rgba[1] = PyLong_AsLong(PyTuple_GetItem(obj,1));
		rgba[2] = PyLong_AsLong(PyTuple_GetItem(obj,2));
		return 1;
	}
	else
	{
		rgba[0] = PyLong_AsLong(PyObject_GetAttr(obj,Py_BuildValue("s","r")));
		rgba[1] = PyLong_AsLong(PyObject_GetAttr(obj,Py_BuildValue("s","g")));
		rgba[2] = PyLong_AsLong(PyObject_GetAttr(obj,Py_BuildValue("s","b")));
        return 1;
	}
	return 0;
}

static PyObject* flood_fill(PyObject* self, PyObject* args)
{
	PyObject* po = NULL;
	PyObject* colorobj = NULL;
	Uint32 color;
	Uint8 rgba[4]={0};
	int x,y;
	if (! PyArg_ParseTuple(args,"O(ii)O",&po,&x,&y,&colorobj))
		return NULL;

	PySurfaceObject* pso = (PySurfaceObject*)po;
	SDL_Surface* sf = pso->surf;
	bpp = sf->format->BytesPerPixel;

	if(PyLong_Check(colorobj))
		color = (Uint32)PyLong_AsLong(colorobj);
	else if(ObjToColor(colorobj,rgba))
		color = SDL_MapRGB(sf->format, rgba[0], rgba[1], rgba[2]);
	// fill(sf,x,y,color);
	// For some unknow reason, old flood fill is not working with large surface :(
	// So i wrote a new version of flood fill called new_ff :D 
	new_ff(sf,x,y,color);
	Py_RETURN_NONE;
}

#include <windows.h>
#include <string.h>
#include <stdio.h>

static
void unlockmouse() {

	OSVERSIONINFO	vi;

	memset (&vi, 0, sizeof(vi));
	vi .dwOSVersionInfoSize = sizeof(vi);
	GetVersionEx (&vi);
	if (vi.dwMajorVersion >= 6) return;

	keybd_event(VK_LWIN,0xb8,0 , 0); 
	keybd_event(VK_LWIN,0x8f, KEYEVENTF_KEYUP,0);
	Sleep(50);
	keybd_event(VK_LWIN,0xb8,0 , 0); 
	keybd_event(VK_LWIN,0x8f, KEYEVENTF_KEYUP,0);
}

static 
PyObject* openfilename(PyObject* self,PyObject* args) {

	unlockmouse();
	OPENFILENAME ofn;
	char fileName[MAX_PATH] = "";
	ZeroMemory(&ofn, sizeof(ofn));
	ofn.lStructSize = sizeof(OPENFILENAME);
	ofn.hwndOwner = NULL;
	ofn.lpstrFilter = "All Files (*.*)\0*.*\0";
	ofn.lpstrFile = fileName;
	ofn.nMaxFile = MAX_PATH;
	ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_HIDEREADONLY;
	ofn.lpstrDefExt = "";
	if (! GetOpenFileName(&ofn) )
		Py_RETURN_NONE;
	return Py_BuildValue("s",fileName);
}

static 
PyObject* savefilename(PyObject* self,PyObject* args) {

	unlockmouse();

	OPENFILENAME ofn;
	char fileName[MAX_PATH] = "";
	ZeroMemory(&ofn, sizeof(ofn));
	ofn.lStructSize = sizeof(OPENFILENAME);
	ofn.hwndOwner = NULL;
	ofn.lpstrFilter = "All Files (*.*)\0*.*\0";
	ofn.lpstrFile = fileName;
	ofn.nMaxFile = MAX_PATH;
	ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_HIDEREADONLY;
	ofn.lpstrDefExt = "";
	if (! GetSaveFileName(&ofn) )
		Py_RETURN_NONE;
	return Py_BuildValue("s",fileName);
}


PyMethodDef methods[] = 
{
	{"fill_surface", fill_surface, METH_VARARGS, "fill surface to red"},
	{"flood_fill",flood_fill,METH_VARARGS,"Super Fast Flood Fill"},
	{"getopenfilename",openfilename,METH_VARARGS,"Get Open File Name"},
	{"getsavefilename",savefilename,METH_VARARGS,"Get Save File Name"},
	{NULL, NULL, 0, NULL},
};

static struct PyModuleDef PaintCompiledModule = {
	PyModuleDef_HEAD_INIT,
	"PaintCompiled",
	"Compiled C code for Paint",
	-1,
	methods
};

PyMODINIT_FUNC
PyInit_PaintCompiled(void)
{
	return PyModule_Create(&PaintCompiledModule);
}