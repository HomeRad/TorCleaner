"""HTML configuration interface functions
"""
# Copyright (C) 2002  Bastian Kleineidam
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

from simpletal import simpleTAL, simpleTALES
from cStringIO import StringIO
from wc import config, TemplateDir
import os

class WebConfig:
    def __init__ (self, client, url, form={}):
        self.client = client
        # we pretend to be the server
        self.connected = "True"
        # make TAL context
        self.context = simpleTALES.Context()
        self.context.addGlobal("form", form)
        self.context.addGlobal("config", config)
        # note: get_template augments the context
        templateFile = file(self.get_template(url))
        # write template
        template = simpleTAL.compileHTMLTemplate(templateFile)
        templateFile.close()
        out = StringIO()
        template.expand(context, out)
        # write response
        self.put_response(out)


    def get_template (self, url):
        d = os.path.join(TemplateDir, config['webgui_theme'])
        # XXX
        return os.path.join(d, "error.html")


    def put_response (self, out):
        response = "HTTP/1.1 200 Ok"
        headers = {'Content-Type': 'text/html'}
        self.client.server_response(self, response, headers)
        self.client.server_content(out)
        self.client.server_close()
