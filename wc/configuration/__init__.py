# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Store configuration data.
"""

import time
import signal
import os
import stat
import glob
from . import ratingstorage
from ..XmlUtils import xmlquoteattr
from ..url import match_url
from .. import (log, LOG_PROXY, LOG_FILTER, decorators, strformat, fileutil,
    ConfigDir, HasSsl, Url, proxy, clamav)
from ..network import iputil

ConfigCharset = "iso-8859-1"

# global config var
config = None
# if config is about to be reloaded
pending_reload = False

def init(confdir=ConfigDir):
    """Initialize and load the configuration."""
    global config
    config = Configuration(confdir)
    return config


# note that Python already ignores SIGPIPE, so no need to configure that
if os.name == 'posix':
    _signum = signal.SIGHUP
else:
    _signum = signal.NSIG
@decorators.signal_handler(_signum)
def sighup_reload_config(signum, frame):
    """Support reload on posix systems.
    Store timer for reloading configuration data."""
    global pending_reload
    if not pending_reload:
        pending_reload = True
        from ..proxy import timer
        timer.make_timer(1, reload_config)


def reload_config():
    """Reload configuration."""
    global pending_reload
    config.reset()
    config.read_proxyconf()
    config.read_filterconf()
    config.init_filter_modules()
    proxy.dns_lookups.init_resolver()
    clamav.init_clamav_conf(config['clamavconf'])
    pending_reload = False


def proxyconf_file(confdir):
    """Return proxy configuration filename."""
    return os.path.join(confdir, "webcleaner.conf")


def filterconf_files(dirname):
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
    "Rating",
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

class Configuration(dict):
    """Hold all configuration data, inclusive filter rules."""

    def __init__(self, confdir):
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

    def check_ssl_certificates(self):
        """Check existance of SSL support and generate certificates if
        needed. This is necessary since SSL support can be installed
        after WebCleaner."""
        if HasSsl and self["sslgateway"]:
            from ..proxy import ssl
            if not ssl.exist_certificates(self.configdir):
                ssl.create_certificates(self.configdir)

    def reset(self):
        """Reset to default values."""
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
        self['mime_content_rewriting'] = set()
        self['gui_theme'] = "classic"
        self['timeout'] = 10
        self['auth_ntlm'] = 0
        self['clamavconf'] = ""
        # in development mode some values have different defaults
        self['development'] = int(os.environ.get("WC_DEVELOPMENT", "0"))
        self['baseurl'] = Url
        self['try_google'] = 0
        from ..rating import service
        self['rating_service'] = service.WebCleanerService()
        self['rating_storage'] = ratingstorage.UrlRatingStorage(self.configdir)
        # delete all registered sids
        from ..filter.rules import delete_registered_sids
        delete_registered_sids()

    def read_proxyconf(self):
        """Read proxy configuration."""
        from .confparse import WConfigParser
        WConfigParser(self.configfile, self).parse()
        # make sure that usernames and passwords are ASCII, or there
        # can be encoding errors
        for name in ascii_values:
            if not strformat.is_ascii(self[name]):
                msg = "The %r configuration value must be ASCII." % name
                raise TypeError(msg)

    def write_proxyconf(self):
        """Write proxy configuration."""
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
        fileutil.write_file(self.configfile, content)

    def read_filterconf(self):
        """Read filter rules."""
        from ..filter.rules import generate_sids
        from ..filter.rules.FolderRule import recalc_up_down
        for filename in filterconf_files(self.filterdir):
            if os.stat(filename)[stat.ST_SIZE] == 0:
                log.info(LOG_PROXY, "Skipping empty file %r", filename)
                continue
            from .confparse import ZapperParser
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
        self.check_single_rules()

    def check_single_rules(self):
        single_rules = ('javascript', 'rating', 'antivirus', 'nocomments')
        enabled = set()
        for folder in self['folderrules']:
            for rule in folder.rules:
                if rule.disable:
                    continue
                key = rule.name
                if key in single_rules:
                    if key in enabled:
                        log.warn(LOG_FILTER,
                            "Duplicate %r rule:\n%s.", key, rule)
                    else:
                        enabled.add(rule.name)

    def merge_folder(self, folder, dryrun=False, log=None):
        """Merge given folder data into config

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

    def write_filterconf(self):
        """Write filter rules."""
        for folder in self['folderrules']:
            folder.write()

    def init_filter_modules(self):
        """Go through list of rules and store them in the filter
        objects. This will also compile regular expression strings
        to regular expression objects.
        """
        # reset filter lists
        from .. import filter
        for stage in filter.FilterStages:
            self['filterlist'][stage] = []
        self['filtermodules'] = []
        self['mime_content_rewriting'] = set()
        for filtername in self['filters']:
            # import filter module
            exec "from ..filter import %s" % filtername
            # Filter class has same name as module.
            clazz = getattr(getattr(filter, filtername), filtername)
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
        for filters in self['filterlist'].values():
            # see Filter.__cmp__ on how sorting is done
            filters.sort()

    def nofilter(self, url):
        """Decide whether to filter this url or not.

        @return: True if the request must not be filtered, else False
        """
        return match_url(url, self['nofilterhosts'])

    def allowed(self, host):
        """Return True if the host is allowed for proxying, else False."""
        hostset = self['allowedhostset']
        return iputil.host_in_set(host, hostset[0], hostset[1])
