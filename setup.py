#!/usr/bin/env python2
"""setup file for the distuils module"""
#    Copyright (C) 2000,2001  Bastian Kleineidam
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os, string, re, sys
from types import StringType, TupleType
from distutils.core import setup, Extension, DEBUG
from distutils.dist import Distribution
from distutils.command.install import install
from distutils.command.config import config
from distutils.command.install_data import install_data
from distutils.command.build_scripts import build_scripts,first_line_re
from distutils.file_util import write_file
from distutils import util
from distutils.dep_util import newer

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
                data.append('config_dir = %s' % `os.path.join(val,
                            'share/webcleaner/config')`)
            data.append("%s = %s" % (attr, `val`))
        from pprint import pformat
        data.append('outputs = %s' % pformat(self.get_outputs()))
        self.distribution.create_conf_file(self.install_lib, data)

class MyInstallData(install_data):
    """My own data installer to handle .man pages"""
    def run (self):
        self.mkpath(self.install_dir)
        for f in self.data_files:
            if type(f) == StringType:
                # it's a simple file, so copy it
                if self.warn_dir:
                    self.warn("setup script did not provide a directory for "
                              "'%s' -- installing right in '%s'" %
                              (f, self.install_dir))
                self._install_file(f, self.install_dir)
            else:
                # it's a tuple with path to install to and a list of files
                dir = f[0]
                if not os.path.isabs(dir):
                    dir = os.path.join(self.install_dir, dir)
                elif self.root:
                    dir = change_root(self.root, dir)
                self.mkpath(dir)
                for data in f[1]:
                    self._install_file(data, dir)

    def _install_file(self, filename, dirname):
        out = self.copy_file(filename, dirname)
        if type(out) == TupleType:
            out = out[0]
        # match for man pages .[0-9]
        if re.search(r'/man/.+\.\d$', out):
            out = out+".gz"
        self.outfiles.append(out)



class my_build_scripts(build_scripts):

    description = "\"build\" scripts (copy and fixup #! line)"

    user_options = [
        ('build-dir=', 'd', "directory to \"build\" (copy) to"),
        ('force', 'f', "forcibly build everything (ignore file timestamps"),
        ]

    boolean_options = ['force']


    def copy_scripts(self):
        """patched because of a bug"""
        outfiles = []
        self.mkpath(self.build_dir)
        for script in self.scripts:
            adjust = 0
            outfile = os.path.join(self.build_dir, os.path.basename(script))

            if not self.force and not newer(script, outfile):
                self.announce("not copying %s (output up-to-date)" % script)
                continue

            # Always open the file, but ignore failures in dry-run mode --
            # that way, we'll get accurate feedback if we can read the
            # script.
            try:
                f = open(script, "r")
            except IOError:
                if not self.dry_run:
                   raise
                f = None
            else:
                first_line = f.readline()
                if not first_line:
                    self.warn("%s is an empty file (skipping)" % script)
                    continue

                match = first_line_re.match(first_line)
                if match:
                    adjust = 1
                    post_interp = match.group(1) or ""

            if adjust:
                self.announce("copying and adjusting %s -> %s" %
                              (script, self.build_dir))
                if not self.dry_run:
                    outf = open(outfile, "w")
                    outf.write("#!%s%s\n" % 
                               (os.path.normpath(sys.executable), post_interp))
                    outf.writelines(f.readlines())
                    outf.close()
                if f:
                    f.close()
            else:
                f.close()
                self.copy_file(script, outfile)

    # copy_scripts ()



class MyDistribution(Distribution):
    def __init__(self, attrs=None):
        Distribution.__init__(self, attrs=attrs)
        self.config_file = "_"+self.get_name()+"_configdata.py"


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

setup (name = "webcleaner",
       version = "0.10",
       description = "a filtering HTTP proxy",
       author = myname,
       author_email = myemail,
       maintainer = myname,
       maintainer_email = myemail,
       url = "http://webcleaner.sourceforge.net/",
       licence = "GPL (Python 2.0 usage granted)",
       packages = ['', 'wc', 'wc/filter', 'wc/daemon',
                   'wc/parser', 'wc/gui', 'wc/proxy', 'wc/proxy/dns'],
       ext_modules = [Extension('wc.parser',['wc/parser/sgmlop.c'])],
       scripts = ['webcleaner', 'webcleanerconf'],
       long_description =
"""WebCleaner can
o disable animated GIFs
o compress documents on-the-fly (with gzip)
o enhance your privacy (remove user-agent: header and obfuscate IP address)
o remove unwanted HTML (adverts, javascript, ...)
o be completely customized to your needs
""",
       distclass = MyDistribution,
       cmdclass = {'install': MyInstall,
                   'install_data': MyInstallData,
		   'build_scripts': my_build_scripts,
                  },
       data_files = [('share/webcleaner/config',
                      ['config/blocked.html',
                       'config/blocked.gif',
                       'config/webcleaner.conf',
                       'config/webcleaner.dtd',
 	               'config/filter.dtd',
		       'config/adverts.zap',
		       'config/css.zap',
		       'config/erotic.zap',
		       'config/finance.zap',
		       'config/misc.zap',
		       'config/plugins.zap',
		       'config/redirects.zap',
		       'config/scripting.zap',
		       'config/iconbig.png',
		       'config/minidoc.png',
		       'config/minifolder.png',
                       'config/disabledrule.png',
		       'config/minifolderopen.png']),
                     ('share/webcleaner/examples',
                      ['webcleaner.bat', 'filtertest', 'filtertest.html']),
                     ('man/man1',
		      ['webcleaner.1', 'webcleanerconf.1']),
		    ],
)
