# -*- coding: iso-8859-1 -*-
"""configuration data"""
# Copyright (C) 2000-2004  Bastian Kleineidam
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

import time
import os
import sets
import stat
import glob
import xml.parsers.expat

import wc
import wc.log
import wc.ip

ConfigCharset = "iso-8859-1"

# global config var
config = None
# if config is about to be reloaded
pending_reload = False

def init (confdir=wc.ConfigDir):
    global config
    config = Configuration(confdir)
    import wc.filter.Rating
    wc.filter.Rating.rating_cache_load()
    return config


def sighup_reload_config (signum, frame):
    """store timer for reloading configuration data"""
    global pending_reload
    if not pending_reload:
        pending_reload = True
        wc.proxy.make_timer(1, reload_config)


def reload_config ():
    """reload configuration"""
    global pending_reload
    config.reset()
    config.read_proxyconf()
    config.read_filterconf()
    config.init_filter_modules()
    wc.proxy.dns_lookups.init_resolver()
    wc.filter.VirusFilter.init_clamav_conf()
    pending_reload = False


def proxyconf_file (confdir):
    """return proxy configuration filename"""
    return os.path.join(confdir, "webcleaner.conf")


def filterconf_files (dirname):
    """return list of filter configuration filenames"""
    return glob.glob(os.path.join(dirname, "*.zap"))


# available filter modules
filtermodules = ["Header", "Blocker", "GifImage", "ImageSize", "ImageReducer",
                 "BinaryCharFilter", "Rewriter", "Replacer", "Compress",
                 "RatingHeader", "VirusFilter", "MimeRecognizer",
                ]
filtermodules.sort()


class Configuration (dict):
    """hold all configuration data, inclusive filter rules"""

    def __init__ (self, confdir):
        """Initialize the options"""
        dict.__init__(self)
        self.filterdir = self.configdir = confdir
        self.configfile = proxyconf_file(self.configdir)
        # reset to default values
        self.reset()
        # read configuration
        self.read_proxyconf()
        self.read_filterconf()

    def reset (self):
        """Reset to default values"""
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
        self['filters'] = []
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
        if os.name == 'posix':
            self['clamavconf'] = "/etc/clamav/clamav.conf"
        elif os.name == 'nt':
            self['clamavconf'] = r"c:\clamav-devel\etc\clamav.conf"
        else:
            self['clamavconf'] = os.path.join(os.getcwd(), "clamav.conf")
        # in development mode some values have different defaults
        self['development'] = os.environ.get("WC_DEVELOPMENT", 0)
        self['baseurl'] = wc.Url
        self['try_google'] = 0
        # delete all registered sids
        from wc.filter.rules import delete_registered_sids
        delete_registered_sids()

    def read_proxyconf (self):
        """read proxy configuration"""
        WConfigParser(self.configfile, self).parse()

    def write_proxyconf (self):
        """write proxy configuration"""
        lines = []
        lines.append('<?xml version="1.0" encoding="%s"?>' % ConfigCharset)
        lines.append('<!DOCTYPE webcleaner SYSTEM "webcleaner.dtd">')
        lines.append('<webcleaner')
        lines.append(' version="%s"' % xmlquoteattr(self['version']))
        lines.append(' bindaddress="%s"' % xmlquoteattr(self['bindaddress']))
        lines.append(' port="%d"' % self['port'])
        lines.append(' sslport="%d"' % self['sslport'])
        if self['sslgateway']:
            lines.append(' sslgateway="%d"' % self['sslgateway'])
        lines.append(' adminuser="%s"' % xmlquoteattr(self['adminuser']))
        lines.append(' adminpass="%s"' % xmlquoteattr(self['adminpass']))
        lines.append(' proxyuser="%s"' % xmlquoteattr(self['proxyuser']))
        lines.append(' proxypass="%s"' % xmlquoteattr(self['proxypass']))
        if self['parentproxy']:
            lines.append(' parentproxy="%s"' %
                         xmlquoteattr(self['parentproxy']))
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
        f = file(self.configfile, 'w')
        f.write(os.linesep.join(lines))
        f.close()

    def read_filterconf (self):
        """read filter rules"""
        from wc.filter.rules import generate_sids
        from wc.filter.rules.FolderRule import recalc_up_down
        for filename in filterconf_files(self.filterdir):
            if os.stat(filename)[stat.ST_SIZE] == 0:
                wc.log.warn(wc.LOG_PROXY, "Skipping empty file %r", filename)
                continue
            p = ZapperParser(filename, self)
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
        """merge given folder data into config
        return True if something has changed
        """
        # test for correct category
        assert folder.sid and folder.sid.startswith("wc")
        f = [ rule for rule in self['folderrules'] if rule.sid == folder.sid ]
        assert len(f) <= 1
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
        """write filter rules"""
        for folder in self['folderrules']:
            folder.write()

    def init_filter_modules (self):
        """go through list of rules and store them in the filter
        objects. This will also compile regular expression strings
        to regular expression objects"""
        # reset filter list
        for stage in wc.filter.FilterStages:
            self['filterlist'][stage] = []
        self['mime_content_rewriting'] = sets.Set()
        for filtername in self['filters']:
            # import filter module
            exec "from filter import %s" % filtername
            # filter class has same name as module
            clazz = getattr(getattr(wc.filter, filtername), filtername)
            # add content-rewriting mime types to special list
            if filtername in ['Rewriter', 'Replacer', 'GifImage',
                              'Compress', 'ImageReducer', 'ImageSize',
                              'VirusFilter', 'BinaryCharFilter']:
                self['mime_content_rewriting'].update(clazz.mimelist)
            instance = clazz()
            for folder in self['folderrules']:
                if folder.disable:
                    continue
                for rule in folder.rules:
                    if rule.disable:
                        continue
                    if rule.get_name() in clazz.rulenames:
                        instance.addrule(rule)
            for stage in clazz.stages:
                self['filterlist'][stage].append(instance)
        for filters in self['filterlist'].values():
            # see Filter.__cmp__ on how sorting is done
            filters.sort()

    def nofilter (self, url):
        """Decide whether to filter this url or not.
           returns True if the request must not be filtered, else False
        """
        return wc.url.match_url(url, self['nofilterhosts'])

    def allowed (self, host):
        """return True if the host is allowed for proxying, else False"""
        hostset = self['allowedhostset']
        return wc.ip.host_in_set(host, hostset[0], hostset[1])


from wc.XmlUtils import xmlquote, xmlquoteattr

##### xml parsers #########

rulenames = (
  u'rewrite',
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
  u'javascript',
  u'replace',
  u'rating',
  u'antivirus',
)
_nestedtags = (
  'title', 'description',
  # urlrule nested tag names
  'matchurl', 'nomatchurl',
  # rewriter rule nested tag names
  'attr','enclosed','replacement',
  # rating rule nested tag names
  'url', 'category',
)


def make_xmlparser ():
    """return a new xml parser object"""
    # note: this parser returns unicode strings
    return xml.parsers.expat.ParserCreate()


class ParseException (Exception):
    """exception thrown at parse errors"""
    pass


class BaseParser (object):
    """base class for parsing xml config files"""

    def __init__ (self, filename, _config):
        """initialize filename and configuration for this parser"""
        super(BaseParser, self).__init__()
        self.filename = filename
        self.config = _config
        # set by _preparse() and _postparse()
        self.xmlparser = None

    def _preparse (self):
        """set handler functions before parsing"""
        self.xmlparser = make_xmlparser()
        self.xmlparser.StartElementHandler = self.start_element
        self.xmlparser.EndElementHandler = self.end_element
        self.xmlparser.CharacterDataHandler = self.character_data

    def _postparse (self):
        """remove handler functions after parsing; avoids cyclic references"""
        self.xmlparser.StartElementHandler = None
        self.xmlparser.EndElementHandler = None
        self.xmlparser.CharacterDataHandler = None
        # note: expat parsers cannot be reused
        self.xmlparser = None

    def parse (self, fp=None):
        """parse the stored filename, or another source given by fp"""
        wc.log.debug(wc.LOG_PROXY, "Parsing %s", self.filename)
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
        """basic start element method doing nothing"""
        pass

    def end_element (self, name):
        """basic end element method doing nothing"""
        pass

    def character_data (self, data):
        """basic character data method doing nothing"""
        pass


class ZapperParser (BaseParser):
    """parser class for *.zap filter configuration files"""

    def __init__ (self, filename, _config, compile_data=True):
        """initialize filename, configuration and compile flag"""
        super(ZapperParser, self).__init__(filename, _config)
        from wc.filter.rules.FolderRule import FolderRule
        self.folder = FolderRule(filename=filename)
        self.cmode = None
        self.rule = None
        self.compile_data = compile_data

    def start_element (self, name, attrs):
        """handle start tag of folder, rule or nested element"""
        super(ZapperParser, self).start_element(name, attrs)
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
            raise ParseException, _("unknown tag name %r") % name

    def end_element (self, name):
        """handle end tag of folder, rule or nested element"""
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
        """handle rule of folder character data"""
        if self.cmode:
            if self.rule is None:
                self.folder.fill_data(data, self.cmode)
            else:
                self.rule.fill_data(data, self.cmode)


class WConfigParser (BaseParser):
    """parser class for webcleaner.conf configuration files"""

    def start_element (self, name, attrs):
        """handle xml configuration for webcleaner attributes and filter
           modules
        """
        if name == 'webcleaner':
            for key, val in attrs.items():
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
            wc.log.debug(wc.LOG_FILTER, "enable filter module %s",
                         attrs['name'])
            self.config['filters'].append(attrs['name'])
