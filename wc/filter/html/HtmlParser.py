# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2005  Bastian Kleineidam
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

import wc.log
import wc.filter
import wc.filter.html
import wc.HtmlParser.htmlsax


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

    def __str__ (self):
        """
        String representation of parser with state info.
        """
        return "%s in state %s" % (self.__class__.__name__, str(self.state))

    def debugbuf (self, cat=wc.LOG_HTML):
        """
        Print debugging information about buffered data.
        """
        wc.log.debug(cat, "self.outbuf %r", self.outbuf.getvalue())
        wc.log.debug(cat, "self.tagbuf %r", self.tagbuf)
        wc.log.debug(cat, "self.waitbuf %r", self.waitbuf)
        wc.log.debug(cat, "self.inbuf %r", self.inbuf.getvalue())

    def tagbuf2data (self):
        """
        Append serialized tag items of the tag buffer to the output buffer
        and clear the tag buffer.
        """
        wc.log.debug(wc.LOG_HTML, "%s tagbuf2data", self)
        wc.filter.html.tagbuf2data(self.tagbuf, self.outbuf)
        self.tagbuf = []

    def feed (self, data):
        """
        Feed some data to the parser.
        """
        wc.log.debug(wc.LOG_HTML, "%s feed %r", self, data)
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
                wc.log.debug(wc.LOG_HTML, "%s parser feed %r", self, data)
                super(HtmlParser, self).feed(data)
            else:
                wc.log.debug(wc.LOG_HTML, "%s empty parser feed", self)
                pass
        elif self.state[0] == 'wait':
            # wait state ==> put in input buffer
            wc.log.debug(wc.LOG_HTML, "%s waits", self)
            self.inbuf.write(data)
        else:
            assert False, "parser %s has unknown parser state" % str(self)

    def flush (self):
        """
        Flush pending data.
        """
        wc.log.debug(wc.LOG_HTML, "%s flush", self)
        if self.state[0] == 'wait':
            # flushing in wait state raises a filter exception
            self.waited += 1
            raise wc.filter.FilterWait, "waited %d at parser %s" % \
                                        (self.waited, str(self))
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
        wc.log.debug(wc.LOG_HTML, "%s replays %r", self, waitbuf)
        for item in waitbuf:
            if self.state[0] == 'wait':
                # the replaying itself can switch to wait state
                self.waitbuf.append(item)
            elif item[0] == wc.filter.html.DATA and \
                 hasattr(self.handler, "characters"):
                self.handler.characters(item[1])
            elif item[0] == wc.filter.html.STARTTAG and \
                 hasattr(self.handler, "start_element"):
                self.handler.start_element(item[1], item[2])
            elif item[0] == wc.filter.html.STARTENDTAG and \
                 hasattr(self.handler, "start_end_element"):
                self.handler.start_end_element(item[1], item[2])
            elif item[0] == wc.filter.html.ENDTAG and \
                 hasattr(self.handler, "end_element"):
                self.handler.end_element(item[1])
            elif item[0] == wc.filter.html.COMMENT and \
                 hasattr(self.handler, "comment"):
                self.handler.comment(item[1])
