#!/usr/bin/env python
"""setup file for the distuils module"""
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

import os, re, sys, string
from types import StringType, TupleType
from distutils.core import setup, Extension, DEBUG
from distutils.dist import Distribution
from distutils.command.install import install
from distutils.file_util import write_file
from distutils import util

class MyInstall(install):
    def run(self):
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
                data.append('config_dir = %s' % \
             `os.path.normcase(os.path.join(val, 'share/webcleaner/config'))`)
            data.append("%s = %s" % (attr, `val`))
        from pprint import pformat
        data.append('outputs = %s' % pformat(self.get_outputs()))
        self.distribution.create_conf_file(self.install_lib, data)


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


class MyDistribution(Distribution):
    def __init__(self, attrs=None):
        Distribution.__init__(self, attrs=attrs)
        self.config_file = "_%s2_configdata.py"%self.get_name()


    def run_commands(self):
        cwd = os.getcwd()
        data = []
	data.append('config_dir = %s' % `os.path.join(cwd, "config")`)
        data.append("install_data = %s" % `cwd`)
        self.create_conf_file(".", data)
        Distribution.run_commands(self)


    def create_conf_file(self, directory, data=[]):
        data.insert(0, "# this file is automatically created by setup.py")
        filename = os.path.join(directory, self.config_file)
        # add metadata
        metanames = dir(self.metadata) + \
                    ['fullname', 'contact', 'contact_email']
        for name in metanames:
              method = "get_" + name
              cmd = "%s = %s" % (name, `getattr(self.metadata, method)()`)
              data.append(cmd)
        util.execute(write_file, (filename, data),
                     "creating %s" % filename, self.verbose>=1, self.dry_run)


myname = "Bastian Kleineidam"
myemail = "calvin@users.sourceforge.net"

data_files = [('share/webcleaner/config',
      ['config/blocked.html',
       'config/blocked.gif',
       'config/webcleaner.conf',
       'config/webcleaner.dtd',
       'config/filter.dtd',
       'config/adverts.zap',
       'config/css.zap',
       'config/erotic.zap',
       'config/misc.zap',
       'config/plugins.zap',
       'config/redirects.zap',
       'config/scripting.zap',
       'config/iconbig.png',
       'config/minidoc.png',
       'config/minifolder.png',
       'config/disabledrule.png',
       'config/minifolderopen.png']),
     ('man/man1',
      ['webcleaner.1', 'webcleanerconf.1', 'wcheaders.1', 'webcleaner.conf.5']),
    ]
scripts = ['webcleaner', 'webcleanerconf', 'wcheaders']

if os.name=="nt":
    scripts.append("webcleaner.bat")
    scripts.append("webcleanerconf.bat")
    scripts.append("wcheaders.bat")
else:
    data_files.append(('share/webcleaner/examples',
                       ['webcleaner.bat',
                        'webcleanerconf.bat',
                        'wcheaders.bat']))

setup (name = "webcleaner",
       version = "0.27",
       description = "a filtering HTTP proxy",
       author = myname,
       author_email = myemail,
       maintainer = myname,
       maintainer_email = myemail,
       url = "http://webcleaner.sourceforge.net/",
       licence = "GPLv2",
       packages = ['', 'wc', 'wc/filter', 'wc/daemon',
                   'wc/parser', 'wc/gui', 'wc/proxy', 'wc/proxy/dns'],
       ext_modules = [Extension('wc.parser.htmlsax',
                      ['wc/parser/htmlsax.c'],
                      libraries = ["xml2"],
                      include_dirs = ["/usr/include/libxml2"],
                      )],
       scripts = scripts,
       long_description =
"""WebCleaner features:
o disable animated GIFs
o compress documents on-the-fly (with gzip)
o enhance your privacy (remove user-agent: header and obfuscate IP address)
o remove unwanted HTML (adverts, javascript, ...)
o completely customizable to suit your (filtering) needs
o single process proxy with select() I/O
o HTTP/1.1 support
""",
       distclass = MyDistribution,
       cmdclass = {'install': MyInstall,
                  },
       data_files = data_files,
)
