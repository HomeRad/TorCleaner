# -*- coding: iso-8859-1 -*-
"""HTML configuration interface functions"""
# Copyright (C) 2003-2004  Bastian Kleineidam
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

import os
import re
import urllib
import urlparse
import gettext
import mimetypes
import cStringIO as StringIO
import wc
import wc.webgui.simpletal.simpleTAL
import wc.webgui.simpletal.simpleTALES
import wc.proxy.auth
import wc.proxy.Headers
from wc.log import *


class WebConfig (object):
    """class for web configuration templates"""

    def __init__ (self, client, url, form, protocol, clientheaders,
                  status=200, msg=wc.i18n._('Ok'), localcontext=None, auth=''):
        """load a web configuration template and return response"""
        debug(GUI, "WebConfig %s %s", url, form)
        self.client = client
        # we pretend to be the server
        self.connected = True
        headers = wc.proxy.Headers.WcMessage()
        headers['Server'] = 'Proxy\r'
        if auth:
            if status==407:
                headers['Proxy-Authenticate'] = "%s\r"%auth
            elif status==401:
                headers['WWW-Authenticate'] = "%s\r"%auth
            else:
                error(GUI, "Authentication with wrong status %d", status)
        if status in [301,302]:
            headers['Location'] = clientheaders['Location']
        gm = mimetypes.guess_type(url, None)
        if gm[0] is not None:
            headers['Content-Type'] = "%s\r"%gm[0]
        else:
            # note: index.html is appended to directories
            headers['Content-Type'] = 'text/html\r'
        try:
            lang = wc.i18n.get_headers_lang(clientheaders)
            # get the template filename
            path, dirs, lang = get_template_url(url, lang)
            if path.endswith('.html'):
                fp = file(path)
                # get TAL context
                context, newstatus = get_context(dirs, form, localcontext, lang)
                if newstatus==401 and status!=newstatus:
                    client.error(401, wc.i18n._("Authentication Required"),
                                 auth=wc.proxy.auth.get_challenges())
                    return
                # get translator
                translator = gettext.translation(wc.Name, wc.LocaleDir, [lang], fallback=True)
                #debug(GUI, "Using translator %s", translator.info())
                # expand template
                data = expand_template(fp, context, translator=translator)
            else:
                fp = file(path, 'rb')
                data = fp.read()
            fp.close()
        except IOError:
            exception(GUI, "Wrong path %r", url)
            # XXX this can actually lead to a maximum recursion
            # error when client.error caused the exception
            client.error(404, wc.i18n._("Not Found"))
            return
        except StandardError:
            # catch standard exceptions and report internal error
            exception(GUI, "Template error")
            client.error(500, wc.i18n._("Internal Error"))
            return
        # not catched builtin exceptions are:
        # SystemExit, StopIteration and all warnings

        # write response
        self.put_response(data, protocol, status, msg, headers)


    def put_response (self, data, protocol, status, msg, headers):
        """write response to client"""
        response = "%s %d %s"%(protocol, status, msg)
        self.client.server_response(self, response, status, headers)
        self.client.server_content(data)
        self.client.server_close(self)


    def client_abort (self):
        """client has aborted the connection"""
        self.client = None


def norm (path):
    """normalize a path name"""
    return os.path.realpath(os.path.normpath(os.path.normcase(path)))


def expand_template (fp, context, translator=None):
    """expand the given template file fp in context
       return expanded data"""
    # note: standard input encoding is iso-8859-1 for html templates
    template = wc.webgui.simpletal.simpleTAL.compileHTMLTemplate(fp)
    out = StringIO.StringIO()
    template.expand(context, out, translator=translator)
    return out.getvalue()


safe_path = re.compile(r"[-a-zA-Z0-9_.]+").match
def is_safe_path (path):
    """return True iff path is safe for opening"""
    return safe_path(path) and ".." not in path


def get_relative_path (path):
    """return splitted and security filtered path"""
    # get non-empty url path components, remove path fragments
    dirs = [ urlparse.urldefrag(d)[0] for d in path.split("/") if d ]
    # remove ".." and other invalid paths (security!)
    return [ d for d in dirs if is_safe_path(d) ]


def get_template_url (url, lang):
    """return tuple (path, dirs, lang)"""
    parts = urlparse.urlsplit(url)
    return get_template_path(urllib.unquote(parts[2]), lang)


def _get_template_path (path):
    """return tuple (path, dirs)"""
    base = os.path.join(wc.TemplateDir, wc.config['gui_theme'])
    base = norm(base)
    dirs = get_relative_path(path)
    if not dirs:
        # default template
        dirs = ['index.html']
    path = os.path.splitdrive(os.path.join(*tuple(dirs)))[1]
    path = norm(os.path.join(base, path))
    if not os.path.isabs(path):
        raise IOError("Relative path %r" % path)
    if not path.startswith(base):
        raise IOError("Invalid path %r" % path)
    return path, dirs


def get_template_path (path, defaultlang):
    """return tuple (path, dirs, lang)"""
    path, dirs = _get_template_path(path)
    lang = defaultlang
    for la in wc.i18n.supported_languages:
        assert len(la)==2
        if path.endswith(".html.%s"%la):
            path = path[:-3]
            dirs[-1] = dirs[-1][:-3]
            lang = la
            break
    if not os.path.isfile(path):
        raise IOError("Non-file path %r" % path)
    return path, dirs, lang


def get_context (dirs, form, localcontext, lang):
    """Get template context, raise ImportError if not found.
       The context includes the given local context, plus all variables
       defined by the imported context module
       Evaluation of the context can set a different HTTP status.
       Returns tuple `(context, status)`"""
    # get template-specific context dict
    status = None
    modulepath = ".".join(['context'] + dirs[:-1])
    template = dirs[-1].replace(".", "_")
    # this can raise an import error
    exec "from %s import %s as template_context" % (modulepath, template)
    # make TAL context
    context = wc.webgui.simpletal.simpleTALES.Context()
    if hasattr(template_context, "_exec_form") and form is not None:
        # handle form action
        debug(GUI, "got form %s", form)
        status = template_context._exec_form(form, lang)
        context.addGlobal("form", form)
    # add default context values
    add_default_context(context, dirs[-1], lang)
    # augment the context
    attrs = [ x for x in dir(template_context) if not x.startswith('_') ]
    for attr in attrs:
        context.addGlobal(attr, getattr(template_context, attr))
    # add local context
    if localcontext is not None:
        for key, value in localcontext.items():
            context.addGlobal(key, value)
    return context, status


def add_default_context (context, filename, lang):
    """add context variables used by all templates"""
    # rule macros
    path, dirs = _get_template_path("macros/rules.html")
    rulemacros = wc.webgui.simpletal.simpleTAL.compileHTMLTemplate(file(path, 'r'))
    context.addGlobal("rulemacros", rulemacros.macros)
    # standard macros
    path, dirs = _get_template_path("macros/standard.html")
    macros = wc.webgui.simpletal.simpleTAL.compileHTMLTemplate(file(path, 'r'))
    context.addGlobal("macros", macros.macros)
    # used by navigation macro
    context.addGlobal("nav", {filename.replace('.', '_'): True})
    # page template name
    context.addGlobal("filename", filename)
    # base url
    context.addGlobal("baseurl", "http://localhost:%d/" % wc.config['port'])
    # language
    context.addGlobal("lang", lang)
    # other available languges
    otherlanguages = []
    for la in wc.i18n.supported_languages:
        if lang==la: continue
        otherlanguages.append({'code': la,
                               'name': wc.i18n.lang_name(la),
                               'trans': wc.i18n.lang_trans(la, lang),
                              })
    context.addGlobal("otherlanguages", otherlanguages)
