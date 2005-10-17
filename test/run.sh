#!/bin/sh
# run python interpreter with current dir as search path, and remove all
# locale settings
PYVER=2.4
env -u LANGUAGE -u LC_ALL -u LC_CTYPE LANG=C WC_DEVELOPMENT=1 PYTHONPATH=`pwd` python$PYVER "$@"
