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

import os
import re
import urllib
import urlparse
import gettext
import mimetypes
import cStringIO as StringIO

import wc
import wc.configuration
import wc.i18n
import wc.log
import wc.proxy.auth
import wc.proxy.Headers


class WebConfig (object):
    """class for web configuration templates"""

    def __init__ (self, client, url, form, protocol, clientheaders,
                 status=200, msg=_('Ok'), localcontext=None, auth=''):
        """load a web configuration template and return response"""
        wc.log.debug(wc.LOG_GUI, "WebConfig %s %s", url, form)
        self.client = client
        # we pretend to be the server
        self.connected = True
        headers = wc.proxy.Headers.WcMessage()
        headers['Server'] = 'Proxy\r'
        if auth:
            if status == 407:
                headers['Proxy-Authenticate'] = "%s\r" % auth
            elif status == 401:
                headers['WWW-Authenticate'] = "%s\r" % auth
            else:
                wc.log.error(wc.LOG_GUI,
                             "Authentication with wrong status %d", status)
        if status in [301, 302]:
            headers['Location'] = clientheaders['Location']
        gm = mimetypes.guess_type(url, None)
        if gm[0] is not None:
            ctype = gm[0]
        else:
            # note: index.html is appended to directories
            ctype = 'text/html'
        if ctype == 'text/html':
            ctype += "; charset=iso-8859-1"
        headers['Content-Type'] = "%s\r" % ctype
        try:
            lang = wc.i18n.get_headers_lang(clientheaders)
            # get the template filename
            path, dirs, lang = get_template_url(url, lang)
            if path.endswith('.html'):
                # get TAL context
                context, newstatus = \
                     get_context(dirs, form, localcontext, lang)
                if newstatus == 401 and status != newstatus:
                    client.error(401, _("Authentication Required"),
                                 auth=wc.proxy.auth.get_challenges())
                    return
                # get (compiled) template
                template = wc.webgui.TemplateCache.templates[path]
                # expand template
                data = expand_template(template, context)
            else:
                fp = file(path, 'rb')
                data = fp.read()
                fp.close()
        except IOError:
            wc.log.exception(wc.LOG_GUI, "Wrong path %r:", url)
            # XXX this can actually lead to a maximum recursion
            # error when client.error caused the exception
            client.error(404, _("Not Found"))
            return
        except StandardError:
            # catch standard exceptions and report internal error
            wc.log.exception(wc.LOG_GUI, "Template error:")
            client.error(500, _("Internal Error"))
            return
        # not catched builtin exceptions are:
        # SystemExit, StopIteration and all warnings

        # finally write response to client
        self.put_response(data, protocol, status, msg, headers)

    def put_response (self, data, protocol, status, msg, headers):
        """write response to client"""
        response = "%s %d %s" % (protocol, status, msg)
        self.client.server_response(self, response, status, headers)
        self.client.server_content(data)
        self.client.server_close(self)

    def client_abort (self):
        """client has aborted the connection"""
        self.client = None


def norm (path):
    """normalize a path name"""
    return os.path.realpath(os.path.normpath(os.path.normcase(path)))


def expand_template (template, context):
    """expand the given template file fp in context
       return expanded data
    """
    return template(**context)
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
    base = os.path.join(wc.TemplateDir, wc.configuration.config['gui_theme'])
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
        assert len(la) == 2
        if path.endswith(".html.%s" % la):
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
    context = {}
    if hasattr(template_context, "_exec_form") and form is not None:
        # handle form action
        wc.log.debug(wc.LOG_GUI, "got form %s", form)
        status = template_context._exec_form(form, lang)
        # add form vars to context
        context_add(context, "form", form)
    # add default context values
    add_default_context(context, dirs[-1], lang)
    # augment the context
    attrs = [ x for x in dir(template_context) if not x.startswith('_') ]
    for attr in attrs:
        context_add(context, attr, getattr(template_context, attr))
    # add local context
    if localcontext is not None:
        for key, value in localcontext.items():
            context_add(context, key, value)
    return context, status


def add_default_context (context, filename, lang):
    """add context variables used by all templates"""
    # rule macros
    path, dirs = _get_template_path("macros/rules.html")
    rulemacros = wc.webgui.TemplateCache.templates[path]
    context_add(context, "rulemacros", rulemacros.macros)
    # standard macros
    path, dirs = _get_template_path("macros/standard.html")
    macros = wc.webgui.TemplateCache.templates[path]
    context_add(context, "macros", macros.macros)
    # used by navigation macro
    context_add(context, "nav", {filename.replace('.', '_'): True})
    # page template name
    context_add(context, "filename", filename)
    # base url
    context_add(context, "baseurl",
                "http://localhost:%d/" % wc.configuration.config['port'])
    # language
    context_add(context, "lang", lang)
    # other available languges
    otherlanguages = []
    for la in wc.i18n.supported_languages:
        if lang == la:
            continue
        otherlanguages.append({'code': la,
                               'name': wc.i18n.lang_name(la),
                               'trans': wc.i18n.lang_trans(la, lang),
                              })
    context_add(context, "otherlanguages", otherlanguages)


def context_add (context, key, val):
    context[unicode(key)] = unicode(val)
