# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2008 Bastian Kleineidam
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
"""
Buffered HTML parser.
"""

from StringIO import StringIO
import codecs
from . import tagbuf2data, DATA, STARTTAG, ENDTAG, STARTENDTAG, COMMENT
from .. import FilterWait
from ... import log, LOG_HTML
import wc.HtmlParser.htmlsax

BOMS = [
    codecs.BOM_UTF8,
    codecs.BOM_UTF16,
    codecs.BOM_UTF16_BE,
    codecs.BOM_UTF16_LE,
    codecs.BOM_UTF32,
    codecs.BOM_UTF32_BE,
    codecs.BOM_UTF32_LE,
]


class HtmlParser (wc.HtmlParser.htmlsax.parser):
    """
    HTML parser with ability to buffer incoming and outgoing data.

    States:
      - parse: default parsing state, no background fetching
      - wait: this parser (or a recursive one used by javascript)
        is fetching additionally data in the background.
        Flushing data in wait state raises a FilterWait
        When finished for <script src="">, the buffers look like this::

         fed data chunks (example):
               [------------------][-------][----------][--...
         outbuf: [--]
         tagbuf:     [-----]
         waitbuf:           [-------]
         inbuf:                      [-------------- ...
                            ^-- <script src> tag

        When finished with script data, the buffers look like
        XXX (to be done)

        After a wait state, replays the waitbuf and re-feed the inbuf data.
    """

    def __init__ (self, handler):
        """
        Initialize parser state and handler data.
        """
        # internal html parser, calls handler functions
        super(HtmlParser, self).__init__(handler)
        # parse state either normal parse or wait
        self.state = ('parse',)
        # already filtered HTML data
        self.outbuf = StringIO()
        # incoming data in wait state
        self.inbuf = StringIO()
        # buffer of parsed HTML tags
        self.tagbuf = []
        # buffer for wait state of parsed HTML tags
        self.waitbuf = []
        # wait indicator flag
        self.waited = 0
        # initial data feed to check for unicode BOM
        # XXX remove when parser supports unicode
        self.initial = True
        self.bom = None

    def __str__ (self):
        """
        String representation of parser with state info.
        """
        return "%s in state %s" % (self.__class__.__name__, str(self.state))

    def debugbuf (self, cat=LOG_HTML):
        """
        Print debugging information about buffered data.
        """
        log.debug(cat, "self.outbuf %r", self.outbuf.getvalue())
        log.debug(cat, "self.tagbuf %r", self.tagbuf)
        log.debug(cat, "self.waitbuf %r", self.waitbuf)
        log.debug(cat, "self.inbuf %r", self.inbuf.getvalue())

    def tagbuf2data (self):
        """
        Append serialized tag items of the tag buffer to the output buffer
        and clear the tag buffer.
        """
        log.debug(LOG_HTML, "%s tagbuf2data", self)
        tagbuf2data(self.tagbuf, self.outbuf)
        self.tagbuf = []

    def feed (self, data):
        """
        Feed some data to the parser.
        """
        log.debug(LOG_HTML, "%s feed %r", self, data)
        if self.initial:
            self.initial = False
            for bom in BOMS:
                if data.startswith(bom):
                    # remove unicode marker
                    self.bom = bom
                    data = data[len(bom):]
                    break
        if self.state[0] == 'parse':
            # look if we must replay something
            if self.waited > 0:
                self.waited = 0
                if self.waitbuf:
                    waitbuf, self.waitbuf = self.waitbuf, []
                    self.replay(waitbuf)
                if self.state[0] == 'wait':
                    self.inbuf.write(data)
                    return
                data = self.inbuf.getvalue() + data
                self.inbuf.close()
                self.inbuf = StringIO()
            if data:
                # only feed non-empty data
                super(HtmlParser, self).feed(data)
        elif self.state[0] == 'wait':
            # wait state ==> put in input buffer
            log.debug(LOG_HTML, "%s waits", self)
            self.inbuf.write(data)
        else:
            assert False, "parser %s has unknown parser state" % str(self)

    def flush (self):
        """
        Flush pending data.
        """
        log.debug(LOG_HTML, "%s flush", self)
        if self.state[0] == 'wait':
            # flushing in wait state raises a filter exception
            self.waited += 1
            raise FilterWait("waited %d at parser %s" %
                (self.waited, str(self)))
        super(HtmlParser, self).flush()

    def getoutput (self):
        """
        Returns all data in output buffer and clears the output buffer.
        """
        data = self.outbuf.getvalue()
        self.outbuf.close()
        self.outbuf = StringIO()
        return data.encode(self.encoding, "ignore")

    def replay (self, waitbuf):
        """
        Call the handler functions again with buffer data.
        """
        log.debug(LOG_HTML, "%s replays %r", self, waitbuf)
        for item in waitbuf:
            if self.state[0] == 'wait':
                # the replaying itself can switch to wait state
                self.waitbuf.append(item)
            else:
                i = item[0]
                if i == DATA:
                    self.handler.characters(item[1])
                elif i == STARTTAG:
                    self.handler.start_element(item[1], item[2])
                elif i == ENDTAG:
                    self.handler.end_element(item[1])
                elif i == STARTENDTAG:
                    self.handler.start_end_element(item[1], item[2])
                elif i == COMMENT:
                    self.handler.comment(item[1])
