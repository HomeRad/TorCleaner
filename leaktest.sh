#!/bin/sh
# install valgrind to run this script
#F=/home/calvin/documents/iptables-tutorial.html
#F=test/html/1.html
#valgrind --leak-check=yes python2.1 -d test/filterfile.py $F
valgrind --leak-check=yes python webcleaner startfunc
