#!/bin/sh
set -e
T=example
echo "start server"
test/run.sh test/server.py start $T
echo "start client"
test/run.sh test/client.py $T
echo "stop server"
test/run.sh test/server.py stop
