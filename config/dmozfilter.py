#!/usr/bin/python2.3
# filter the big dmoz file
# usage:
# zcat content.rdf.u8.gz | dmozfilter.py | gzip --best > dmoz.rdf.stripped.gz
import sys
line = sys.stdin.readline()
topic = None
while line:
    line = line.strip()
    if line.startswith("<Topic r:id="):
        _topic = line[13:line.rindex('"')]
        if "/" in _topic:
            topic = _topic.split("/", 2)[1].lower()
    elif line.startswith("</Topic>"):
        topic = None
    if topic=='kids_and_teens':
        print line
    line = sys.stdin.readline()
