# -*- coding: iso-8859-1 -*-
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from simpletal import simpleTAL, simpleTALES
from cStringIO import StringIO
from wc import i18n, config, TemplateDir, filtermodules
from wc.log import *
import os, urllib, urlparse

class WebConfig (object):
    def __init__ (self, client, url, form, protocol,
                  status=200, msg=i18n._('Ok'), context={},
                  headers={'Content-Type': 'text/html'}):
        self.client = client
        # we pretend to be the server
        self.connected = True
        try:
            # get the template filename
            path, dirs = get_template_url(url)
            if headers['Content-Type'] == 'text/html':
                f = file(path)
                # get TAL context
                context = get_context(dirs, form, context)
                # expand template
                data = expand_template(f, context)
            else:
                f = file(path, 'rb')
                data = f.read()
        except IOError, e:
            exception(GUI, "Wrong path `%s'", url)
            # XXX this can actually lead to a maximum recursion
            # error when client.error caused the exception
            return client.error(404, i18n._("Not Found"))
        except:
            # catch all other exceptions and report internal error
            exception(GUI, "Template error")
            return client.error(500, i18n._("Internal Error"))
        f.close()
        # write response
        self.put_response(data, protocol, status, msg, headers)


    def put_response (self, out, protocol, status, msg, headers):
        response = "%s %d %s"%(protocol, status, msg)
        self.client.server_response(self, response, headers)
        self.client.server_content(out)
        self.client.server_close()


    def client_abort (self):
        self.client = None


def norm (path):
    return os.path.realpath(os.path.normpath(os.path.normcase(path)))


def expand_template (f, context):
    """expand the given template file in context
       return expanded data"""
    template = simpleTAL.compileHTMLTemplate(f)
    out = StringIO()
    template.expand(context, out)
    data = out.getvalue()
    out.close()
    return data


def get_relative_path (path):
    # get non-empty url path components, remove path fragments
    dirs = [ urlparse.urldefrag(d)[0] \
             for d in urllib.unquote(path).split("/") if d ]
    # remove ".." paths
    dirs = [ d for d in dirs if d!=".." ]
    return dirs


def get_template_url (url):
    """return tuple (path, dirs)"""
    parts = urlparse.urlsplit(url)
    return get_template_path(parts[2])


def get_template_path (path):
    """return tuple (path, dirs)"""
    base = os.path.join(TemplateDir, config['gui_theme'])
    base = norm(base)
    dirs = get_relative_path(path)
    if not dirs:
        # default template
        dirs = ['index.html']
    path = os.path.splitdrive(os.path.join(*tuple(dirs)))[1]
    path = norm(os.path.join(base, path))
    if not os.path.isabs(path):
        raise IOError("Relative path %s" % `path`)
    if not path.startswith(base):
        raise IOError("Invalid path %s" % `path`)
    if not os.path.isfile(path):
        raise IOError("Non-file path %s" % `path`)
    return path, dirs


def get_context (dirs, form, localcontext):
    """get template context, raise ImportError if not found"""
    # get template-specific context dict
    modulepath = ".".join(['context'] + dirs[:-1])
    template = dirs[-1].replace(".", "_")
    # this can raise an import error
    exec "from %s import %s as template_context" % (modulepath, template)
    if hasattr(template_context, "exec_form") and form is not None:
        # handle form action
        template_context.exec_form(form)
    # make TAL context
    context = simpleTALES.Context()
    # add default context values
    context.addGlobal("form", form)
    path, dirs = get_template_path("macros/rules.html")
    f = file(path, 'r')
    rulemacros = simpleTAL.compileHTMLTemplate(f)
    f.close()
    context.addGlobal("rulemacros", rulemacros)
    # augment the context
    attrs = [ x for x in dir(template_context) if not x.startswith('_') ]
    for attr in attrs:
        context.addGlobal(attr, getattr(template_context, attr))
    # add local context
    for key, value in localcontext.items():
        context.addGlobal(key, value)
    return context
