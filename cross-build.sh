#!/bin/sh
# cross compilation Linux -> Win32 script
TARGET=i386-mingw32
HOST=i386-mingw32
#HOST=i386-mingw32msvc
BUILD=i686-pc-linux-gnu
# for other build boxen you might want to use:
# BUILD=i386-linux
CC=/usr/bin/i586-mingw32msvc-gcc ./configure \
	--target=$TARGET --host=$HOST --build=$BUILD
# now if you have a cross-compilation of python, you could do:
#CC=/usr/bin/i586-mingw32msvc-gcc /usr/local/bin/python-win setup.py build_ext
#
