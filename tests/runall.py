#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import unittest, os, getopt, sys


def usageExit (msg=None):
    if msg:
        print msg
    print """Usage: test/run.sh tests/runall.py [options]

Options:
  -h, --help       Show this message
  -v, --verbose    Verbose output
  -q, --quiet      Minimal output
"""
    sys.exit(2)


def parse_args (argv):
    verbosity = 1
    try:
        options, args = getopt.getopt(argv[1:], 'hHvq',
                                      ['help','verbose','quiet'])
        for opt, value in options:
            if opt in ('-h','-H','--help'):
                usageExit()
            if opt in ('-q','--quiet'):
                verbosity = 0
            if opt in ('-v','--verbose'):
                verbosity = 2
    except getopt.error, msg:
        usageExit(msg)
    return verbosity


def runall (verbosity):
    mysuite = unittest.TestSuite()
    gettests('tests', mysuite)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(mysuite)


def gettests (dirname, suite):
    for fname in os.listdir(dirname):
        fullname = os.path.join(dirname, fname)
        if os.path.isfile(fullname) and \
           fname.startswith('Test') and fname.endswith('.py'):
            addtest(dirname, fname, suite)
        elif os.path.isdir(fullname):
            gettests(fullname, suite)


def addtest (dirname, fname, mysuite):
    pkg = dirname.replace(os.path.sep, ".")
    klass = os.path.splitext(fname)[0]
    try:
        exec 'from %s.%s import suite' % (pkg, klass)
        mysuite.addTest(suite)
    except ImportError, msg:
        print "oops", msg
        pass


if __name__=='__main__':
    verbosity = parse_args(sys.argv)
    runall(verbosity)
