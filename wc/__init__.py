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
import xml.parsers.expat
import _webcleaner2_configdata as configdata
from glob import glob
from sets import Set
from cStringIO import StringIO

Version = configdata.version
AppName = configdata.appname
Name = configdata.name
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
BaseUrl = "http://webcleaner.sourceforge.net/zapper/"
#BaseUrl = "http://localhost/~calvin/webcleaner.sf.net/htdocs/test/"

from XmlUtils import xmlify, unxmlify

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
    except IOError:
        pass
    return False


def sort_seq (seq):
    """return sorted list of given sequence"""
    l = list(seq)
    l.sort()
    return l


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
    from wc.proxy import mainloop
    mainloop(handle=handle)


def reload_config (*dummy):
    """reload configuration function with dummy params for (signum, frame)
    from the signal handler prototype
    """
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


def proxyconf_file ():
    """return proxy configuration filename"""
    return os.path.join(ConfigDir, "webcleaner.conf")


def filterconf_files ():
    """return list of filter configuration filenames"""
    return glob(os.path.join(ConfigDir, "*.zap"))


def encode_string (s):
    return s.decode("utf8").encode(ConfigCharset)


def encode_values (d):
    for key,val in d.items():
        key = encode_string(key)
        val = encode_string(val)
        d[key] = val


# available filter modules
filtermodules = ["Header", "Blocker", "GifImage", "ImageSize", "ImageReducer",
                 "BinaryCharFilter", "Rewriter", "Replacer", "Compress", ]
filtermodules.sort()

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
        if self['timeout']:
            socket.setdefaulttimeout(self['timeout'])
        else:
            socket.setdefaulttimeout(None)


    def reset (self):
        """Reset to default values"""
        self['port'] = 8080
        self['proxyuser'] = ""
        self['proxypass'] = ""
        self['parentproxy'] = ""
        self['parentproxyport'] = 3128
        self['parentproxyuser'] = ""
        self['parentproxypass'] = ""
        # dynamically stored parent proxy authorization credentials
        self['parentproxycreds'] = None
        self['strict_whitelist'] = 0
        self['folderrules'] = []
        self['filters'] = []
        self['filterlist'] = [[],[],[],[],[],[],[],[],[],[]]
        self['colorize'] = 0
        self['nofilterhosts'] = None
        # DNS resolved nofilterhosts
        self['allowedhosts'] = None
        self['starttime'] = time.time()
        self['requests'] = {'valid':0, 'error':0, 'blocked':0}
        self['local_sockets_only'] = 0
        self['localhosts'] = get_localhosts()
        self['mime_content_rewriting'] = Set()
        self['showerrors'] = 0
        self['gui_theme'] = "classic"
        self['timeout'] = 30


    def read_proxyconf (self):
        """read proxy configuration"""
        filename = proxyconf_file()
        WConfigParser(filename).parse(file(filename), self)


    def write_proxyconf (self):
        """write proxy configuration"""
        f = file(proxyconf_file(), 'w')
        f.write("""<?xml version="1.0" encoding="%s"?>
<!DOCTYPE webcleaner SYSTEM "webcleaner.dtd">
<webcleaner
""" % ConfigCharset)
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
        f.write(' timeout="%d"\n' % self['timeout'])
        f.write(' gui_theme="%s"\n' % xmlify(self['gui_theme']))
        hosts = sort_seq(ip.map2hosts(self['nofilterhosts']))
        f.write(' nofilterhosts="%s"\n'%xmlify(",".join(hosts)))
        hosts = sort_seq(ip.map2hosts(self['allowedhosts']))
        f.write(' allowedhosts="%s"\n'%xmlify(",".join(hosts)))
        f.write('>\n')
        for key in self['filters']:
            f.write('<filter name="%s"/>\n' % key)
        f.write('</webcleaner>\n')
        f.close()


    def read_filterconf (self):
        """read filter rules"""
        # filter configuration
        for filename in filterconf_files():
            p = ZapperParser(filename)
            p.parse(file(filename), self)
            self['folderrules'].append(p.folder)
        self.sort()


    def sort (self):
        """sort rules"""
        from filter.rules.FolderRule import recalc_oids, recalc_up_down
        for f in self['folderrules']:
            f.sort()
        self['folderrules'].sort()
        recalc_oids(self['folderrules'])
        recalc_up_down(self['folderrules'])


    def merge_folder (self, folder, dryrun=False, log=None):
        """merge given folder data into config
        return True if something has changed
        """
        # test for correct category
        assert folder.sid.startswith("wc")
        f = [ rule for rule in self['folderrules'] if rule.sid==folder.sid ]
        if f:
            chg = f[0].update(folder, dryrun=dryrun, log=log)
        else:
            chg = True
            print >>log, "inserting", folder.tiptext()
            if not dryrun:
                self['folderrules'].append(folder)
        return chg


    def write_filterconf (self):
        """write filter rules"""
        for folder in self['folderrules']:
            f = file(folder.filename, 'w')
            f.write(folder.toxml())
            f.close()


    def init_filter_modules (self):
        """go through list of rules and store them in the filter
        objects. This will also compile regular expression strings
        to regular expression objects"""
        import wc.filter
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
        self.sort_filter_modules()


    def sort_filter_modules (self):
        for l in self['filterlist']:
            # see Filter.__cmp__ on how sorting is done
            l.sort()


    def nofilter (self, url):
        """Decide whether to filter this url or not.
           returns True if the request must not be filtered, else False
        """
        return match_url(url, self['nofilterhosts'])


    def allowed (self, host):
        """return True if the host is allowed for proxying, else False"""
        return match_host(host, self['allowedhosts'])


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
  'pics'
)
_nestedtags = (
  # rewriter rule nested tag names
  'attr','enclosed','replacement',
  # PICS rule nested tag names
  'url', 'service','category',
)

class ParseException (Exception): pass

class BaseParser (object):
    def __init__ (self, filename):
        self.p = xml.parsers.expat.ParserCreate()
        self.p.returns_unicode = 0
        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.character_data
        self.filename = filename


    def parse (self, fp, _config):
        self.config = _config
        debug(WC, "Parsing %s", self.filename)
        try:
            self.p.ParseFile(fp)
        except xml.parsers.expat.ExpatError:
            error(WC, "Error parsing %s", self.filename)
            raise


    def start_element (self, name, attrs):
        pass


    def end_element (self, name):
        pass


    def character_data (self, data):
        pass


class ZapperParser (BaseParser):
    def __init__ (self, filename):
        super(ZapperParser, self).__init__(filename)
        from wc.filter.rules import FolderRule
        self.folder = FolderRule.FolderRule(filename=filename)
        self.cmode = None
        self.rule = None


    def start_element (self, name, attrs):
        encode_values(attrs)
        self.cmode = name
        if name=='folder':
            self.folder.fill_attrs(attrs, name)
        elif name in rulenames:
            import wc.filter
            self.rule = wc.filter.GetRuleFromName(name)
            self.rule.fill_attrs(attrs, name)
            self.folder.append_rule(self.rule)
        # tag has character data
        elif name in _nestedtags:
            self.rule.fill_attrs(attrs, name)
        else:
            raise ParseException, i18n._("unknown tag name %s")%name


    def end_element (self, name):
        self.cmode = None
        if name=='rewrite':
            self.rule.set_start_sufficient()
        if name in rulenames:
            assert self.rule.sid is not None


    def character_data (self, data):
        if self.cmode and self.rule:
            self.rule.fill_data(data, self.cmode)


class WConfigParser (BaseParser):
    def parse (self, fp, _config):
        super(WConfigParser, self).parse(fp, _config)
        self.config['configfile'] = self.filename
        self.config['filters'].sort()


    def start_element (self, name, attrs):
        if name=='webcleaner':
            for key,val in attrs.items():
                self.config[key] = unxmlify(val)
            for key in ('port', 'parentproxyport', 'timeout',
	                'colorize', 'showerrors', 'strict_whitelist'):
                self.config[key] = int(self.config[key])
            if self.config['nofilterhosts'] is not None:
                strhosts = self.config['nofilterhosts']
                self.config['nofilterhosts'] = ip.strhosts2map(strhosts)
            else:
                self.config['nofilterhosts'] = [Set(), []]
            if self.config['allowedhosts'] is not None:
                strhosts = self.config['allowedhosts']
                self.config['allowedhosts'] = ip.strhosts2map(strhosts)
            else:
                self.config['allowedhosts'] = [Set(), []]
        elif name=='filter':
            debug(FILTER, "enable filter module %s", attrs['name'])
            self.config['filters'].append(attrs['name'])


from log import *
import ip, i18n
from wc.proxy import match_url, match_host
