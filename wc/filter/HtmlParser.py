# -*- coding: iso-8859-1 -*-
"""Buffered HTML parser"""
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

from cStringIO import StringIO
from wc.parser import htmlsax
from wc.filter import FilterWait
from wc.filter.rules.RewriteRule import STARTTAG, ENDTAG, DATA, COMMENT, tagbuf2data
from wc.log import *


class HtmlParser (htmlsax.parser):
    """HTML parser with ability to buffer incoming and outgoing data.
       States:
       parse - default parsing state, no background fetching
       wait  - this parser (or a recursive one used by javascript)
               is fetching additionally data in the background.
               Flushing data in wait state raises a FilterWait
               When finished for <script src="">, the buffers look like this:

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


    def _debugbuf (self):
        """print debugging information about data buffer status"""
        self._debug("self.outbuf %r", self.outbuf.getvalue())
        self._debug("self.tagbuf %r", self.tagbuf)
        self._debug("self.waitbuf %r", self.waitbuf)
        self._debug("self.inbuf %r", self.inbuf.getvalue())


    def tagbuf2data (self):
        """Append all tags of the tag buffer to the output buffer"""
        tagbuf2data(self.tagbuf, self.outbuf)
        self.tagbuf = []


    def feed (self, data):
        """feed some data to the parser"""
        if self.state[0]=='parse':
            # look if we must replay something
            if self.waited > 0:
                self.waited = 0
                waitbuf, self.waitbuf = self.waitbuf, []
                self.replay(waitbuf)
                if self.state[0]!='parse':
                    self.inbuf.write(data)
                    return
                data = self.inbuf.getvalue() + data
                self.inbuf.close()
                self.inbuf = StringIO()
            if data:
                # only feed non-empty data
                debug(FILTER, "parser feed %r", data)
                super(HtmlParser, self).feed(data)
            else:
                debug(FILTER, "empty parser feed")
                pass
        else:
            # wait state ==> put in input buffer
            debug(FILTER, "parser wait")
            self.inbuf.write(data)


    def flush (self, finish=False):
        """flush pending data and return the flushed output buffer"""
        debug(FILTER, "parser flush")
        if self.waited > 100:
            error(FILTER, "waited too long for %s"%self.state[1])
            # tell recursive background downloaders to stop
            if hasattr(self.handler, "finish"):
                self.handler.finish()
            # switch back to parse
            self.state = ('parse',)
            # feeding an empty string will replay() buffered data
            self.feed("")
        elif self.state[0]=='wait':
            # flushing in wait state raises a filter exception
            self.waited += 1
            raise FilterWait("HtmlParser[wait]: waited %d times for %s"%\
                             (self.waited, self.state[1]))
        super(HtmlParser, self).flush()
        if finish:
            self.tagbuf2data()
        data = self.outbuf.getvalue()
        self.outbuf.close()
        self.outbuf = StringIO()
        return data


    def replay (self, waitbuf):
        """call the handler functions again with buffer data"""
        debug(FILTER, "parser replay %r", waitbuf)
        for item in waitbuf:
            if item[0]==DATA and hasattr(self.handler, "characters"):
                self.handler.characters(item[1])
            elif item[0]==STARTTAG and hasattr(self.handler, "startElement"):
                self.handler.startElement(item[1], item[2])
            elif item[0]==ENDTAG and hasattr(self.handler, "endElement"):
                self.handler.endElement(item[1])
            elif item[0]==COMMENT and hasattr(self.handler, "comment"):
                self.handler.comment(item[1])

