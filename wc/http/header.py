# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam

from cStringIO import StringIO
import rfc822


class WcMessage(rfc822.Message, object):
    """
    Represents a single RFC 2822-compliant message, adding functions
    handling multiple headers with the same name.
    """

    def __init__(self, fp=None, seekable=True):
        """
        Initialize message reading from given optional file descriptor.
        """
        if fp is None:
            fp = StringIO()
        super(WcMessage, self).__init__(fp, seekable=seekable)

    def remove_multiple_headers(self, name):
        """
        Remove all occurrences of given header name except the first.
        """
        values = self.getheaders(name)
        if len(values) > 1:
            self[name] = values[0]
            return True
        return False

    def addheader(self, name, value):
        """
        Add given header name and value to the end of the header list.
        Multiple headers with the same name are supported.
        """
        text = name + ": " + value
        lines = text.split('\n')
        for line in lines:
            self.headers.append(line + "\n")
        self.dict[name.lower()] = value

    def __str__(self):
        """
        HTTP conform string representation.
        """
        return "\n".join([ repr(s) for s in self.headers ])

    def copy(self):
        """
        Copy these headers into a new WcHeaders object.
        """
        return WcMessage(fp=StringIO("".join(self.headers)))

    def iterkeys(self):
        """Get all of a message's header field names."""
        return self.dict.iterkeys()

    def itervalues(self):
        """Get all of a message's header field values."""
        return self.dict.itervalues()

    def iteritems(self):
        """Get all of a message's header (name, value) items."""
        return self.dict.iteritems()
