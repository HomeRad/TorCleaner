#!/bin/sh -e
# network device, change as appropriate
NETDEV=ppp0
if ifconfig $NETDEV | grep RUNNING > /dev/null; then
    echo "--resource=network"
fi

if msgfmt -V > /dev/null 2>&1; then
    echo "--resource=msgfmt"
fi

PROXY=localhost:8081
if waitfor -w 1 port:$PROXY; then
    echo "--resource=proxy"
fi

os=`python -c "import os; print os.name"`
if [ "x$os" = "xposix" ]; then
    echo "--resource=posix"
fi
