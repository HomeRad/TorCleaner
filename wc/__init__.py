"""configuration data"""
# Copyright (C) 2000-2003  Bastian Kleineidam
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
import os, re, sys, UserDict, time, socket, ip, i18n
import _webcleaner2_configdata as configdata
from debug import *
sys.setcheckinterval(100)

Version = configdata.version
AppName = configdata.name
App = AppName+" "+Version
UserAgent = AppName+"/"+Version
Author =  configdata.author
HtmlAuthor = Author.replace(' ', '&nbsp;')
Copyright = "Copyright © 2000-2002 by "+Author
HtmlCopyright = "Copyright &copy; 2000-2002 by "+HtmlAuthor
AppInfo = App+"              "+Copyright
HtmlAppInfo = App+", "+HtmlCopyright
Url = configdata.url
Email = configdata.author_email
Freeware = AppName+""" comes with ABSOLUTELY NO WARRANTY!
This is free software, and you are welcome to redistribute it
under certain conditions. Look at the file `LICENSE' whithin this
distribution."""
ConfigDir = configdata.config_dir
TemplateDir = configdata.template_dir
LocaleDir = os.path.join(configdata.install_data, 'locale')

def remove_headers (headers, to_remove):
    """utility function to remove entries from RFC822 headers"""
    for h in to_remove:
        if headers.has_key(h):
            #debug(BRING_IT_ON, "remove header", `h`)
            del headers[h]

config = None

def startfunc ():
    # support reload on posix systems
    if os.name=='posix':
        import signal
        signal.signal(signal.SIGHUP, reload_config)
    # drop root privileges
    if os.geteuid()==0:
        import pwd, grp
        try:
            pentry = pwd.getpwnam("nobody")
            pw_uid = 2
            nobody = pentry[pw_uid]
            gentry = grp.getgrnam("nogroup")
            gr_gid = 2
            nogroup = gentry[gr_gid]
            os.setgid(nogroup)
            os.setuid(nobody)
        except KeyError:
            print >>sys.stderr, "warning: could not drop root privileges, user nobody and/or group nogroup not found"
            pass
    # read configuration
    global config
    config = Configuration()
    config.init_filter_modules()
    # start the proxy
    import wc.proxy
    wc.proxy.mainloop()

# reload configuration
def reload_config (signum, frame):
    global config
    config.reset()
    config.read_proxyconf()
    config.read_filterconf()
    config.init_filter_modules()

import wc.filter

class Configuration (UserDict.UserDict):
    """hold all configuration data, inclusive filter rules"""

    def __init__ (self):
        """Initialize the options"""
        UserDict.UserDict.__init__(self)
        # reset to default
        self.reset()
        # read configuration
        self.read_proxyconf()
        self.read_filterconf()

    def reset (self):
        """Reset to default values"""
        self['port'] = 8080
        self['proxyuser'] = ""
        self['proxypass'] = ""
        self['parentproxy'] = ""
        self['parentproxyport'] = 3128
        self['parentproxyuser'] = ""
        self['parentproxypass'] = ""
        self['logfile'] = ""
        self['strict_whitelist'] = 0
        self['debuglevel'] = 0
        self['rules'] = []
        self['filters'] = []
        self['filterlist'] = [[],[],[],[],[],[],[],[],[],[]]
        self['colorize'] = 0
        self['noproxyfor'] = {}
        self['allowedhosts'] = {}
        self['starttime'] = time.time()
        self['requests'] = {'valid':0, 'error':0, 'blocked':0}
        self['local_sockets_only'] = 0
        self['localip'] = socket.gethostbyname(socket.gethostname())
        self['mime_content_rewriting'] = []
        self['headersave'] = 100
        self['showerrors'] = None

    def read_proxyconf (self):
        """read proxy configuration"""
        p = WConfigParser()
        p.parse(os.path.join(ConfigDir, "webcleaner.conf"), self)
        global DebugLevel
        DebugLevel = self['debuglevel']

    def read_filterconf (self):
        """read filter rules"""
        from glob import glob
        # filter configuration
        for f in glob(os.path.join(ConfigDir, "*.zap")):
            #debug(BRING_IT_ON, "parsing", f)
            ZapperParser().parse(f, self)
        for f in self['rules']:
            f.sort()
        self['rules'].sort()
        filter.rules.FolderRule.recalc_oids(self['rules'])

    def init_filter_modules (self):
        """go through list of rules and store them in the filter
        objects. This will also compile regular expression strings
        to regular expression objects"""
        for f in self['filters']:
            exec "from filter import %s" % f
            _module = getattr(wc.filter, f)
            # add content-rewriting mime types to special list
            if f in ('Rewriter', 'Replacer', 'GifImage', 'Compress'):
                for mime in getattr(_module, "mimelist"):
                    if mime not in self['mime_content_rewriting']:
                        self['mime_content_rewriting'].append(mime)
            # class has same name as module
            instance = getattr(_module, f)(getattr(_module, "mimelist"))
            for order in getattr(_module, 'orders'):
                for rules in self['rules']:
                    if rules.disable: continue
                    for rule in rules.rules:
                        if rule.disable: continue
                        if rule.get_name() in getattr(_module, 'rulenames'):
                            instance.addrule(rule)
                self['filterlist'][order].append(instance)

    def __repr__ (self):
        return i18n._("""
WebCleaner Configuration
========================

Port:          %(port)d
Parent proxy:  %(parentproxy)s
Logfile:       %(logfile)s
Debug level:   %(debuglevel)d
Show errors:   %(showerrors)d
Headers saved: %(headersave)d

""") % self

##### xml parsers #########
import xml.parsers.expat
from XmlUtils import unxmlify

_rulenames = (
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
  'replacer')
_nestedtags = ('attr','enclosed','replace')

class ParseException (Exception): pass

class BaseParser:
    def parse (self, filename, config):
        #debug(HURT_ME_PLENTY, "Parsing "+filename)
        self.p = xml.parsers.expat.ParserCreate()
        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.character_data
        self.reset()
        self.config = config
        self.p.ParseFile(open(filename))

    def start_element (self, name, attrs):
        pass
    def end_element (self, name):
        pass
    def character_data (self, data):
        pass
    def reset (self):
        pass


class ZapperParser (BaseParser):
    def parse (self, filename, config):
        BaseParser.parse(self, filename, config)
        self.rules.filename = filename
        config['rules'].append(self.rules)

    def start_element (self, name, attrs):
        self.cmode = name
        if name=='folder':
            self.rules.fill_attrs(attrs, name)
        elif name in _rulenames:
            self.rule = wc.filter.GetRuleFromName(name)
            self.rule.fill_attrs(attrs, name)
            self.rules.append_rule(self.rule)
        # tag has character data
        elif name in _nestedtags:
            self.rule.fill_attrs(attrs, name)
        else:
            raise ParseException, i18n._("unknown tag name %s")%name

    def end_element (self, name):
        self.cmode = None
        if name in _rulenames:
            if name=='rewrite':
                self.rule.set_start_sufficient()

    def character_data (self, data):
        if self.cmode and self.rule:
            self.rule.fill_data(data, self.cmode)

    def reset (self):
        from wc.filter.rules import FolderRule
        self.rules = FolderRule.FolderRule()
        self.cmode = None
        self.rule = None


class WConfigParser (BaseParser):
    def parse (self, filename, config):
        BaseParser.parse(self, filename, config)
        self.config['configfile'] = filename

    def start_element (self, name, attrs):
        if name=='webcleaner':
            for key,val in attrs.items():
                self.config[str(key)] = unxmlify(val)
            for key in ('port','parentproxyport',
	                'debuglevel','colorize','showerrors',
                        'strict_whitelist'):
                self.config[key] = int(self.config[key])
            for key in ('version', 'parentproxy', 'logfile', 'proxyuser',
                        'proxypass', 'parentproxyuser', 'parentproxypass',
                        ):
                if self.config[key] is not None:
                    self.config[key] = str(self.config[key])
            if self.config['noproxyfor']:
                strhosts = str(self.config['noproxyfor'])
                self.config['noproxyfor'] = host_set(strhosts)
            if self.config['allowedhosts']:
                strhosts = str(self.config['allowedhosts'])
                self.config['allowedhosts'] = host_set(strhosts)
            if self.config['logfile'] == '<stdout>':
                self.config['logfile'] = sys.stdout
            elif self.config['logfile']:
                self.config['logfile'] = open(self.config['logfile'], 'a')
        elif name=='filter':
            #debug(BRING_IT_ON, "enable filter module %s" % attrs['name'])
            self.config['filters'].append(attrs['name'])


def host_set (strhosts):
    hosts = [s.strip() for s in strhosts.split(",")]
    ret = []
    ret.extend(ip.host_map(hosts))
    dict = {}
    for h in hosts:
        dict[h] = None
    ret.append(dict)
    return ret
