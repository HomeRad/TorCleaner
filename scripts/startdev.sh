#!/bin/sh
CONFIG=${1:-localconfig}
if [ "$CONFIG" = "localconfig" ]; then
    export WC_DEVELOPMENT=1
fi
PYVER=2.5
exec env -u ftp_proxy -u http_proxy -u LANGUAGE -u LC_ALL -u LC_CTYPE \
  LANG=C PYTHONPATH=`pwd` python${PYVER} ${PYOPTS:-} \
  webcleaner --config=$CONFIG --no-file-logs
