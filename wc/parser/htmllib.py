# -*- coding: iso-8859-1 -*-
"""A parser for HTML"""
# Copyright (C) 2000-2004  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import sys
try:
    import htmlsax
except ImportError, msg:
    exctype, value = sys.exc_info()[:2]
    print >>sys.stderr, "Could not import the parser module `htmlsax':", value
    print >>sys.stderr, "Please check your installation of WebCleaner."
    sys.exit(1)


class SortedDict (dict):
    def __init__ (self):
        # sorted list of keys
        self._keys = []


    def __setitem__ (self, key, value):
        self._keys.append(key)
        super(SortedDict, self).__setitem__(key, value)


    def values (self):
        return [self[k] for k in self._keys]


    def items (self):
        return [(k, self[k]) for k in self._keys]


    def keys (self):
        return self._keys[:]


    def itervalues (self):
        return iter(self.values())


    def iteritems (self):
        return iter(self.items())


    def iterkeys (self):
        return iter(self.keys())


class HtmlPrinter (object):
    """handles all functions by printing the function name and attributes"""
    def __init__ (self, fd=sys.stdout):
        self.fd = fd


    def _print (self, *attrs):
        print >> self.fd, self.mem, attrs


    def _errorfun (self, msg, name):
        """print msg to stderr with name prefix"""
        print >> sys.stderr, name, msg


    def error (self, msg):
        """signal a filter/parser error"""
        self._errorfun(msg, "error:")


    def warning (self, msg):
        """signal a filter/parser warning"""
        self._errorfun(msg, "warning:")


    def fatalError (self, msg):
        """signal a fatal filter/parser error"""
        self._errorfun(msg, "fatal error:")


    def __getattr__ (self, name):
        """remember the func name"""
        self.mem = name
        return self._print


class HtmlPrettyPrinter (object):
    def __init__ (self, fd=sys.stdout):
        self.fd = fd


    def comment (self, data):
        self.fd.write("<!--%s-->" % data)


    def startElement (self, tag, attrs):
        self.fd.write("<%s"%tag.replace("/", ""))
        for key, val in attrs.iteritems():
            if val is None:
                self.fd.write(" %s"%key)
            else:
                self.fd.write(" %s=\"%s\"" % (key, quote_attrval(val)))
        self.fd.write(">")


    def endElement (self, tag):
        self.fd.write("</%s>" % tag)


    def doctype (self, data):
        self.fd.write("<!DOCTYPE%s>" % data)


    def pi (self, data):
        self.fd.write("<?%s?>" % data)


    def cdata (self, data):
        self.fd.write("<![CDATA[%s]]>"%data)


    def characters (self, data):
        self.fd.write(data)


def quote_attrval (val):
    """quote a HTML attribute to be able to wrap it in double quotes"""
    return val.replace('"', '&quot;')

