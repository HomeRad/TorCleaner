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

import os
import time
import socket
import glob
import sets
import stat
import xml.parsers.expat
import logging.config
import logging.handlers
import _webcleaner2_configdata as configdata
import log

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

# logger areas
LOG_FILTER = "wc.filter"
LOG_CONNECTION = "wc.connection"
LOG_PROXY = "wc.proxy"
LOG_AUTH = "wc.proxy.auth"
LOG_DNS = "wc.proxy.dns"
LOG_GUI = "wc.gui"
LOG_ACCESS = "wc.access"
LOG_RATING = "wc.rating"


def initlog (filename, appname):
    """initialize logfiles and configuration"""
    trydirs = []
    if os.environ.get("WC_DEVELOPMENT"):
        trydirs.append(os.getcwd())
    logging.config.fileConfig(filename)
    logname = "%s.log"%appname
    logfile = log.get_log_file(appname, logname, trydirs=trydirs)
    handler = get_wc_handler(logfile)
    logging.getLogger("wc").addHandler(handler)
    logging.getLogger("simpleTAL").addHandler(handler)
    logging.getLogger("simpleTALES").addHandler(handler)
    # access log is always a file
    logname = "%s-access.log"%appname
    logfile = log.get_log_file(appname, logname, trydirs=trydirs)
    handler = get_access_handler(logfile)
    logging.getLogger("wc.access").addHandler(handler)


def get_wc_handler (logfile):
    """return a handler for webcleaner logging"""
    mode = 'a'
    maxBytes = 1024*1024*2 # 2 MB
    backupCount = 5 # number of files to generate
    handler = logging.handlers.RotatingFileHandler(logfile, mode, maxBytes, backupCount)
    return log.set_format(handler)


def get_access_handler (logfile):
    """return a handler for access logging"""
    mode = 'a'
    maxBytes = 1024*1024*2 # 2 MB
    backupCount = 5 # number of files to generate
    handler = logging.handlers.RotatingFileHandler(logfile, mode, maxBytes, backupCount)
    # log only the message
    handler.setFormatter(logging.Formatter("%(message)s"))
    return handler



def sort_seq (seq):
    """return sorted list of given sequence"""
    l = list(seq)
    l.sort()
    return l

import wc.ip
import wc.i18n
import wc.url
import wc.network
import wc.proxy
import wc.proxy.dns_lookups
import wc.filter
import wc.filter.VirusFilter

# set this to an empty dictionary so that webgui/context/*.py can
# safely set config values upon import
config = {}

def wstartfunc (handle=None, abort=None, confdir=ConfigDir):
    """Initalize configuration, start psyco compiling and the proxy loop.
       This function does not return until Ctrl-C is pressed."""
    global config
    # init logging
    initlog(os.path.join(confdir, "logging.conf"), Name)
    # read configuration
    config = Configuration(confdir=confdir)
    if abort is not None:
        abort(False)
    # support reload on posix systems
    elif os.name=='posix':
        import signal
        signal.signal(signal.SIGHUP, sighup_reload_config)
        # change dir to avoid open files on umount
        os.chdir("/")
    config.init_filter_modules()
    wc.filter.VirusFilter.init_clamav_conf()
    # psyco library for speedup
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    # start the proxy
    log.info(LOG_PROXY, "Starting proxy on port %d", config['port'])
    wc.proxy.mainloop(handle=handle, abort=abort)


def sighup_reload_config (signum, frame):
    """store timer for reloading configuration data"""
    wc.proxy.make_timer(1, reload_config)


def reload_config ():
    """reload configuration"""
    config.reset()
    config.read_proxyconf()
    config.read_filterconf()
    config.init_filter_modules()
    wc.proxy.dns_lookups.init_dns_resolver()
    wc.filter.VirusFilter.init_clamav_conf()


def proxyconf_file (confdir):
    """return proxy configuration filename"""
    return os.path.join(confdir, "webcleaner.conf")


def filterconf_files (dirname):
    """return list of filter configuration filenames"""
    return glob.glob(os.path.join(dirname, "*.zap"))


# available filter modules
filtermodules = ["Header", "Blocker", "GifImage", "ImageSize", "ImageReducer",
                 "BinaryCharFilter", "Rewriter", "Replacer", "Compress",
                 "RatingHeader", "VirusFilter",
                ]
filtermodules.sort()

from wc.XmlUtils import xmlquote, xmlquoteattr

class Configuration (dict):
    """hold all configuration data, inclusive filter rules"""

    def __init__ (self, confdir=ConfigDir):
        """Initialize the options"""
        dict.__init__(self)
        self.configfile = proxyconf_file(confdir)
        self.filterdir = confdir
        # reset to default values
        self.reset()
        # read configuration
        self.read_proxyconf()
        self.read_filterconf()
        if self['development']:
            # avoid conflicting servers if an official WebCleaner release
            # is installed by incrementing port numbers
            self['port'] += 1
            self['sslport'] += 1
            # test data directory url
            self['baseurl'] = "file:///home/calvin/projects/webcleaner/test/"


    def reset (self):
        """Reset to default values"""
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
        self['localhosts'] = wc.network.get_localhosts()
        self['mime_content_rewriting'] = sets.Set()
        self['gui_theme'] = "classic"
        self['timeout'] = 10
        self['auth_ntlm'] = 0
        if os.name=='posix':
            self['clamavconf'] = "/etc/clamav/clamav.conf"
        elif os.name=='nt':
            self['clamavconf'] = r"c:\clamav-devel\etc\clamav.conf"
        else:
            self['clamavconf'] = os.path.join(os.getcwd(), "clamav.conf")
        # in development mode some values have different defaults
        self['development'] = os.environ.get("WC_DEVELOPMENT", 0)
        self['baseurl'] = Url
        self['try_google'] = 0
        # delete all registered sids
        from wc.filter.rules import delete_registered_sids
        delete_registered_sids()


    def read_proxyconf (self):
        """read proxy configuration"""
        WConfigParser(self.configfile, self).parse()


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
        f.write(' clamavconf="%s"\n' % xmlquoteattr(self['clamavconf']))
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
        from wc.filter.rules import generate_sids
        from wc.filter.rules.FolderRule import recalc_up_down
        for filename in filterconf_files(self.filterdir):
            if os.stat(filename)[stat.ST_SIZE]==0:
                log.warn(LOG_PROXY, "Skipping empty file %r", filename)
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
            print >>log, " ", wc.i18n._("inserting %s")%folder.tiptext()
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
        self['filterlist'] = [[],[],[],[],[],[],[],[],[],[]]
        self['mime_content_rewriting'] = sets.Set()
        for filtername in self['filters']:
            # import filter module
            exec "from filter import %s" % filtername
            # filter class has same name as module
            clazz = getattr(getattr(wc.filter, filtername), filtername)
            # add content-rewriting mime types to special list
            if filtername in ['Rewriter', 'Replacer', 'GifImage',
                              'Compress', 'ImageReducer', 'ImageSize',
                              'VirusFilter']:
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
        return wc.url.match_url(url, self['nofilterhosts'])


    def allowed (self, host):
        """return True if the host is allowed for proxying, else False"""
        hostset = self['allowedhostset']
        return wc.ip.host_in_set(host, hostset[0], hostset[1])


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
        log.debug(LOG_PROXY, "Parsing %s", self.filename)
        if fp is None:
            fp = file(self.filename)
        self._preparse()
        try:
            try:
                self.xmlparser.ParseFile(fp)
            except (xml.parsers.expat.ExpatError, ParseException):
                log.exception(LOG_PROXY, "Error parsing %s", self.filename)
                raise SystemExit("parse error in %s"%self.filename)
        finally:
            self._postparse()


    def start_element (self, name, attrs):
        pass


    def end_element (self, name):
        pass


    def character_data (self, data):
        pass


class ZapperParser (BaseParser):
    """parser class for *.zap filter configuration files"""

    def __init__ (self, filename, _config, compile_data=True):
        super(ZapperParser, self).__init__(filename, _config)
        from wc.filter.rules.FolderRule import FolderRule
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
            raise ParseException, wc.i18n._("unknown tag name %s")%name


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
    """parser class for webcleaner.conf configuration files"""

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
                self.config['allowedhostset'] = wc.ip.hosts2map(hosts)
            else:
                self.config['allowedhosts'] = []
                self.config['allowedhostset'] = [sets.Set(), []]
        elif name=='filter':
            log.debug(LOG_FILTER, "enable filter module %s", attrs['name'])
            self.config['filters'].append(attrs['name'])


