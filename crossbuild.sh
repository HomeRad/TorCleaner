#!/bin/sh
# generate a windows .exe binary installer
TARGET=i386-mingw32
HOST=i386-mingw32
#HOST=i386-mingw32msvc
BUILD=i686-pc-linux-gnu
# for other build boxen you might want to use:
#BUILD=i386-linux
CC=/usr/bin/i586-mingw32msvc-gcc \
  CXX=/usr/bin/i586-mingw32msvc-g++ \
  AR=/usr/bin/i586-mingw32msvc-ar \
  RANLIB=/usr/bin/i586-mingw32msvc-ranlib \
 ./configure --target=$TARGET --host=$HOST --build=$BUILD \
 2>&1 | tee crossbuild.log
make crossbuild 2>&1 | tee --append crossbuild.log
