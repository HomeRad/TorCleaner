# -*- coding: iso-8859-1 -*-
""" test script to test filtering"""

import os, wc
wc.config = wc.Configuration()
wc.config['filters'] = ['Rewriter', 'BinaryCharFilter']
wc.config.init_filter_modules()
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY
attrs = get_filterattrs("", [FILTER_RESPONSE_MODIFY])
fp = file(os.path.join(os.getcwd(), "test", "html", "rewrite.html"))
htmldata = fp.read()
print applyfilter(FILTER_RESPONSE_MODIFY, htmldata, 'finish', attrs)
