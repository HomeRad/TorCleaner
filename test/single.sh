#!/bin/sh
# restart the webcleaner proxy, logging to local files
# used for development test runs
rm -f webcleaner.log webcleaner.err
./webcleaner restart 2> webcleaner.err
if [ "x$1" != "x" ]; then
    sleep 3
    env http_proxy="http://localhost:8080" wget "$1"
fi
