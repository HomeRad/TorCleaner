#!/bin/sh
# restart the webcleaner proxy, logging to local files
# used for development test runs
rm -f webcleaner.log* webcleaner.err
test/run.sh webcleaner stopwatch
test/run.sh webcleaner startwatch 2> webcleaner.err
if [ "x$1" != "x" ]; then
    sleep 5
    env http_proxy="http://localhost:8080" wget "$1"
fi
