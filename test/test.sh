#!/bin/sh
if ifconfig eth1 | grep RUNNING > /dev/null; then
    echo "Network resource available"
    RES_NETWORK="--resource=network"
else
    echo "Network disabled"
    RES_NETWORK=""
fi
if waitfor -w 1 port:localhost:8081; then
    echo "Proxy resource available"
    RES_PROXY="--resource=proxy"
else
    echo "Proxy disabled"
    RES_PROXY=""
fi
test/run.sh test.py $RES_NETWORK $RES_PROXY --search-in=wc -ufpv "$@"
