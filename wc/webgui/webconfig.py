# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2005  Bastian Kleineidam
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
HTML configuration interface functions.
"""

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
    """
    Class for web configuration templates.
    """

    def __init__ (self, client, url, form, protocol, clientheaders,
                 status=200, msg=_('Ok'), localcontext=None,
                 auth_challenges=None):
        """
        Load a web configuration template and return response.
        """
        wc.log.debug(wc.LOG_GUI, "WebConfig %s %s", url, form)
        if isinstance(msg, unicode):
            msg = msg.encode("iso8859-1", "ignore")
        self.client = client
        # we pretend to be the server
        self.connected = True
        headers = get_headers(url, status, auth_challenges, clientheaders)
        path = ""
        newstatus = None
        try:
            lang = wc.i18n.get_headers_lang(clientheaders)
            # get the template filename
            path, dirs, lang = wc.webgui.get_template_url(url, lang)
            if path.endswith('.html'):
                # get TAL context
                hostname = client.socket.getsockname()[0]
                context, newstatus = \
                     get_context(dirs, form, localcontext, hostname, lang)
                if newstatus == 401 and status != newstatus:
                    client.error(401, _("Authentication Required"),
                               auth_challenges=wc.proxy.auth.get_challenges())
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

        # write response to client
        self.put_response(data, protocol, status, msg, headers)
        # restart?
        if newstatus == "restart":
            wc.restart()


    def put_response (self, data, protocol, status, msg, headers):
        """
        Write response to client.
        """
        response = "%s %d %s" % (protocol, status, msg)
        self.client.server_response(self, response, status, headers)
        self.client.server_content(data)
        self.client.server_close(self)

    def client_abort (self):
        """
        Client has aborted the connection.
        """
        self.client = None


def expand_template (template, context):
    """
    Expand the given template file fp in context

    @return: expanded data
    """
    return template.render(context)


def get_headers (url, status, auth_challenges, clientheaders):
    """
    Get proxy headers to send.
    """
    headers = wc.http.header.WcMessage()
    headers['Server'] = 'Proxy\r'
    if auth_challenges:
        if status not in (401, 407):
            wc.log.error(wc.LOG_GUI,
                         "Authentication with wrong status %d", status)
        else:
            if status == 407:
                name = 'Proxy-Authenticate'
            if status == 401:
                name = 'WWW-Authenticate'
            for auth in auth_challenges:
                headers.addheader(name, "%s\r" % auth)
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
    return headers


def get_context (dirs, form, localcontext, hostname, lang):
    """
    Get template context, raise ImportError if not found.
    The context includes the given local context, plus all variables
    defined by the imported context module
    Evaluation of the context can set a different HTTP status.
    Returns tuple `(context, status)`
    """
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
    add_default_context(context, dirs[-1], hostname, lang)
    # augment the context
    attrs = [ x for x in dir(template_context) if not x.startswith('_') ]
    for attr in attrs:
        context_add(context, attr, getattr(template_context, attr))
    # add local context
    if localcontext is not None:
        for key, value in localcontext.items():
            context_add(context, key, value)
    return context, status


def add_default_context (context, filename, hostname, lang):
    """
    Add context variables used by all templates.
    """
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
    port = wc.configuration.config['port']
    context_add(context, "baseurl", "http://%s:%d/" % (hostname, port))
    newport = wc.configuration.config.get('newport', port)
    context_add(context, "newbaseurl", "http://%s:%d/" % (hostname, newport))
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
    """
    Add 'nav' variable to context.
    """
    filename = filename.replace('.', '_')
    nav = {}
    for fname in nav_filenames:
        nav[fname] = fname == filename
    context_add(context, "nav", nav)


def add_i18n_context (context, lang):
    """
    Add i18n variables 'lang', 'i18n' and 'otherlanguages' to context.
    """
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
    """
    Add key/val pair to context.
    """
    context[key] = val


class Translator (gettext.GNUTranslations):
    """
    Translator which interpolates TAL expressions.
    """

    def translate (self, domain, msgid, mapping=None,
                   context=None, target_language=None, default=None):
        """
        Interpolates and translate TAL expression.
        """
        _msg = self.gettext(msgid)
        wc.log.debug(wc.LOG_TAL, "TRANSLATED %r %r", msgid, _msg)
        return wc.webgui.TAL.TALInterpreter.interpolate(_msg, mapping)

    def gettext (self, msgid):
        """
        Return unicode with ugettext().
        """
        return self.ugettext(msgid)

    def ngettext (self, singular, plural, number):
        """
        Return unicode with ungettext().
        """
        return self.ungettext(singular, plural, number)


class NullTranslator (gettext.NullTranslations):
    """
    Fallback translator which interpolates TAL expressions.
    """

    def translate (self, domain, msgid, mapping=None,
                   context=None, target_language=None, default=None):
        """
        Interpolates TAL expression.
        """
        return wc.webgui.TAL.TALInterpreter.interpolate(msgid, mapping)
