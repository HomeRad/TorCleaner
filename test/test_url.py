# -*- coding: iso-8859-1 -*-
import os
from wc.proxy import url_norm, url_quote

def _test():
    url = "http://server/..%5c..%5c..%5c..%5c..%5c..%5..%5c..%5ccskin.zip"
    print url_quote(url_norm(url))

_test()
