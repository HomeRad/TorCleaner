#!/bin/sh
# install valgrind to run this script
valgrind --leak-check=yes python wc/parser/htmllib.py
