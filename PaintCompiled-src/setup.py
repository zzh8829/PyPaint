from distutils.core import setup, Extension

module1 = Extension('PaintCompiled',
                    include_dirs = ['E:/PortableApps/CommonFiles/SDL/include'],
                    libraries = ['SDL','SDLmain','Comdlg32'],
                    library_dirs = ['E:/PortableApps/CommonFiles/SDL/lib'],
                    sources = ['PaintC.c'])

setup (name = 'PaintCompiled',
       version = '1.0',
       description = 'This is a module written in C language for speeding up my Paint Program',
       ext_modules = [module1])
