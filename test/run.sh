#!/bin/sh
# run python interpreter with current dir as search path, and remove all
# locale settings
env -u LANGUAGE -u LC_ALL -u LC_CTYPE -u LANG PYTHONPATH=`pwd` python $*
