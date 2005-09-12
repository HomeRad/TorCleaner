#!/bin/sh -e
if ifconfig eth1 | grep RUNNING > /dev/null; then
    echo "Network resource available"
    RES_NETWORK="--resource=network"
else
    echo "Network disabled"
    RES_NETWORK=""
fi
PROXY=localhost:8081
if waitfor -w 1 port:$PROXY; then
    echo "Proxy resource available"
    RES_PROXY="--resource=proxy"
else
    echo "Proxy disabled"
    RES_PROXY=""
fi
if [ -n "$RES_PROXY" ]; then
    NAMES="index config filterconfig update rating help"
    for NAME in $NAMES; do
        URL="http://$PROXY/${NAME}.html"
        echo "Validating $URL"
        curl -s $URL | xmllint --html --noout --valid -
        URL1="${URL}.de"
        echo "Validating $URL1"
        curl -s $URL1 | xmllint --html --noout --valid -
        URL1="${URL}.en"
        echo "Validating $URL1"
        curl -s $URL1 | xmllint --html --noout --valid -
    done
fi
test/run.sh test.py $RES_NETWORK $RES_PROXY --search-in=wc -ufpv "$@"
