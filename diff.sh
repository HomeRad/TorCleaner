#!/bin/sh
PYTHON=/usr/bin/python2.1

$PYTHON webcleaner restart
sleep 4
env http_proxy="" wget -t1 -O unfiltered.html $1
# use CalZilla as User-Agent, some sites are blocking spiders (eg. IMDB)
env http_proxy="http://localhost:9090" wget -t1 -U CalZilla -O filtered.html $1
diff -BuN unfiltered.html filtered.html
rm -f unfiltered.html filtered.html
