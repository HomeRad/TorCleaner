#!/bin/sh
# install valgrind to run this script
F=test/html/script2.html
valgrind --leak-check=yes test/filterfile.py $F 2>/dev/stdout | tee leak.log
#valgrind --leak-check=yes --trace-signals=yes python webcleaner startfunc 2>/dev/stdout | tee leak.log
