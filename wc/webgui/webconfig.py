# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2009 Bastian Kleineidam
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
import mimetypes
from .. import log, LOG_GUI, LOG_TAL, i18n, configuration, restart, get_translator
from . import templatecache, TAL, get_template_url, get_safe_template_path
from ..proxy import auth
from ..http.header import WcMessage


class WebConfig (object):
    """
    Load and send template files. This is a class rather than
    separate functions to store all config data in a single place,
    and to be able to use it as a (fake) server object.
    """

    def __init__ (self, client, url, form, protocol, clientheaders,
                 status=200, msg='OK', localcontext=None,
                 auth_challenges=None):
        """
        Store template configuration data in the object.
        """
        log.debug(LOG_GUI, "WebConfig %s %s", url, form)
        if isinstance(msg, unicode):
            msg = msg.encode("iso8859-1", "ignore")
        self.client = client
        self.url = url
        self.form = form
        self.protocol = protocol
        self.clientheaders = clientheaders
        self.status = status
        self.msg = msg
        if localcontext is None:
            self.localcontext = {}
        else:
            self.localcontext = localcontext
        self.auth_challenges = auth_challenges
        # Flag ensuring load() is called before send().
        self._loaded = False
        # We pretend to be the server.
        self.connected = True

    def load (self):
        """
        Load the data of the template into self.data. Errors are
        catched and redirected to the appropriate internal error
        template.
        """
        try:
            self._load()
        except IOError:
            log.exception(LOG_GUI, "Wrong path %r:", self.url)
            if self.status == 404:
                raise
            self.status = 404
            self.msg = _("Not Found")
            self.localcontext["error"] = self.url
            self.url = "/internal_404.html"
            self.load()
        except StandardError, msg:
            # catch standard exceptions and report internal error
            log.exception(LOG_GUI, "Template error: %r", self.url)
            if self.status == 500:
                raise
            self.status = 500
            self.msg = _("Internal Error")
            self.url = "/internal_500.html"
            self.localcontext["error"] = str(msg)
            self.load()
        # not catched builtin exceptions are:
        # SystemExit, StopIteration and all warnings

    def _load (self):
        """
        Helper method to handle the raw template data retrieval,
        without catching errors.
        """
        lang = i18n.get_headers_lang(self.clientheaders)
        hostname = self.client.socket.getsockname()[0]
        # get the template filename
        path, dirs, lang = get_template_url(self.url, lang)
        self.newstatus = None
        if path.endswith('.html'):
            # get TAL context
            context, self.newstatus = get_context(dirs, self.form,
                                           self.localcontext, hostname, lang)
            if self.newstatus == 401 and self.status != 401:
                self.status = 401
                self.msg = _("Authentication Required")
                self.url = "/internal_401.html"
                self.auth_challenges = auth.get_challenges()
                self.load()
                return
            # get (compiled) template
            template = templatecache.templates[path]
            # expand template
            self.data = expand_template(template, context)
            # note: data is already encoded
        else:
            fp = file(path, 'rb')
            self.data = fp.read()
            fp.close()
        self._loaded = True

    def send (self):
        """
        Send response to client.
        """
        if not self._loaded:
            self.load()
        response = "%s %d %s" % (self.protocol, self.status, self.msg)
        headers = get_headers(self.url, self.status, self.auth_challenges,
                              self.clientheaders)
        self.client.server_response(self, response, self.status, headers)
        self.client.server_content(self.data)
        self.client.server_close(self)
        # Check for restart.
        if self.newstatus == "restart":
            restart()

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
    headers = WcMessage()
    headers['Server'] = 'Proxy\r'
    if auth_challenges:
        if status not in (401, 407):
            log.error(LOG_GUI,
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
    template_context = None
    # this can raise an import error
    exec "from %s import %s as template_context" % (modulepath, template)
    # make TAL context
    context = {}
    if hasattr(template_context, "_form_reset"):
        template_context._form_reset()
    if hasattr(template_context, "_exec_form") and form is not None:
        # handle form action
        log.debug(LOG_GUI, "got form %s", form)
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
    for key, value in localcontext.iteritems():
        context_add(context, key, value)
    return context, status


def add_default_context (context, filename, hostname, lang):
    """
    Add context variables used by all templates.
    """
    # rule macros
    path = get_safe_template_path("macros/rules.html")[0]
    rulemacros = templatecache.templates[path]
    context_add(context, "rulemacros", rulemacros.macros)
    # standard macros
    path = get_safe_template_path("macros/standard.html")[0]
    macros = templatecache.templates[path]
    context_add(context, "macros", macros.macros)
    # used by navigation macro
    add_nav_context(context, filename)
    # page template name
    context_add(context, "filename", filename)
    # base url
    port = configuration.config['port']
    context_add(context, "baseurl", "http://%s:%d/" % (hostname, port))
    newport = configuration.config.get('newport', port)
    context_add(context, "newbaseurl", "http://%s:%d/" % (hostname, newport))
    add_i18n_context(context, lang)
    # XXX TODO referrer variables
    context_add(context, "referrer", "XXX")
    context_add(context, "no_referrer", True)
    context_add(context, "self_referrer", False)
    context_add(context, "unknown_referrer", False)


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
    context_add(context, "i18n", TALTranslator(get_translator(lang)))
    # other available languges
    otherlanguages = []
    for la in i18n.supported_languages:
        if lang == la:
            continue
        otherlanguages.append({'code': la,
                               'name': i18n.lang_name(la),
                               'trans': i18n.lang_trans(la, lang),
                              })
    context_add(context, "otherlanguages", otherlanguages)


def context_add (context, key, val):
    """
    Add key/val pair to context.
    """
    context[key] = val


class TALTranslator (object):
    """Proxy for a gettext translator, providing the "translate" method."""

    def __init__ (self, translator):
        """The initializer."""
        super(TALTranslator, self).__init__()
        self._translator = translator

    def __getattr__ (self, name):
        return getattr(self._translator, name)

    def translate (self, domain, msgid, mapping=None,
                   context=None, target_language=None, default=None):
        """Interpolates and translate TAL expression."""
        _msg = self.ugettext(msgid)
        log.debug(LOG_TAL, "TRANSLATED %r %r", msgid, _msg)
        return TAL.TALInterpreter.interpolate(_msg, mapping)

