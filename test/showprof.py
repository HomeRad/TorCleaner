#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
def _main ():
    import pstats
    stats = pstats.Stats("filter.prof")
    stats.strip_dirs().sort_stats("cumulative").print_stats(25)

if __name__=='__main__':
    _main()
