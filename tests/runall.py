# -*- coding: iso-8859-1 -*-
import unittest, os, getopt, sys

def get_test_files ():
    return [p for p in os.listdir('tests')
            if p.startswith('Test') and p.endswith('.py')]


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
    for fname in get_test_files():
        klass = os.path.splitext(fname)[0]
        exec 'from tests.%s import suite' % klass
        mysuite.addTest(suite)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(mysuite)


if __name__=='__main__':
    verbosity = parse_args(sys.argv)
    runall(verbosity)
