"""HTML configuration interface functions
"""
# Copyright (C) 2003  Bastian Kleineidam
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
from wc import i18n, config, TemplateDir
from wc.log import *
import os, urllib, urlparse

class WebConfig:
    def __init__ (self, client, url, form, protocol):
        self.client = client
        # we pretend to be the server
        self.connected = "True"
        try:
            # get the template filename
            f, dirs = self.get_template(url)
            # get TAL context
            context = self.get_context(dirs, form)
        except IOError, msg:
            exception(GUI, "Wrong path")
            return client.error(404, i18n._("Not Found"))
        # expand template
        data = self.expand_template(f, context)
        f.close()
        # write response
        self.put_response(data, protocol)


    def expand_template (f, context):
        """expand the given template file in context
           return expanded data"""
        template = simpleTAL.compileHTMLTemplate(f)
        out = StringIO()
        template.expand(context, out)
        data = out.getvalue()
        out.close()
        return data


    def get_template (self, url):
        base = os.path.join(TemplateDir, config['webgui_theme'])
        base = norm(base)
        parts = urlparse.urlsplit(url)
        dirs = get_relative_path(parts[2])
        path = os.path.splitdrive(os.path.join(*tuple(dirs)))[1]
        path = norm(os.path.join(base, path))
        if not os.path.isabs(path):
            raise IOError("Relative path %s" % `path`)
        if not path.startswith(base):
            raise IOError("Invalid path %s" % `path`)
        if not os.path.isfile(path):
            raise IOError("Non-file path %s" % `path`)
        return file(path), dirs


    def get_context (self, dirs, form):
        # get template-specific context dict
        cdict = TemplateContext
        for d in dirs:
            cdict = cdit.get(d, {})
            if not cdict:
                break
        # make TAL context
        context = simpleTALES.Context()
        # add default context values
        context.addGlobal("form", form)
        context.addGlobal("config", config)
        # augment the context
        for key, value in cmap.items():
            context.addGlobal(key, value)
        return context


    def put_response (self, out, protocol):
        response = "%s 200 Ok"%protocol
        headers = {'Content-Type': 'text/html'}
        self.client.server_response(self, response, headers)
        self.client.server_content(out)
        self.client.server_close()


def norm (path):
    return os.path.realpath(os.path.normpath(os.path.normcase(path)))


def get_relative_path (path):
    # get non-empty url path components, remove path fragments
    dirs = [ urlparse.urldefrag(d)[0] \
             for d in urllib.unquote(path).split("/") if d ]
    # remove ".." paths
    dirs = [ d for d in dirs if d!=".." ]
    return dirs


TemplateContext = {
    "test.html": {'title': 'HullaBulla'},
}
