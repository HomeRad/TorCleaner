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
        - parse:
         default parsing state, no background fetching
        - wait:
         this parser (or a recursive one used by javascript)
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


    def __str__ (self):
        return "%s in state %s"%(self.__class__.__name__, str(self.state))


    def debugbuf (self):
        """print debugging information about buffered data"""
        debug(FILTER, "self.outbuf %r", self.outbuf.getvalue())
        debug(FILTER, "self.tagbuf %r", self.tagbuf)
        debug(FILTER, "self.waitbuf %r", self.waitbuf)
        debug(FILTER, "self.inbuf %r", self.inbuf.getvalue())


    def tagbuf2data (self):
        """append serialized tag items of the tag buffer to the output buffer
           and clear the tag buffer"""
        debug(FILTER, "%s tagbuf2data", self)
        tagbuf2data(self.tagbuf, self.outbuf)
        self.tagbuf = []


    def feed (self, data):
        """feed some data to the parser"""
        debug(FILTER, "%s feed %r", self, data)
        if self.state[0]=='parse':
            # look if we must replay something
            if self.waited > 0:
                self.waited = 0
                if self.waitbuf:
                    waitbuf, self.waitbuf = self.waitbuf, []
                    self.replay(waitbuf)
                if self.state[0]=='wait':
                    self.inbuf.write(data)
                    return
                data = self.inbuf.getvalue() + data
                self.inbuf.close()
                self.inbuf = StringIO()
            if data:
                # only feed non-empty data
                debug(FILTER, "%s parser feed %r", self, data)
                super(HtmlParser, self).feed(data)
            else:
                debug(FILTER, "%s empty parser feed", self)
                pass
        elif self.state[0]=='wait':
            # wait state ==> put in input buffer
            debug(FILTER, "%s waits", self)
            self.inbuf.write(data)
        else:
            assert False, "parser %s has unknown parser state"%str(self)


    def flush (self):
        """flush pending data"""
        debug(FILTER, "%s flush", self)
        if self.state[0]=='wait':
            # flushing in wait state raises a filter exception
            self.waited += 1
            raise FilterWait("waited %d at parser %s"%(self.waited, str(self)))
        super(HtmlParser, self).flush()


    def getoutput (self):
        """returns all data in output buffer and clears the output buffer"""
        data = self.outbuf.getvalue()
        self.outbuf.close()
        self.outbuf = StringIO()
        return data


    def replay (self, waitbuf):
        """call the handler functions again with buffer data"""
        debug(FILTER, "%s replays %r", self, waitbuf)
        for item in waitbuf:
            if self.state[0]=='wait':
                # the replaying itself can switch to wait state
                self.waitbuf.append(item)
            elif item[0]==DATA and hasattr(self.handler, "characters"):
                self.handler.characters(item[1])
            elif item[0]==STARTTAG and hasattr(self.handler, "startElement"):
                self.handler.startElement(item[1], item[2])
            elif item[0]==ENDTAG and hasattr(self.handler, "endElement"):
                self.handler.endElement(item[1])
            elif item[0]==COMMENT and hasattr(self.handler, "comment"):
                self.handler.comment(item[1])

