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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import os, sys, time, socket
import xml.parsers.expat
import _webcleaner2_configdata as configdata
from glob import glob
from sets import Set
from stat import ST_SIZE
Version = configdata.version
AppName = configdata.appname
Name = configdata.name
Description = configdata.description
App = AppName+" "+Version
UserAgent = AppName+"/"+Version
Author =  configdata.author
HtmlAuthor = Author.replace(' ', '&nbsp;')
Copyright = "Copyright © 2000-2002 "+Author
HtmlCopyright = "Copyright &copy; 2000-2003 "+HtmlAuthor
AppInfo = App+"              "+Copyright
HtmlAppInfo = App+", "+HtmlCopyright
Url = configdata.url
Email = configdata.author_email
Freeware = """%s comes with ABSOLUTELY NO WARRANTY!
This is free software, and you are welcome to redistribute it
under certain conditions. Look at the file `LICENSE' whithin this
distribution.""" % AppName
ConfigDir = configdata.config_dir
TemplateDir = configdata.template_dir
LocaleDir = os.path.join(configdata.install_data, 'share', 'locale')
ConfigCharset = "iso-8859-1"

def iswriteable (fname):
    if os.path.isdir(fname) or os.path.islink(fname):
        return False
    try:
        if os.path.exists(fname):
            file(fname, 'a').close()
            return True
        else:
            file(fname, 'w').close()
            os.remove(fname)
            return True
    except IOError:
        pass
    return False


def sort_seq (seq):
    """return sorted list of given sequence"""
    l = list(seq)
    l.sort()
    return l

import ip, i18n

config = None

def wstartfunc (handle=None):
    global config
    # init logging
    initlog(os.path.join(ConfigDir, "logging.conf"))
    # support reload on posix systems
    if os.name=='posix':
        import signal
        signal.signal(signal.SIGHUP, sighup_reload_config)
        # change dir to avoid open files on umount
        os.chdir("/")
    # read configuration
    config = Configuration()
    config.init_filter_modules()
    # psyco library for speedup
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    # start the proxy
    info(PROXY, "Starting proxy on port %d", config['port'])
    from wc.proxy import mainloop
    mainloop(handle=handle)


def sighup_reload_config (signum, frame):
    """store timer for reloading configuration data"""
    make_timer(1, reload_config)


def reload_config ():
    """reload configuration"""
    config.reset()
    config.read_proxyconf()
    config.read_filterconf()
    config.init_filter_modules()


def get_localhosts ():
    """get list of localhost names and ips"""
    # XXX is this list of localhost stuff complete?
    addrinfo = socket.gethostbyaddr(socket.gethostname())
    localhosts = {
      'localhost' : None,
      'loopback' : None,
      '127.0.0.1' : None,
      '::1' : None,
      'ip6-localhost' : None,
      'ip6-loopback' : None,
    }
    localhosts[addrinfo[0]] = None
    for h in addrinfo[1]:
        localhosts[h] = None
    for h in addrinfo[2]:
        localhosts[h] = None
    return localhosts.keys()


def proxyconf_file ():
    """return proxy configuration filename"""
    return os.path.join(ConfigDir, "webcleaner.conf")


def filterconf_files ():
    """return list of filter configuration filenames"""
    return glob(os.path.join(ConfigDir, "*.zap"))


# available filter modules
filtermodules = ["Header", "Blocker", "GifImage", "ImageSize", "ImageReducer",
                 "BinaryCharFilter", "Rewriter", "Replacer", "Compress",
                 "RatingHeader",
                ]
filtermodules.sort()

from wc.XmlUtils import xmlquote, xmlquoteattr

class Configuration (dict):
    """hold all configuration data, inclusive filter rules"""

    def __init__ (self):
        """Initialize the options"""
        dict.__init__(self)
        # reset to default
        self.reset()
        # read configuration
        self.read_proxyconf()
        self.read_filterconf()
        if self['development']:
            # avoid conflicting servers if an official WebCleaner release
            # is installed
            self['port'] += 1
            self['sslport'] += 1
            self['sslgateway'] = 1
            # test data directory url
            self['baseurl'] = "file:///home/calvin/projects/webcleaner/test/"


    def reset (self):
        """Reset to default values"""
        self['configfile'] = proxyconf_file()
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
        self['filterlist'] = [[],[],[],[],[],[],[],[],[],[]]
        self['colorize'] = 0
        self['nofilterhosts'] = None
        # DNS resolved nofilterhosts
        self['allowedhosts'] = None
        self['starttime'] = time.time()
	# if set to one the bound socket does not accept connections from
	# hosts except localhost; normally not needed
        self['local_sockets_only'] = 0
        self['localhosts'] = get_localhosts()
        self['mime_content_rewriting'] = Set()
        self['gui_theme'] = "classic"
        self['timeout'] = 10
        self['auth_ntlm'] = 0
        # in development mode some values have different defaults
        self['development'] = os.environ.get("WC_DEVELOPMENT", 0)
        self['baseurl'] = Url
        self['try_google'] = 0
        # delete all registered sids
        from wc.filter.rules import delete_registered_sids
        delete_registered_sids()


    def read_proxyconf (self):
        """read proxy configuration"""
        WConfigParser(self['configfile'], self).parse()


    def write_proxyconf (self):
        """write proxy configuration"""
        f = file(self['configfile'], 'w')
        f.write("""<?xml version="1.0" encoding="%s"?>
<!DOCTYPE webcleaner SYSTEM "webcleaner.dtd">
<webcleaner
""" % ConfigCharset)
        f.write(' version="%s"\n' % xmlquoteattr(self['version']))
        port = self['port']
        sslport = self['sslport']
        if self['development']:
            port -= 1
            sslport -= 1
        f.write(' port="%d"\n' % port)
        f.write(' sslport="%d"\n' % sslport)
        if self['sslgateway']:
            f.write(' sslgateway="%d"\n' % self['sslgateway'])
        f.write(' adminuser="%s"\n' % xmlquoteattr(self['adminuser']))
        f.write(' adminpass="%s"\n' % xmlquoteattr(self['adminpass']))
        f.write(' proxyuser="%s"\n' % xmlquoteattr(self['proxyuser']))
        f.write(' proxypass="%s"\n' % xmlquoteattr(self['proxypass']))
        if self['parentproxy']:
            f.write(' parentproxy="%s"\n' % xmlquoteattr(self['parentproxy']))
        f.write(' parentproxyuser="%s"\n' % xmlquoteattr(self['parentproxyuser']))
        f.write(' parentproxypass="%s"\n' % xmlquoteattr(self['parentproxypass']))
        f.write(' parentproxyport="%d"\n' % self['parentproxyport'])
        f.write(' timeout="%d"\n' % self['timeout'])
        f.write(' gui_theme="%s"\n' % xmlquoteattr(self['gui_theme']))
        f.write(' auth_ntlm="%d"\n' % self['auth_ntlm'])
        f.write(' try_google="%d"\n' % self['try_google'])
        hosts = self['nofilterhosts']
        f.write(' nofilterhosts="%s"\n'%xmlquoteattr(",".join(hosts)))
        hosts = self['allowedhosts']
        f.write(' allowedhosts="%s"\n'%xmlquoteattr(",".join(hosts)))
        f.write('>\n')
        for key in self['filters']:
            f.write('<filter name="%s"/>\n' % xmlquoteattr(key))
        f.write('</webcleaner>\n')
        f.close()


    def read_filterconf (self):
        """read filter rules"""
        from wc.filter.rules import generate_sids, recalc_up_down
        for filename in filterconf_files():
            if os.stat(filename)[ST_SIZE]==0:
                warn(PROXY, "Skipping empty file %r", filename)
                continue
            p = ZapperParser(filename, self)
            p.parse()
            self['folderrules'].append(p.folder)
        # sort folders according to oid
        self['folderrules'].sort()
        for i,folder in enumerate(self['folderrules']):
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
        assert folder.sid.startswith("wc")
        f = [ rule for rule in self['folderrules'] if rule.sid==folder.sid ]
        assert len(f) <= 1
        if f:
            chg = f[0].update(folder, dryrun=dryrun, log=log)
        else:
            chg = True
            print >>log, " ", i18n._("inserting %s")%folder.tiptext()
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
        import wc.filter
        self['filterlist'] = [[],[],[],[],[],[],[],[],[],[]]
        self['mime_content_rewriting'] = Set()
        for filtername in self['filters']:
            exec "from filter import %s" % filtername
            # filter class has same name as module
            clazz = getattr(getattr(wc.filter, filtername), filtername)
            # add content-rewriting mime types to special list
            if filtername in ['Rewriter', 'Replacer', 'GifImage',
                              'Compress', 'ImageReducer', 'ImageSize']:
                self['mime_content_rewriting'].update(clazz.mimelist)
            instance = clazz()
            for order in clazz.orders:
                for folder in self['folderrules']:
                    if folder.disable: continue
                    for rule in folder.rules:
                        if rule.disable: continue
                        if rule.get_name() in clazz.rulenames:
                            instance.addrule(rule)
                self['filterlist'][order].append(instance)
        for filters in self['filterlist']:
            # see Filter.__cmp__ on how sorting is done
            filters.sort()


    def nofilter (self, url):
        """Decide whether to filter this url or not.
           returns True if the request must not be filtered, else False
        """
        return match_url(url, self['nofilterhosts'])


    def allowed (self, host):
        """return True if the host is allowed for proxying, else False"""
        hostset = self['allowedhostset']
        return ip.host_in_set(host, hostset[0], hostset[1])


##### xml parsers #########

rulenames = (
  'rewrite',
  'block',
  'blockurls',
  'blockdomains',
  'allowurls',
  'allowdomains',
  'allow',
  'header',
  'image',
  'nocomments',
  'javascript',
  'replace',
  'rating'
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

import wc.filter


def make_xmlparser ():
    """return a new xml parser object"""
    # note: this parser returns unicode strings
    return xml.parsers.expat.ParserCreate()


class ParseException (Exception): pass


class BaseParser (object):
    def __init__ (self, filename, _config):
        self.filename = filename
        self.config = _config


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
        debug(PROXY, "Parsing %s", self.filename)
        if fp is None:
            fp = file(self.filename)
        self._preparse()
        try:
            try:
                self.xmlparser.ParseFile(fp)
            except (xml.parsers.expat.ExpatError, ParseException):
                exception(PROXY, "Error parsing %s", self.filename)
                raise SystemExit("parse error in %s"%self.filename)
        finally:
            self._postparse()


    def start_element (self, name, attrs):
        # all strings are unicode, but internal representation of
        # rule data has to be in ConfigCharset
        newattrs = attrs.copy()
        attrs.clear()
        for key,value in newattrs.items():
            attrs[key.encode(ConfigCharset)] = value.encode(ConfigCharset)


    def end_element (self, name):
        pass


    def character_data (self, data):
        pass


class ZapperParser (BaseParser):
    def __init__ (self, filename, _config, compile_data=True):
        super(ZapperParser, self).__init__(filename, _config)
        from wc.filter.rules import FolderRule
        self.folder = FolderRule(filename=filename)
        self.cmode = None
        self.rule = None
        self.compile_data = compile_data


    def start_element (self, name, attrs):
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
        elif name=='folder':
            self.folder.fill_attrs(attrs, name)
        else:
            raise ParseException, i18n._("unknown tag name %s")%name


    def end_element (self, name):
        self.cmode = None
        if self.rule is None:
            self.folder.end_data(name)
        else:
            self.rule.end_data(name)
        if name in rulenames:
            if self.compile_data:
                self.rule.compile_data()
        elif name=='folder':
            if self.compile_data:
                self.folder.compile_data()


    def character_data (self, data):
        if self.cmode:
            if self.rule is None:
                self.folder.fill_data(data, self.cmode)
            else:
                self.rule.fill_data(data, self.cmode)


class WConfigParser (BaseParser):
    def start_element (self, name, attrs):
        if name=='webcleaner':
            for key,val in attrs.items():
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
                self.config['allowedhostset'] = ip.hosts2map(hosts)
            else:
                self.config['allowedhosts'] = []
                self.config['allowedhostset'] = [Set(), []]
        elif name=='filter':
            debug(FILTER, "enable filter module %s", attrs['name'])
            self.config['filters'].append(attrs['name'])


from log import *
from url import match_url
