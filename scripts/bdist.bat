@echo off
REM batch file for generating the windows .exe installer
set PYTHON="c:\Python25\python.exe"
%PYTHON% setup.py clean --all
%PYTHON% setup.py sdist --manifest-only
%PYTHON% setup.py build -c mingw32 bdist_wininst -b tacho.bmp
REM start resource editor for .exe icon
REM "%PROGRAMFILES%\XN Resource Editor\XNResourceEditor.exe"
