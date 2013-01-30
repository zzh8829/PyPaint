@echo off
set path=%path%;E:\PortableApps\CommonFiles\MinGW\bin
E:\PortableApps\CommonFiles\Python32\python.exe setup.py build --compiler=mingw32
pause