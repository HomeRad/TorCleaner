#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-

def _main ():
    """USAGE: test/run.sh test/exportratings.py <.html file>"""
    from test import initlog
    initlog("test/logging.conf")
    import wc
    wc.config = wc.Configuration()
    from wc.filter.Rating import rating_exportall
    rating_exportall()


if __name__=='__main__':
    _main()
