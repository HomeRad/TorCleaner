# -*- coding: iso-8859-1 -*-
import os
from wc.url import url_norm, url_quote

def _test():
    url = "http://server/..%5c..%5c..%5c..%5c..%5c..%5..%5c..%5ccskin.zip"
    print url_quote(url_norm(url))
    url = "http://groups.google.com/groups?hl=en&lr=&ie=UTF-8&threadm=3845B54D.E546F9BD%40monmouth.com&rnum=2&prev=/groups%3Fq%3Dlogitech%2Bwingman%2Bextreme%2Bdigital%2B3d%26hl%3Den%26lr%3D%26ie%3DUTF-8%26selm%3D3845B54D.E546F9BD%2540monmouth.com%26rnum%3D2"
    nurl = url_quote(url_norm(url))
    if url!=nurl:
        print url
        print nurl
_test()
