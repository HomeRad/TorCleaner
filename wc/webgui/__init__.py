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

from wc.webgui.simpletal import simpleTAL, simpleTALES
from wc.webgui.context import getval
from cStringIO import StringIO
from wc import i18n, config, TemplateDir, App, filtermodules, Name, LocaleDir
from wc.log import *
import os, re, urllib, urlparse, gettext, mimetypes

class WebConfig (object):
    def __init__ (self, client, url, form, protocol, clientheaders,
                  status=200, msg=i18n._('Ok'), context={}, auth=''):
        self.client = client
        # we pretend to be the server
        self.connected = True
        headers = {'Server': 'Proxy'}
        if auth:
            headers['Proxy-Authenticate'] = "%s\r"%auth
        gm = mimetypes.guess_type(url, None)
        if gm[0] is not None:
            headers['Content-Type'] = "%s\r"%gm[0]
        else:
            # note: index.html is appended to directories
            headers['Content-Type'] = 'text/html\r'
        try:
            lang = i18n.get_headers_lang(clientheaders)
            # get the template filename
            path, dirs, lang = get_template_url(url, lang)
            if path.endswith('.html'):
                f = file(path)
                # get TAL context
                context = get_context(dirs, form, context, lang)
                # get translator
                translator = gettext.translation(Name, LocaleDir, [lang], fallback=True)
                debug(GUI, "Using translator %s", str(translator.info()))
                # expand template
                data = expand_template(f, context, translator=translator)
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


    def put_response (self, data, protocol, status, msg, headers):
        response = "%s %d %s"%(protocol, status, msg)
        self.client.server_response(self, response, headers)
        self.client.server_content(data)
        self.client.server_close()


    def client_abort (self):
        self.client = None


def norm (path):
    """normalize a path name"""
    return os.path.realpath(os.path.normpath(os.path.normcase(path)))


def expand_template (f, context, translator=None):
    """expand the given template file in context
       return expanded data"""
    # note: standard input encoding is iso-8859-1 for html templates
    template = simpleTAL.compileHTMLTemplate(f)
    out = StringIO()
    template.expand(context, out, translator=translator)
    data = out.getvalue()
    out.close()
    return data


safe_path = re.compile(r"[-a-zA-Z0-9_.]+").match
def is_safe_path (path):
    return safe_path(path) and ".." not in path


def get_relative_path (path):
    """return splitted and security filtered path"""
    # get non-empty url path components, remove path fragments
    dirs = [ urlparse.urldefrag(d)[0] for d in path.split("/") if d ]
    # remove ".." and other invalid paths (security!)
    dirs = [ d for d in dirs if is_safe_path(d) ]
    return dirs


def get_template_url (url, lang):
    """return tuple (path, dirs, lang)"""
    parts = urlparse.urlsplit(url)
    return get_template_path(urllib.unquote(parts[2]), lang)


def get_template_path (path, lang):
    """return tuple (path, dirs, lang)"""
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
    for la in i18n.supported_languages:
        assert len(la)==2
        if path.endswith(".html.%s"%la):
            path = path[:-3]
            dirs[-1] = dirs[-1][:-3]
            lang = la
            break
    if not os.path.isfile(path):
        raise IOError("Non-file path %s" % `path`)
    return path, dirs, lang


def get_context (dirs, form, localcontext, lang):
    """Get template context, raise ImportError if not found.
       The context includes the given local context, plus all variables
       defined by the imported context module"""
    # get template-specific context dict
    modulepath = ".".join(['context'] + dirs[:-1])
    template = dirs[-1].replace(".", "_")
    # this can raise an import error
    exec "from %s import %s as template_context" % (modulepath, template)
    if hasattr(template_context, "_exec_form") and form is not None:
        # handle form action
        debug(GUI, "got form %s", str(form))
        template_context._exec_form(form)
    # make TAL context
    context = simpleTALES.Context()
    # add default context values
    add_default_context(context, form, dirs[-1], lang)
    # augment the context
    attrs = [ x for x in dir(template_context) if not x.startswith('_') ]
    for attr in attrs:
        context.addGlobal(attr, getattr(template_context, attr))
    # add local context
    for key, value in localcontext.items():
        context.addGlobal(key, value)
    return context


def add_default_context (context, form, filename, lang):
    # form values
    context.addGlobal("form", form)
    # rule macros
    path, dirs, lang = get_template_path("macros/rules.html", lang)
    f = file(path, 'r')
    rulemacros = simpleTAL.compileHTMLTemplate(f)
    f.close()
    context.addGlobal("rulemacros", rulemacros)
    # standard macros
    path, dirs, lang = get_template_path("macros/standard.html", lang)
    f = file(path, 'r')
    macros = simpleTAL.compileHTMLTemplate(f)
    f.close()
    context.addGlobal("macros", macros)
    # used by navigation macro
    context.addGlobal("nav", {filename.replace('.', '_'): True})
    # page template name
    context.addGlobal("filename", filename)
    # language
    context.addGlobal("lang", lang)
    # other available languges
    otherlanguages = []
    for la in i18n.supported_languages:
        if lang==la: continue
        otherlanguages.append({'code': la,
                               'name': i18n.lang_name(la),
                               'trans': i18n.lang_trans(la, lang),
                              })
    context.addGlobal("otherlanguages", otherlanguages)
