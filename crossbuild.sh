#!/bin/sh
# generate a windows .exe binary installer
TARGET=i386-mingw32
HOST=i386-mingw32
#HOST=i386-mingw32msvc
BUILD=i686-pc-linux-gnu
# for other build boxen you might want to use:
#BUILD=i386-linux
CC=i586-mingw32msvc-gcc \
  CXX=i586-mingw32msvc-g++ \
  AR=i586-mingw32msvc-ar \
  RANLIB=i586-mingw32msvc-ranlib \
 ./configure --target=$TARGET --host=$HOST --build=$BUILD
make crossbuild
