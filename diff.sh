#!/bin/sh
PYTHON=/usr/bin/python2.2

$PYTHON webcleaner restart
sleep 4
env http_proxy="" wget -t1 -O unfiltered.html $1
env http_proxy="http://localhost:8080" wget -t1 -O filtered.html $1
#diff -BuN unfiltered.html filtered.html
#rm -f unfiltered.html filtered.html
