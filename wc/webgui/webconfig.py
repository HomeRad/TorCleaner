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

import gettext
import mimetypes

import wc
import wc.configuration
import wc.i18n
import wc.log
import wc.proxy.auth
import wc.proxy.Headers
import wc.webgui
import wc.webgui.templatecache
import wc.webgui.TAL


class WebConfig (object):
    """class for web configuration templates"""

    def __init__ (self, client, url, form, protocol, clientheaders,
                 status=200, msg=_('Ok'), localcontext=None, auth=''):
        """load a web configuration template and return response"""
        wc.log.debug(wc.LOG_GUI, "WebConfig %s %s", url, form)
        if isinstance(msg, unicode):
            msg = msg.encode("iso8859-1", "ignore")
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
        path = ""
        try:
            lang = wc.i18n.get_headers_lang(clientheaders)
            # get the template filename
            path, dirs, lang = wc.webgui.get_template_url(url, lang)
            if path.endswith('.html'):
                # get TAL context
                context, newstatus = \
                     get_context(dirs, form, localcontext, lang)
                if newstatus == 401 and status != newstatus:
                    client.error(401, _("Authentication Required"),
                                 auth=wc.proxy.auth.get_challenges())
                    return
                # get (compiled) template
                template = wc.webgui.templatecache.templates[path]
                # expand template
                data = expand_template(template, context)
                # note: data is already encoded
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
            wc.log.exception(wc.LOG_GUI, "Template error: %r", path)
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


def expand_template (template, context):
    """expand the given template file fp in context
       return expanded data
    """
    return template.render(context)


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
    if hasattr(template_context, "_form_reset"):
        template_context._form_reset()
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
    path, dirs = wc.webgui.get_safe_template_path("macros/rules.html")
    rulemacros = wc.webgui.templatecache.templates[path]
    context_add(context, "rulemacros", rulemacros.macros)
    # standard macros
    path, dirs = wc.webgui.get_safe_template_path("macros/standard.html")
    macros = wc.webgui.templatecache.templates[path]
    context_add(context, "macros", macros.macros)
    # used by navigation macro
    add_nav_context(context, filename)
    # page template name
    context_add(context, "filename", filename)
    # base url
    context_add(context, "baseurl",
                "http://localhost:%d/" % wc.configuration.config['port'])
    add_i18n_context(context, lang)


nav_filenames = [
    "index_html",
    "config_html",
    "filterconfig_html",
    "update_html",
    "rating_html",
    "help_html",
]
def add_nav_context (context, filename):
    filename = filename.replace('.', '_')
    nav = {}
    for fname in nav_filenames:
        nav[fname] = fname==filename
    context_add(context, "nav", nav)


def add_i18n_context (context, lang):
    # language and i18n
    context_add(context, "lang", lang)
    translator = wc.get_translator(lang, translatorklass=Translator,
                                   fallbackklass=NullTranslator)
    context_add(context, "i18n", translator)
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
    context[key] = val


class Translator (gettext.GNUTranslations):

    def translate (self, domain, msgid, mapping=None,
                   context=None, target_language=None, default=None):
        _msg = self.gettext(msgid)
        wc.log.debug(wc.LOG_TAL, "TRANSLATED %r %r", msgid, _msg)
        return wc.webgui.TAL.TALInterpreter.interpolate(_msg, mapping)

    def gettext (self, msgid):
        return self.ugettext(msgid)

    def ngettext (self, singular, plural, number):
        return self.ungettext(singular, plural, number)


class NullTranslator (gettext.NullTranslations):

    def translate (self, domain, msgid, mapping=None,
                   context=None, target_language=None, default=None):
        return wc.webgui.TAL.TALInterpreter.interpolate(msgid, mapping)
