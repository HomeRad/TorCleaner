"""configuration data"""
# Copyright (C) 2000,2001  Bastian Kleineidam
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

import _webcleaner_configdata,os,sys,UserDict
from string import ljust,rjust,replace,join

Version = _webcleaner_configdata.version
AppName = _webcleaner_configdata.name
App = AppName+" "+Version
UserAgent = AppName+"/"+Version
Author =  _webcleaner_configdata.author
HtmlAuthor = replace(Author, ' ', '&nbsp;')
Copyright = "Copyright � 2000,2001 by "+Author
HtmlCopyright = "Copyright &copy; 2000,2001 by "+HtmlAuthor
AppInfo = App+"              "+Copyright
HtmlAppInfo = App+", "+HtmlCopyright
Url = _webcleaner_configdata.url
Email = _webcleaner_configdata.author_email
Freeware = AppName+""" comes with ABSOLUTELY NO WARRANTY!
This is free software, and you are welcome to redistribute it
under certain conditions. Look at the file `LICENSE' whithin this
distribution."""
ConfigVersion = "0.7"
ConfigDir = _webcleaner_configdata.config_dir
LocaleDir = os.path.join(_webcleaner_configdata.install_data, 'locale')
DebugLevel = 0
Colorize = 0

if Colorize:
    def color(text, col=None, bgcol=None):
        if (col is not None) and os.environ.get('TERM'):
            if bgcol is not None:
                col = '%s;4%s' % (col, bgcol)
            return '\033[3%sm%s\033[0m' % (col, text)
        else:
            return text
else:
    def color(text, col=None, bgcol=None):
        return text


def message(labelcolor=0, label='info', field1=None, field2=None, *args):
    output = []
    labelwidth = 6
    if field1:
        labelwidth = 11
        if field2:
            labelwidth = 13
    output.append(color(ljust(label, labelwidth), labelcolor))
    if field1: output.append(rjust(str(field1), 5))
    output.append(' ')
    if field2: output.append(ljust(str(field2), 2))
    for a in args:
        output.append(' ')
        output.append(str(a))
    print join(output, '')

# debug function, using the debug level
def debug(s, level=1):
    if level <= DebugLevel:
        sys.stderr.write("DEBUG: %s\n" % s)

try:
    import fintl
    gettext = fintl.gettext
    domain = 'webcleaner'
    fintl.bindtextdomain(domain, LocaleDir)
    fintl.textdomain(domain)
except ImportError, msg:
    print msg
    def gettext(msg):
        return msg
# set _ as an alias for gettext
_ = gettext

def error(s):
    sys.stderr.write("error: %s\n" % s)


ErrorText = _("""<html><head>
<title>WebCleaner Proxy Error %d %s</title>
</head><body bgcolor="#fff7e5"><br><center><b>Bummer!</b><br>
WebCleaner Proxy Error %d %s<br>
%s<br></center></body></html>""")
ErrorLen = len(ErrorText)


from wc import proxy

def startfunc():
    if os.name=='posix':
        import signal
        signal.signal(signal.SIGHUP, configure)
    configure(None, None)
    proxy.mainloop()


# configuration
def configure(signum, frame):
    """The signum and frame args are needed for signal.signal()
       You can fill them with (None, None) values"""
    global _config
    _config = Configuration()
    proxy.configure(_config)


class Configuration(UserDict.UserDict):
    def __init__(self):
        """Initialize the options"""
        UserDict.UserDict.__init__(self)
        # reset to default
        self.reset()
        # read configuration
        self.read()

    def reset(self):
        """Reset to default values"""
        self['port'] = 8080
        self['parentproxy'] = None
        self['parentproxyport'] = 8080
        self['buffersize'] = 1024
        self['logfile'] = None
        self['timeout'] = 30
        self['obfuscateip'] = 0
        self['debuglevel'] = 0
        self['rules'] = []
        self['filters'] = []
        self['filterlist'] = [[],[],[],[],[],[],[],[],[],[]]
        self['errorlen'] = ErrorLen
        self['errortext'] = ErrorText
        self['colorize'] = 0

    def read(self):
        # proxy configuration
        p = WConfigParser()
        p.parse(os.path.join(ConfigDir, "webcleaner.conf"), self)
        global DebugLevel
        DebugLevel = self['debuglevel']
        from glob import glob
        # filter configuration
        for f in glob(os.path.join(ConfigDir, "*.zap")):
            ZapperParser().parse(f, self)

    def init_filtermodules(self):
        for f in self[u'filters']:
            exec "from filter import %s" % f
            _module = getattr(sys.modules['wc.filter'], f)
            for order in getattr(_module, 'orders'):
                instance = getattr(_module, f)()
                for rules in self[u'rules']:
                    if rules.disable: continue
                    for rule in rules.rules:
                        if rule.disable: continue
                        if rule.get_name() in getattr(_module, 'rulenames'):
                            instance.addrule(rule)
                self[u'filterlist'][order].append(instance)



##### xml parsers #########
import xml.parsers.expat
from wc.filter import Rules

_rulenames = ('rewrite','block','allow','header','image','nocomments')
_nestedtags = ('attr','enclosed','replace')
_plaindatatags = ('replace',)

class ParseException(Exception): pass

class BaseParser:
    def parse(self, filename, config):
        debug("Parsing "+filename)
        self.p = xml.parsers.expat.ParserCreate()
        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.character_data
        self.reset()
        self.config = config
        self.p.ParseFile(open(filename))

    def start_element(self, name, attrs):
        pass
    def end_element(self, name):
        pass
    def character_data(self, data):
        pass
    def reset(self):
        pass


class ZapperParser(BaseParser):
    def parse(self, filename, config):
        BaseParser.parse(self, filename, config)
        self.rules.filename = filename
        config['rules'].append(self.rules)

    def start_element(self, name, attrs):
        self.cmode = name
        if name=='folder':
            self.rules.fill_attrs(attrs, name)
        elif name in _rulenames:
            self.rule = filter.GetRuleFromName(name)
            self.rule.fill_attrs(attrs, name)
            self.rules.append_rule(self.rule)
        # tag has character data
        elif name in _nestedtags:
            self.rule.fill_attrs(attrs, name)
        else:
            raise ParseException, "unknown tag name %s"%name

    def end_element(self, name):
        self.cmode = None
        if name in _rulenames:
            if name=='rewrite':
                self.rule.set_start_sufficient()

    def character_data(self, data):
        if self.cmode and self.rule:
            self.rule.fill_data(data, self.cmode)

    def reset(self):
        self.rules = Rules.FolderRule()
        self.cmode = None
        self.rule = None


class WConfigParser(BaseParser):
    def parse(self, filename, config):
        BaseParser.parse(self, filename, config)
        self.config['configfile'] = filename

    def start_element(self, name, attrs):
        if name=='webcleaner':
            for key,val in attrs.items():
                self.config[str(key)] = val
            for key in ['port','parentproxyport','buffersize','timeout',
	                'obfuscateip','debuglevel','colorize']:
                self.config[key] = int(self.config[key])
        elif name=='filter':
            self.config['filters'].append(attrs['name'])

