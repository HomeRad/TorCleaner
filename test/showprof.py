#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-

def _main (fname):
    import hotshot.stats
    stats = hotshot.stats.load(fname)
    stats.strip_dirs()
    stats.sort_stats('time', 'calls')
    stats.print_stats(25)

if __name__=='__main__':
    import sys
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = "filter.prof"
    _main(fname)
