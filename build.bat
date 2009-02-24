@echo off
set PYTHON="c:\Python26\python.exe"
%PYTHON% setup.py sdist --manifest-only
%PYTHON% setup.py build -c mingw32
copy build\lib.win32-2.6\wc\HtmlParser\htmlsax.pyd wc\HtmlParser
copy build\lib.win32-2.6\wc\js\jslib.pyd wc\js
copy build\lib.win32-2.6\wc\levenshtein.pyd wc
copy build\lib.win32-2.6\wc\network\_network.pyd wc\network
