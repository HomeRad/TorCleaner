#!/usr/bin/python2.3 -O
"""setup file for the distuils module"""
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

import os, re, sys, string
from types import StringType, TupleType
from distutils.core import setup, Extension, DEBUG
from distutils.dist import Distribution
from distutils.command.install import install
from distutils.file_util import write_file
from distutils import util

def p (path):
    """norm a path name to platform specific notation"""
    return os.path.normpath(path)

# set to 1 to use JavaScript
USE_JS = 1

class MyInstall (install):
    def run (self):
        install.run(self)
        # we have to write a configuration file because we need the
        # <install_data> directory (and other stuff like author, url, ...)
        data = []
        for d in ['purelib', 'platlib', 'lib', 'headers', 'scripts', 'data']:
            attr = 'install_'+d
            if self.root:
                val = getattr(self, attr)[len(self.root):]
            else:
                val = getattr(self, attr)
            if attr=="install_data":
                base = os.path.join(val, 'share', 'webcleaner')
                data.append('config_dir = %s' % \
                            `os.path.normcase(os.path.join(base, 'config'))`)
                data.append('template_dir = %s' % \
                          `os.path.normcase(os.path.join(base, 'templates'))`)
            data.append("%s = %s" % (attr, `val`))
        from pprint import pformat
        data.append('outputs = %s' % pformat(self.get_outputs()))
        self.distribution.create_conf_file(self.install_lib, data)
        # install proxy service
        if os.name=="nt":
            self.install_nt_service()


    def state_nt_service (self, name):
        import win32serviceutil
        return win32serviceutil.QueryServiceStatus(name)[1]


    def install_nt_service (self):
        from wc import daemon, AppName, Configuration
        import win32serviceutil
        oldargs = sys.argv
        # install service
        sys.argv = ['webcleaner', 'install']
        win32serviceutil.HandleCommandLine(daemon.ProxyService)
        # stop proxy (if it is running)
        state = self.state_nt_service(AppName)
        while state==win32service.SERVICE_START_PENDING:
            time.sleep(1)
            state = self.state_nt_service(AppName)
        if state==win32service.SERVICE_RUNNING:
            sys.argv = ['webcleaner', 'stop']
            win32serviceutil.HandleCommandLine(daemon.ProxyService)
        state = self.state_nt_service(AppName)
        while state==win32service.SERVICE_STOP_PENDING:
            time.sleep(1)
            state = self.state_nt_service(AppName)
        # start proxy
        sys.argv = ['webcleaner', 'start']
        win32serviceutil.HandleCommandLine(daemon.ProxyService)
        sys.argv = oldargs
        config = Configuration()
        config_url = "http://localhost:%d/" % config['port']
        # sleep a while to let the proxy start...
        import time, webbrowser
        time.sleep(5)
        webbrowser.open(config_url)


    # sent a patch for this, but here it is for compatibility
    def dump_dirs (self, msg):
        if DEBUG:
            from distutils.fancy_getopt import longopt_xlate
            print msg + ":"
            for opt in self.user_options:
                opt_name = opt[0]
                if opt_name[-1] == "=":
                    opt_name = opt_name[0:-1]
                if self.negative_opt.has_key(opt_name):
                    opt_name = string.translate(self.negative_opt[opt_name],
                                                longopt_xlate)
                    val = not getattr(self, opt_name)
                else:
                    opt_name = string.translate(opt_name, longopt_xlate)
                    val = getattr(self, opt_name)
                print "  %s: %s" % (opt_name, val)


class MyDistribution (Distribution):
    def __init__ (self, attrs=None):
        Distribution.__init__(self, attrs=attrs)
        self.config_file = "_%s2_configdata.py"%self.get_name()


    def run_commands (self):
        cwd = os.getcwd()
        data = []
	data.append('config_dir = %s' % `os.path.join(cwd, "config")`)
        data.append('template_dir = %s' % `os.path.join(cwd, "templates")`)
        data.append("install_data = %s" % `cwd`)
        self.create_conf_file("", data)
        Distribution.run_commands(self)


    def create_conf_file (self, directory, data=[]):
        data.insert(0, "# this file is automatically created by setup.py")
        if not directory:
            directory = os.getcwd()
        filename = os.path.join(directory, self.config_file)
        # add metadata
        metanames = ("name", "version", "author", "author_email",
                     "maintainer", "maintainer_email", "url",
                     "license", "description", "long_description",
                     "keywords", "platforms", "fullname", "contact",
                     "contact_email", "fullname")
        for name in metanames:
              method = "get_" + name
              cmd = "%s = %s" % (name, `getattr(self.metadata, method)()`)
              data.append(cmd)
        data.append('appname = "WebCleaner"')
        util.execute(write_file, (filename, data),
                     "creating %s" % filename, self.verbose>=1, self.dry_run)


    def create_batch_file (self, directory, data, filename):
        filename = os.path.join(directory, filename)
        # write the batch file
        util.execute(write_file, (filename, data),
                 "creating %s" % filename, self.verbose>=1, self.dry_run)

if os.name=='nt':
    # windows does not have unistd.h
    macros = [('YY_NO_UNISTD_H', None)]
    cargs = []
else:
    macros = []
    # for gcc 3.x we could add -std=gnu99 to get rid of warnings, but
    # that breaks other compilers
    cargs = ["-pedantic"]

# extensions
extensions = [Extension('wc.parser.htmlsax',
                        sources=[p('wc/parser/htmllex.c'),
                                 p('wc/parser/htmlparse.c')],
                        depends=[p("wc/parser/htmlsax.h")],
                        include_dirs = [p("wc/parser")],
                        define_macros = macros,
                        extra_compile_args = cargs,
                      ),
             Extension('wc.levenshtein',
                        sources=[p('wc/levenshtein.c'),],
                        define_macros = macros,
                        extra_compile_args = cargs,
                      ),
             ]
# javascript extension
if os.name=='nt':
    extensions.append(Extension('wc.js.jslib',
                    sources=['wc/js/jslib.c'],
                    # since we are not compiling with configure/make, put
                    # all needed defines here
                    define_macros = [('WIN32', None), ('XP_WIN', None), ('EXPORT_JS_API', None)],
                    include_dirs = ['libjs'],
                    extra_compile_args = cargs,
                    extra_objects = ['libjs/.libs/libjs.a'],
                  ))
else:
    extensions.append(Extension('wc.js.jslib',
                    sources=['wc/js/jslib.c'],
                    include_dirs = ['libjs'],
                    extra_compile_args = cargs,
                    extra_objects = ['libjs/.libs/libjs.a'],
                  ))

# no to the main stuff
myname = "Bastian Kleineidam"
myemail = "calvin@users.sourceforge.net"
setup (name = "webcleaner",
       version = "2.8",
       description = "a filtering HTTP proxy",
       author = myname,
       author_email = myemail,
       maintainer = myname,
       maintainer_email = myemail,
       url = "http://webcleaner.sourceforge.net/",
       license = "GPLv2",
       packages = ['', 'wc', 'wc/filter', 'wc/daemon', 'wc/js', 'wc/magic',
           'wc/parser', 'wc/proxy', 'wc/proxy/dns', 'wc/proxy/auth',
           'wc/filter/rules', 'wc/webgui', 'wc/webgui/simpletal',
           'wc/webgui/context',],
       ext_modules = extensions,
       scripts = ['webcleaner'],
       long_description = """WebCleaner features:
* HTTP/1.1 and HTTPS support
* integrated HTML parser, removes unwanted HTML (adverts, flash, etc.)
* integrated JavaScript engine, allows popup filtering
* compress documents on-the-fly (with gzip)
* disable animated GIFs
* filter images by size, removes banner adverts
* reduce images to low-bandwidth JPEGs
* remove/add/modify arbitrary HTTP headers
* usage of SquidGuard domain and url blacklists
* Basic, Digest and (untested) NTLM proxy authentication support
* per-host access control
* configurable over a themable web interface
""",
       classifiers = ['Development Status :: 5 - Production/Stable',
           'Environment :: No Input/Output (Daemon)',
           'Programming Language :: Python',
           'Programming Language :: C',
           'Topic :: Internet :: Proxy Servers',
           'License :: OSI Approved :: GNU General Public License (GPL)',
       ],
       distclass = MyDistribution,
       cmdclass = {'install': MyInstall,
                  },
       data_files = [('share/webcleaner/config',
      ['config/webcleaner.conf',
       'config/webcleaner.dtd',
       'config/wcheaders.conf',
       'config/wcheaders.dtd',
       'config/filter.dtd',
       'config/logging.conf',
       'config/adverts.zap',
       'config/adverts_specific.zap',
       'config/blacklist_ads.zap',
       'config/blacklist_aggressive.zap',
       'config/blacklist_violence.zap',
       'config/css.zap',
       'config/erotic.zap',
       'config/header.zap',
       'config/misc.zap',
       'config/pics_rating.zap',
       'config/plugins.zap',
       'config/redirects.zap',
       'config/scripting.zap',
       'config/trackers.zap',
       'config/magic.mime',
       ]),
     ('share/webcleaner/config/blacklists',
      ['config/blacklists/README']),
     ('share/webcleaner/config/blacklists/ads',
      ['config/blacklists/ads/urls.gz',
       'config/blacklists/ads/domains.gz']),
     ('share/webcleaner/config/blacklists/aggressive',
      ['config/blacklists/aggressive/urls.gz',
       'config/blacklists/aggressive/domains.gz']),
     ('share/webcleaner/config/blacklists/violence',
      ['config/blacklists/violence/domains.gz']),
     ('man/man1',
      ['webcleaner.1',
       'webcleaner.conf.5',
      ]),
     ('share/webcleaner/templates/classic',
      ['templates/classic/accessibility.html',
       'templates/classic/blocked.html',
       'templates/classic/blocked.png',
       'templates/classic/config.html',
       'templates/classic/disabled.png',
       'templates/classic/down.png',
       'templates/classic/error.html',
       'templates/classic/feedback.html',
       'templates/classic/filterconfig.html',
       'templates/classic/google.html',
       'templates/classic/help.html',
       'templates/classic/iconbig.png',
       'templates/classic/index.html',
       'templates/classic/minidoc.png',
       'templates/classic/minifolder.png',
       'templates/classic/minifolderopen.png',
       'templates/classic/pics.html',
       'templates/classic/robots.txt',
       'templates/classic/up.png',
       'templates/classic/update.html',
       'templates/classic/update_doit.html',
       'templates/classic/wc.css',
      ]),
     ('share/webcleaner/templates/classic/macros',
      ['templates/classic/macros/rules.html',
       'templates/classic/macros/standard.html',
      ]),
     ('share/webcleaner/examples',
      ['config/bl2wc.py',
       'config/dmozfilter.py',
      ]),
     ('share/locale/de/LC_MESSAGES',
      ['share/locale/de/LC_MESSAGES/webcleaner.mo',
      ]),
     ]
)
