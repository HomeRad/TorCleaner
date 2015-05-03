#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Test MIME type guessing.
"""

import sys

def _main(args):
    """
    Read file and guess MIME type.
    """
    import wc.configuration
    wc.configuration.init()
    import wc.magic
    for arg in args:
        fp = open(arg)
        try:
            print repr(wc.magic.classify(fp))
        finally:
            fp.close()


if __name__ == '__main__':
    _main(sys.argv[1:])
