#!/bin/sh
env -u LANGUAGE -u LC_ALL -u LC_CTYPE -u LANG PYTHONPATH=`pwd` python test/regrtest.py $*
