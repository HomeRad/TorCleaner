"""configuration data"""
# -*- coding: iso-8859-1 -*-
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import os, sys, time, socket
import _webcleaner2_configdata as configdata
from glob import glob
from wc.XmlUtils import xmlify

Version = configdata.version
AppName = configdata.name
App = AppName+" "+Version
UserAgent = AppName+"/"+Version
Author =  configdata.author
HtmlAuthor = Author.replace(' ', '&nbsp;')
Copyright = "Copyright � 2000-2002 by "+Author
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

def iswriteable (fname):
    if os.path.isdir(fname) or os.path.islink(fname):
        return False
    try:
        if os.path.exists(fname):
            f = file(fname, 'a')
            f.close()
            return True
        else:
            f = file(fname, 'w')
            f.close()
            os.remove(fname)
            return True
    except IOError, msg:
        pass
    return False


import ip, i18n
from log import *

config = None

def startfunc (handle=None):
    # init logging
    initlog(os.path.join(ConfigDir, "logging.conf"))
    # we run single-threaded, decrease check interval
    sys.setcheckinterval(500)
    # support reload on posix systems
    if os.name=='posix':
        import signal
        signal.signal(signal.SIGHUP, reload_config)
        # drop privileges
        os.chdir("/")
        # for web configuration, we cannot drop privileges
        #if os.geteuid()==0:
        #    import pwd, grp
        #    try:
        #        pentry = pwd.getpwnam("nobody")
        #        pw_uid = 2
        #        nobody = pentry[pw_uid]
        #        gentry = grp.getgrnam("nogroup")
        #        gr_gid = 2
        #        nogroup = gentry[gr_gid]
        #        os.setgid(nogroup)
        #        os.setuid(nobody)
        #    except KeyError:
        #        warn(WC, "could not drop root privileges, user nobody "+\
        #                 "and/or group nogroup not found")
        #        pass
    # read configuration
    global config
    config = Configuration()
    config.init_filter_modules()
    # start the proxy
    import wc.proxy
    wc.proxy.mainloop(handle=handle)


# reload configuration
def reload_config (signum, frame):
    global config
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


import wc.filter


def proxyconf_file ():
    """return proxy configuration filename"""
    return os.path.join(ConfigDir, "webcleaner.conf")


def filterconf_files ():
    """return list of filter configuration filenames"""
    return glob(os.path.join(ConfigDir, "*.zap"))


# available filter modules
filtermodules = ["Header", "Blocker", "GifImage", "ImageReducer",
                 "BinaryCharFilter", "Rewriter", "Replacer", "Compress", ]

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

    def reset (self):
        """Reset to default values"""
        self['port'] = 8080
        self['proxyuser'] = ""
        self['proxypass'] = ""
        self['parentproxy'] = ""
        self['parentproxyport'] = 3128
        self['parentproxyuser'] = ""
        self['parentproxypass'] = ""
        self['strict_whitelist'] = 0
        self['rules'] = []
        self['filters'] = []
        self['filterlist'] = [[],[],[],[],[],[],[],[],[],[]]
        self['colorize'] = 0
        self['noproxyfor'] = None
        self['allowedhosts'] = None
        self['starttime'] = time.time()
        self['requests'] = {'valid':0, 'error':0, 'blocked':0}
        self['local_sockets_only'] = 0
        self['localhosts'] = get_localhosts()
        self['mime_content_rewriting'] = []
        self['headersave'] = 100
        self['showerrors'] = 0
        self['webgui_theme'] = "classic"
        self['timeout'] = 30


    def read_proxyconf (self):
        """read proxy configuration"""
        p = WConfigParser()
        p.parse(proxyconf_file(), self)


    def write_proxyconf (self):
        """write proxy configuration"""
        f = file(proxyconf_file(), 'w')
        f.write("""<?xml version="1.0"?>
<!DOCTYPE webcleaner SYSTEM "webcleaner.dtd">
<webcleaner
""")
        f.write(' version="%s"\n' % xmlify(self['version']))
        f.write(' port="%d"\n' % self['port'])
        f.write(' proxyuser="%s"\n' % xmlify(self['proxyuser']))
        f.write(' proxypass="%s"\n' % xmlify(self['proxypass']))
        if self['parentproxy']:
            f.write(' parentproxy="%s"\n' % xmlify(self['parentproxy']))
        f.write(' parentproxyuser="%s"\n' % xmlify(self['parentproxyuser']))
        f.write(' parentproxypass="%s"\n' % xmlify(self['parentproxypass']))
        f.write(' parentproxyport="%d"\n' % self['parentproxyport'])
        if self['showerrors']:
            f.write(' showerrors="1"\n')
        if self['timeout']:
            f.write(' timeout="%d"\n' % self['timeout'])
        f.write(' webgui_theme="%s"\n' % xmlify(self['webgui_theme']))
        if self['noproxyfor']:
            keys = self['noproxyfor'][2].keys()
            keys.sort()
            f.write(' noproxyfor="%s"\n'%xmlify(",".join(keys)))
        if self['allowedhosts']:
            keys = self['allowedhosts'][2].keys()
            keys.sort()
            f.write(' allowedhosts="%s"\n'%xmlify(",".join(keys)))
        f.write('>\n')
        for key in self['filters']:
            f.write('<filter name="%s"/>\n' % key)
        f.write('</webcleaner>\n')
        f.close()


    def read_filterconf (self):
        """read filter rules"""
        # filter configuration
        for f in filterconf_files():
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
  'javascript',
  'replacer',
  'pics'
)
_nestedtags = (
  # rewriter rule nested tag names
  'attr','enclosed','replace',
  # PICS rule nested tag names
  'url', 'service','category',
)

class ParseException (Exception): pass

class BaseParser:
    def parse (self, filename, config):
        debug(WC, "Parsing %s", filename)
        self.p = xml.parsers.expat.ParserCreate("ISO-8859-1")
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
            for key in ('port', 'parentproxyport', 'timeout',
	                'colorize', 'showerrors', 'strict_whitelist'):
                self.config[key] = int(self.config[key])
            for key in ('version', 'parentproxy', 'proxyuser',
                        'proxypass', 'parentproxyuser', 'parentproxypass',
                        'webgui_theme',
                        ):
                if self.config[key] is not None:
                    self.config[key] = str(self.config[key])
            if self.config['noproxyfor'] is not None:
                strhosts = str(self.config['noproxyfor'])
                self.config['noproxyfor'] = ip.host_set(strhosts)
            else:
                self.config['noproxyfor'] = [{}, [], {}]
            if self.config['allowedhosts'] is not None:
                strhosts = str(self.config['allowedhosts'])
                self.config['allowedhosts'] = ip.host_set(strhosts)
            else:
                self.config['allowedhosts'] = [{}, [], {}]
        elif name=='filter':
            debug(FILTER, "enable filter module %s", attrs['name'])
            self.config['filters'].append(attrs['name'])

