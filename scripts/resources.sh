#!/bin/sh -e
# network device, change as appropriate
if dnsip www.fsf.org | grep -q \\.; then
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

SOCK=`grep LocalSocket /etc/clamav/clamd.conf  | awk '{print $2;}'`
if test -n $SOCK; then
    if waitfor -w 1 unix:"$SOCK"; then
        echo "--resource=clamav"
    fi
fi
