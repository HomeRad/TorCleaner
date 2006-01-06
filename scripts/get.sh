#!/bin/sh
env http_proxy="http://localhost:8081" wget --no-check-certificate -O /dev/null "$1"
# note: curl has problems with chunked encoding
#TRACE=--trace curltrace.txt
#curl $TRACE -i -k -x localhost:8081 "$1"
