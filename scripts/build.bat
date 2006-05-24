@echo off
set PYTHON="c:\Python 24\python.exe"
%PYTHON% setup.py sdist --manifest-only
%PYTHON% setup.py build -c mingw32
copy build\lib.win32-2.4\wc\HtmlParser\htmlsax.pyd wc\HtmlParser
copy build\lib.win32-2.4\wc\js\jslib.pyd wc\js
copy build\lib.win32-2.4\wc\levenshtein.pyd wc
