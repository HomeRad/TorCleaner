# -*- coding: iso-8859-1 -*-
import os
from wc.proxy import norm_url

def _test():
    url = "http://server/..%5c..%5c..%5c..%5c..%5c..%5..%5c..%5ccskin.zip"
    print norm_url(url)

_test()
