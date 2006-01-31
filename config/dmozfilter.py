#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
"""
filter the big dmoz file
Usage:
zcat content.rdf.u8.gz | dmozfilter.py | gzip --best > dmoz.rdf.stripped.gz
Note: the dmoz content license is not GPL compatible, so you may not
distribute it with WebCleaner!
"""
import fileinput
topic = None
for line in fileinput.input()
    line = line.strip()
    if line.startswith("<Topic r:id="):
        _topic = line[13:line.rindex('"')]
        if "/" in _topic:
            topic = _topic.split("/", 2)[1].lower()
    elif line.startswith("</Topic>"):
        topic = None
    if topic=='kids_and_teens':
        print line
