# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2006 Bastian Kleineidam
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
Store configuration data.
"""

import time
import signal
import os
import sets
import stat
import glob
import xml.parsers.expat

import wc
import wc.log
import wc.ip
import wc.decorators
import wc.strformat
import wc.fileutil
import wc.rating.service

ConfigCharset = "iso-8859-1"

# global config var
config = None
# if config is about to be reloaded
pending_reload = False

def init (confdir=wc.ConfigDir):
    """
    Initialize and load the configuration.
    """
    global config
    config = Configuration(confdir)
    return config


# note that Python already ignores SIGPIPE, so no need to configure that
if os.name == 'posix':
    _signum = signal.SIGHUP
else:
    _signum = signal.NSIG
@wc.decorators.signal_handler(_signum)
def sighup_reload_config (signum, frame):
    """
    Support reload on posix systems.
    Store timer for reloading configuration data.
    """
    global pending_reload
    if not pending_reload:
        pending_reload = True
        import wc.proxy.timer
        wc.proxy.timer.make_timer(1, reload_config)


def reload_config ():
    """
    Reload configuration.
    """
    global pending_reload
    config.reset()
    config.read_proxyconf()
    config.read_filterconf()
    config.init_filter_modules()
    wc.proxy.dns_lookups.init_resolver()
    wc.filter.VirusFilter.init_clamav_conf(config['clamavconf'])
    pending_reload = False


def proxyconf_file (confdir):
    """
    Return proxy configuration filename.
    """
    return os.path.join(confdir, "webcleaner.conf")


def filterconf_files (dirname):
    """
    Return list of filter configuration filenames.
    """
    return glob.glob(os.path.join(dirname, "*.zap"))


# available filter modules
filtermodules = [
    "Header",
    "Blocker",
    "GifImage",
    "ImageSize",
    "ImageReducer",
    "BinaryCharFilter",
    "HtmlRewriter",
    "XmlRewriter",
    "Replacer",
    "Compress",
# XXX to be implemented    "RatingHeader",
    "VirusFilter",
    "MimeRecognizer",
]
filtermodules.sort()

# names of config values that have to be in ASCII
ascii_values = [
    "adminuser",
    "adminpass",
    "proxyuser",
    "proxypass",
    "parentproxyuser",
    "parentproxypass",
]

rewriting_filter_modules = [
    'HtmlRewriter',
    'Replacer',
    'GifImage',
    'Compress',
    'ImageReducer',
    'ImageSize',
    'VirusFilter',
    'BinaryCharFilter',
    'XmlRewriter',
]

class Configuration (dict):
    """
    Hold all configuration data, inclusive filter rules.
    """

    def __init__ (self, confdir):
        """
        Initialize the options.
        """
        dict.__init__(self)
        self.filterdir = self.configdir = confdir
        self.configfile = proxyconf_file(self.configdir)
        # reset to default values
        self.reset()
        # read configuration
        self.read_proxyconf()
        self.check_ssl_certificates()
        self.read_filterconf()

    def check_ssl_certificates (self):
        """
        Check existance of SSL support and generate certificates if
        needed. This is necessary since SSL support can be installed
        after WebCleaner.
        """
        import wc
        if wc.HasSsl and self["sslgateway"]:
            import wc.proxy.ssl
            if not wc.proxy.ssl.exist_certificates(self.configdir):
                wc.proxy.ssl.create_certificates(self.configdir)

    def reset (self):
        """
        Reset to default values.
        """
        self['configversion'] = '0.10'
        # The bind address specifies on which address the socket should
        # listen.
        # The default empty string represents INADDR_ANY which means to
        # accept incoming connections from all hosts.
        self['bindaddress'] = ''
        self['port'] = 8080
        self['sslport'] = 8443
        self['sslgateway'] = 0
        self['adminuser'] = ""
        self['adminpass'] = ""
        self['proxyuser'] = ""
        self['proxypass'] = ""
        self['parentproxy'] = ""
        self['parentproxyport'] = 3128
        self['parentproxyuser'] = ""
        self['parentproxypass'] = ""
        # dynamically stored parent proxy authorization credentials
        self['parentproxycreds'] = None
        self['folderrules'] = []
        # filter module name list
        self['filters'] = []
        # filter module instance list
        self['filtermodules'] = []
        # filter module instances sorted by filter stage
        self['filterlist'] = {}
        self['colorize'] = 0
        # DNS resolved nofilterhosts
        self['nofilterhosts'] = None
        self['allowedhosts'] = None
        self['starttime'] = time.time()
        self['mime_content_rewriting'] = sets.Set()
        self['gui_theme'] = "classic"
        self['timeout'] = 10
        self['auth_ntlm'] = 0
        self['clamavconf'] = ""
        # in development mode some values have different defaults
        self['development'] = int(os.environ.get("WC_DEVELOPMENT", "0"))
        self['baseurl'] = wc.Url
        self['try_google'] = 0
        self['rating_service'] = wc.rating.service.WebCleanerService()
        # delete all registered sids
        from wc.filter.rules import delete_registered_sids
        delete_registered_sids()

    def read_proxyconf (self):
        """
        Read proxy configuration.
        """
        WConfigParser(self.configfile, self).parse()
        # make sure that usernames and passwords are ASCII, or there
        # can be encoding errors
        for name in ascii_values:
            if not wc.strformat.is_ascii(self[name]):
                msg = "The %r configuration value must be ASCII." % name
                raise TypeError(msg)

    def write_proxyconf (self):
        """
        Write proxy configuration.
        """
        lines = []
        lines.append('<?xml version="1.0" encoding="%s"?>' % ConfigCharset)
        lines.append('<!DOCTYPE webcleaner SYSTEM "webcleaner.dtd">')
        lines.append('<webcleaner')
        lines.append(' configversion="%s"' %
                     xmlquoteattr(self['configversion']))
        lines.append(' bindaddress="%s"' % xmlquoteattr(self['bindaddress']))
        lines.append(' port="%d"' % self['port'])
        lines.append(' sslport="%d"' % self['sslport'])
        lines.append(' sslgateway="%d"' % self['sslgateway'])
        lines.append(' adminuser="%s"' % xmlquoteattr(self['adminuser']))
        lines.append(' adminpass="%s"' % xmlquoteattr(self['adminpass']))
        lines.append(' proxyuser="%s"' % xmlquoteattr(self['proxyuser']))
        lines.append(' proxypass="%s"' % xmlquoteattr(self['proxypass']))
        lines.append(' parentproxy="%s"' % xmlquoteattr(self['parentproxy']))
        lines.append(' parentproxyuser="%s"' %
                     xmlquoteattr(self['parentproxyuser']))
        lines.append(' parentproxypass="%s"' %
                     xmlquoteattr(self['parentproxypass']))
        lines.append(' parentproxyport="%d"' % self['parentproxyport'])
        lines.append(' timeout="%d"' % self['timeout'])
        lines.append(' gui_theme="%s"' % xmlquoteattr(self['gui_theme']))
        lines.append(' auth_ntlm="%d"' % self['auth_ntlm'])
        lines.append(' try_google="%d"' % self['try_google'])
        lines.append(' clamavconf="%s"' % xmlquoteattr(self['clamavconf']))
        hosts = self['nofilterhosts']
        lines.append(' nofilterhosts="%s"' % xmlquoteattr(",".join(hosts)))
        hosts = self['allowedhosts']
        lines.append(' allowedhosts="%s"' % xmlquoteattr(",".join(hosts)))
        lines.append('>')
        for key in self['filters']:
            lines.append('<filter name="%s"/>' % xmlquoteattr(key))
        lines.append('</webcleaner>')
        content = os.linesep.join(lines)
        wc.fileutil.write_file(self.configfile, content)

    def read_filterconf (self):
        """
        Read filter rules.
        """
        from wc.filter.rules import generate_sids
        from wc.filter.rules.FolderRule import recalc_up_down
        for filename in filterconf_files(self.filterdir):
            if os.stat(filename)[stat.ST_SIZE] == 0:
                wc.log.warn(wc.LOG_PROXY, "Skipping empty file %r", filename)
                continue
            p = ZapperParser(filename)
            p.parse()
            self['folderrules'].append(p.folder)
        # sort folders according to oid
        self['folderrules'].sort()
        for i, folder in enumerate(self['folderrules']):
            folder.oid = i
            recalc_up_down(folder.rules)
        recalc_up_down(self['folderrules'])
        prefix = self['development'] and "wc" or "lc"
        generate_sids(prefix)

    def merge_folder (self, folder, dryrun=False, log=None):
        """
        Merge given folder data into config

        @return: True if something has changed
        """
        # test for correct category
        assert folder.sid and folder.sid.startswith("wc"), \
          "Invalid SID in folder %s" % str(folder)
        f = [ rule for rule in self['folderrules'] if rule.sid == folder.sid ]
        assert len(f) <= 1, "Duplicate SID found: %s" % str(f)
        if f:
            chg = f[0].update(folder, dryrun=dryrun, log=log)
        else:
            chg = True
            print >> log, " ", _("inserting %s") % folder.tiptext()
            if not dryrun:
                folder.oid = len(self['folderrules'])
                self['folderrules'].append(folder)
        return chg

    def write_filterconf (self):
        """
        Write filter rules.
        """
        for folder in self['folderrules']:
            folder.write()

    def init_filter_modules (self):
        """
        Go through list of rules and store them in the filter
        objects. This will also compile regular expression strings
        to regular expression objects.
        """
        # reset filter lists
        for stage in wc.filter.FilterStages:
            self['filterlist'][stage] = []
        self['filtermodules'] = []
        self['mime_content_rewriting'] = sets.Set()
        for filtername in self['filters']:
            # import filter module
            exec "from filter import %s" % filtername
            # Filter class has same name as module.
            clazz = getattr(getattr(wc.filter, filtername), filtername)
            if not clazz.enable:
                # The filter is not enabled, probably due to missing
                # dependencies.
                continue
            # add content-rewriting mime types to special list
            instance = clazz()
            if filtername in rewriting_filter_modules:
                self['mime_content_rewriting'].update(instance.mimes)
            self['filtermodules'].append(instance)
            for folder in self['folderrules']:
                if folder.disable:
                    continue
                for rule in folder.rules:
                    if rule.disable:
                        continue
                    if rule.name in instance.rulenames:
                        instance.addrule(rule)
            for stage in instance.stages:
                self['filterlist'][stage].append(instance)
        for filters in self['filterlist'].itervalues():
            # see Filter.__cmp__ on how sorting is done
            filters.sort()

    def nofilter (self, url):
        """
        Decide whether to filter this url or not.

        @return: True if the request must not be filtered, else False
        """
        return wc.url.match_url(url, self['nofilterhosts'])

    def allowed (self, host):
        """
        Return True if the host is allowed for proxying, else False.
        """
        hostset = self['allowedhostset']
        return wc.ip.host_in_set(host, hostset[0], hostset[1])


from wc.XmlUtils import xmlquoteattr

##### xml parsers #########

rulenames = (
  u'block',
  u'blockurls',
  u'blockdomains',
  u'allowurls',
  u'allowdomains',
  u'allow',
  u'header',
  u'image',
  u'imagereduce',
  u'nocomments',
  u'nojscomments',
  u'javascript',
  u'replace',
# XXX to be implemented  u'rating',
  u'antivirus',
  u'htmlrewrite',
  u'xmlrewrite',
)
_nestedtags = (
  u'title', u'description',
  # urlrule nested tag names
  u'matchurl', u'nomatchurl',
  # htmlrewriter rule nested tag names
  u'attr', u'enclosed', u'replacement',
  # rating rule nested tag names
  u'url', u'category',
)
# make sure no name clashes occur between tag names
for _x in _nestedtags:
    assert _x not in rulenames


def make_xmlparser ():
    """
    Return a new xml parser object.
    """
    # note: this parser returns unicode strings
    return xml.parsers.expat.ParserCreate()


class ParseException (Exception):
    """
    Exception thrown at parse errors.
    """
    pass


class BaseParser (object):
    """
    Base class for parsing xml config files.
    """

    def __init__ (self, filename):
        """
        Initialize filename and configuration for this parser.
        """
        super(BaseParser, self).__init__()
        self.filename = filename
        # error condition
        self.error = None
        # set by _preparse() and _postparse()
        self.xmlparser = None

    def _preparse (self):
        """
        Set handler functions before parsing.
        """
        self.xmlparser = make_xmlparser()
        self.xmlparser.StartElementHandler = self.start_element
        self.xmlparser.EndElementHandler = self.end_element
        self.xmlparser.CharacterDataHandler = self.character_data

    def _postparse (self):
        """
        Remove handler functions after parsing; avoids cyclic references.
        """
        self.xmlparser.StartElementHandler = None
        self.xmlparser.EndElementHandler = None
        self.xmlparser.CharacterDataHandler = None
        # note: expat parsers cannot be reused
        self.xmlparser = None

    def parse (self, fp=None):
        """
        Parse the stored filename, or another source given by fp.
        """
        assert wc.log.debug(wc.LOG_PROXY, "Parsing %s", self.filename)
        if fp is None:
            fp = file(self.filename)
        self._preparse()
        try:
            try:
                self.xmlparser.ParseFile(fp)
            except (xml.parsers.expat.ExpatError, ParseException):
                wc.log.exception(wc.LOG_PROXY, "Error parsing %s",
                                 self.filename)
                raise SystemExit("parse error in %s" % self.filename)
        finally:
            self._postparse()

    def start_element (self, name, attrs):
        """
        Basic start element method doing nothing.
        """
        pass

    def end_element (self, name):
        """
        Basic end element method doing nothing.
        """
        pass

    def character_data (self, data):
        """
        Basic character data method doing nothing.
        """
        pass


class ZapperParser (BaseParser):
    """
    Parser class for *.zap filter configuration files.
    """

    def __init__ (self, filename, compile_data=True):
        """
        Initialize filename, configuration and compile flag.
        """
        super(ZapperParser, self).__init__(filename)
        from wc.filter.rules.FolderRule import FolderRule
        self.folder = FolderRule(filename=filename)
        self.cmode = None
        self.rule = None
        self.compile_data = compile_data

    def start_element (self, name, attrs):
        """
        Handle start tag of folder, rule or nested element.
        """
        super(ZapperParser, self).start_element(name, attrs)
        if self.error:
            return
        self.cmode = name
        if name in rulenames:
            self.rule = wc.filter.GetRuleFromName(name)
            self.rule.fill_attrs(attrs, name)
            self.folder.append_rule(self.rule)
        # tag has character data
        elif name in _nestedtags:
            if self.rule is None:
                self.folder.fill_attrs(attrs, name)
            else:
                self.rule.fill_attrs(attrs, name)
        elif name == 'folder':
            self.folder.fill_attrs(attrs, name)
        else:
            wc.log.warn(wc.LOG_FILTER, _("unknown tag name %r"), name)
            self.error = name
            self.cmode = None

    def end_element (self, name):
        """
        Handle end tag of folder, rule or nested element.
        """
        if self.error:
            if name == self.error:
                self.error = None
        else:
            self.cmode = None
            if self.rule is None:
                self.folder.end_data(name)
            else:
                self.rule.end_data(name)
            if name in rulenames:
                if self.compile_data:
                    self.rule.compile_data()
            elif name == 'folder':
                if self.compile_data:
                    self.folder.compile_data()

    def character_data (self, data):
        """
        Handle rule of folder character data.
        """
        if self.error:
            pass
        elif self.cmode:
            if self.rule is None:
                self.folder.fill_data(data, self.cmode)
            else:
                self.rule.fill_data(data, self.cmode)


class WConfigParser (BaseParser):
    """
    Parser class for webcleaner.conf configuration files.
    """

    def __init__ (self, filename, _config):
        """
        Initialize filename, configuration and compile flag.
        """
        super(WConfigParser, self).__init__(filename)
        self.config = _config

    def start_element (self, name, attrs):
        """
        Handle xml configuration for webcleaner attributes and filter
        modules.
        """
        if self.error:
            return
        if name == 'webcleaner':
            for key, val in attrs.iteritems():
                self.config[key] = val
            for key in ('port', 'sslport', 'parentproxyport', 'timeout',
                        'auth_ntlm', 'colorize', 'development', 'try_google',
                        'sslgateway',):
                self.config[key] = int(self.config[key])
            if self.config['nofilterhosts'] is not None:
                strhosts = self.config['nofilterhosts']
                self.config['nofilterhosts'] = strhosts.split(",")
            else:
                self.config['nofilterhosts'] = []
            if self.config['allowedhosts'] is not None:
                hosts = self.config['allowedhosts'].split(',')
                self.config['allowedhosts'] = hosts
                self.config['allowedhostset'] = wc.ip.hosts2map(hosts)
            else:
                self.config['allowedhosts'] = []
                self.config['allowedhostset'] = [sets.Set(), []]
        elif name == 'filter':
            assert wc.log.debug(wc.LOG_FILTER, "enable filter module %s",
                         attrs['name'])
            self.config['filters'].append(attrs['name'])
        else:
            wc.log.warn(wc.LOG_PROXY, _("unknown tag name %r"), name)
            self.error = name

    def end_element (self, name):
        """
        Handle error case.
        """
        if self.error:
            if name == self.error:
                self.error = None
