#!/bin/sh
# install valgrind to run this script
valgrind --leak-check=yes python -d test/parsefile.py
