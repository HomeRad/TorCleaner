# -*- coding: iso-8859-1 -*-
from wc.filter.Rating import *

# rating_split_url
for url in ['', 'a', 'a/b',
            'http://imadoofus.com',
            'http://imadoofus.com//',
            'http://imadoofus.com/?q=a',
            'http://imadoofus.com/?q=a#a',
            'http://imadoofus.com/a/b//c',
            'http://imadoofus.com/forum',
            'http://imadoofus.com/forum/',
           ]:
    print rating_split_url(url)
print rating_cache_get('http://www.heise.de/foren/')

# rating_in_range (prange, value)
print "true", rating_in_range((None, None), (1, 1))
print "true", rating_in_range((1, 1), (None, None))
print "true", rating_in_range((None, 1), (1, None))
print "true", rating_in_range((1, None), (None, 1))
print "false", rating_in_range((1, 2), (0, 1))
print "false", rating_in_range((1, 2), (1, 3))
print "false", rating_in_range((1, 2), (0, None))
print "false", rating_in_range((1, 2), (None, 3))
print "true", rating_in_range((1, 2), (1, 2))

# rating_range (range)
print "valid", rating_range("-")
print "valid", rating_range("1-")
print "valid", rating_range("-1")
print "valid", rating_range("1-1")
print "invalid", rating_range("")
print "invalid", rating_range("1")
print "invalid", rating_range("-1-")
