#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-

import sys

def _main (args):
    import wc.configuration
    wc.configuration.config = wc.configuration.init()
    import wc.magic
    print repr(wc.magic.classify(open(args[0])))


if __name__ == '__main__':
    _main(sys.argv[1:])
