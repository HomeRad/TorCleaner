#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
import os, sys
_profile = "filter.prof"
if not os.path.exists(_profile):
    sys.stderr.write(i18n._("Could not find profiling file %s.")%_profile)
    sys.stderr.write(i18n._("Please run one of test/prof*.py to generate it."))
    sys.exit(1)
import pstats
stats = pstats.Stats(_profile)
stats.strip_dirs().sort_stats("cumulative").print_stats(25)
sys.exit(0)
