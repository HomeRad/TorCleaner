#!/usr/bin/python -O
"""setup file for the distuils module"""
# -*- coding: iso-8859-1 -*-

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

import os
import stat
import re
import sys
import string
from types import StringType, TupleType
from distutils.core import setup, Extension, DEBUG
#try:
#    import py2exe
#    distklass = py2exe.Distribution
#except ImportError:
#    import distutils.dist
#    distklass = distutils.dist.Distribution
import distutils.command
import distutils.dist
distklass = distutils.dist.Distribution
from distutils.command.install import install
from distutils.command.bdist_wininst import bdist_wininst
from distutils.command.install_data import install_data
from distutils.file_util import write_file
from distutils.dir_util import create_tree, remove_tree
from distutils import util, log
from distutils.sysconfig import get_python_version


# cross compile config
cc = os.environ.get("CC")
# directory with cross compiled (for win32) python
# see also http://kampfwurst.net/python-mingw32/
win_python_dir = "/home/calvin/src/python23-maint-cvs/dist/src/"
# if we are compiling for or under windows
win_compiling = (os.name == 'nt') or (cc is not None and "mingw32" in cc)


def normpath (path):
    """norm a path name to platform specific notation"""
    return os.path.normpath(path)


def cnormpath (path):
    """norm a path name to platform specific notation, but honoring
       the win_compiling flag"""
    path = normpath(path)
    if win_compiling:
        # replace slashes with backslashes
        path = path.replace("/", "\\")
    return path


# windows install scheme for python >= 2.3
# snatched from PC/bdist_wininst/install.c
# this is used to fix install_* paths when cross compiling for windows
win_path_scheme = {
    "purelib": ("PURELIB", "Lib\\site-packages\\"),
    "platlib": ("PLATLIB", "Lib\\site-packages\\"),
    # note: same as platlib because of C extensions, else it would be purelib
    "lib": ("PLATLIB", "Lib\\site-packages\\"),
    # 'Include/dist_name' part already in archive
    "headers": ("HEADERS", ""),
    "scripts": ("SCRIPTS", "Scripts\\"),
    "data": ("DATA", ""),
}

class MyInstall (install, object):

    def run (self):
        super(MyInstall, self).run()
        # we have to write a configuration file because we need the
        # <install_data> directory (and other stuff like author, url, ...)
        data = []
        for d in ['purelib', 'platlib', 'lib', 'headers', 'scripts', 'data']:
            attr = 'install_%s'%d
            if self.root:
                # cut off root path prefix
                cutoff = len(self.root)
                # don't strip the path separator
                if self.root.endswith(os.sep):
                    cutoff -= 1
                val = getattr(self, attr)[cutoff:]
            else:
                val = getattr(self, attr)
            if win_compiling and d in win_path_scheme:
                # look for placeholders to replace
                oldpath, newpath = win_path_scheme[d]
                oldpath = "%s%s" % (os.sep, oldpath)
                if oldpath in val:
                    val = val.replace(oldpath, newpath)
            if attr=="install_data":
                base = os.path.join(val, 'share', 'webcleaner')
                data.append('config_dir = %r' % \
                            cnormpath(os.path.join(base, 'config')))
                data.append('template_dir = %r' % \
                            cnormpath(os.path.join(base, 'templates')))
            val = cnormpath(val)
            data.append("%s = %r" % (attr, val))
        self.distribution.create_conf_file(data, directory=self.install_lib)

    def get_outputs (self):
        """add the generated config file from distribution.create_conf_file()
           to the list of outputs.
        """
        outs = super(MyInstall, self).get_outputs()
        outs.append(self.distribution.get_conf_filename(self.install_lib))
        return outs

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


class MyInstallData (install_data, object):
    """My own data installer to handle permissions"""

    def run (self):
        """adjust permissions on POSIX systems"""
        super(MyInstallData, self).run()
        if os.name == 'posix' and not self.dry_run:
            # Make the data files we just installed world-readable,
            # and the directories world-executable as well.
            for path in self.get_outputs():
                mode = os.stat(path)[stat.ST_MODE]
                if stat.S_ISDIR(mode):
                    mode |= 011
                mode |= 044
                os.chmod(path, mode)


class MyDistribution (distklass, object):

    def __init__ (self, attrs=None):
        super(MyDistribution, self).__init__(attrs=attrs)
        self.config_file = "_%s2_configdata.py"%self.get_name()

    def run_commands (self):
        cwd = os.getcwd()
        data = []
	data.append('config_dir = %r' % os.path.join(cwd, "config"))
        data.append('template_dir = %r' % os.path.join(cwd, "templates"))
        data.append("install_data = %r" % cwd)
        data.append("install_scripts = %r" % cwd)
        self.create_conf_file(data)
        super(MyDistribution, self).run_commands()

    def get_conf_filename (self, directory):
        return os.path.join(directory, "_%s2_configdata.py"%self.get_name())

    def create_conf_file (self, data, directory=None):
        """create local config file from given data (list of lines) in
           the directory (or current directory if not given)
        """
        data.insert(0, "# this file is automatically created by setup.py")
        data.insert(0, "# -*- coding: iso-8859-1 -*-")
        if directory is None:
            directory = os.getcwd()
        filename = self.get_conf_filename(directory)
        # add metadata
        metanames = ("name", "version", "author", "author_email",
                     "maintainer", "maintainer_email", "url",
                     "license", "description", "long_description",
                     "keywords", "platforms", "fullname", "contact",
                     "contact_email", "fullname")
        for name in metanames:
              method = "get_" + name
              cmd = "%s = %r" % (name, getattr(self.metadata, method)())
              data.append(cmd)
        data.append('appname = "WebCleaner"')
        util.execute(write_file, (filename, data),
                     "creating %s" % filename, self.verbose>=1, self.dry_run)


class MyBdistWininst (bdist_wininst, object):
    """bdist_wininst command supporting cross compilation"""

    def run (self):
        if (sys.platform != "win32" and not win_compiling and
            (self.distribution.has_ext_modules() or
             self.distribution.has_c_libraries())):
            raise DistutilsPlatformError \
                  ("distribution contains extensions and/or C libraries; "
                   "must be compiled on a Windows 32 platform")

        if not self.skip_build:
            self.run_command('build')

        install = self.reinitialize_command('install', reinit_subcommands=1)
        install.root = self.bdist_dir
        install.skip_build = self.skip_build
        install.warn_dir = 0

        install_lib = self.reinitialize_command('install_lib')
        # we do not want to include pyc or pyo files
        install_lib.compile = 0
        install_lib.optimize = 0

        # If we are building an installer for a Python version other
        # than the one we are currently running, then we need to ensure
        # our build_lib reflects the other Python version rather than ours.
        # Note that for target_version!=sys.version, we must have skipped the
        # build step, so there is no issue with enforcing the build of this
        # version.
        target_version = self.target_version
        if not target_version:
            assert self.skip_build, "Should have already checked this"
            target_version = sys.version[0:3]
        plat_specifier = ".%s-%s" % (util.get_platform(), target_version)
        build = self.get_finalized_command('build')
        build.build_lib = os.path.join(build.build_base,
                                       'lib' + plat_specifier)

        # Use a custom scheme for the zip-file, because we have to decide
        # at installation time which scheme to use.
        for key in ('purelib', 'platlib', 'headers', 'scripts', 'data'):
            value = string.upper(key)
            if key == 'headers':
                value = value + '/Include/$dist_name'
            setattr(install,
                    'install_' + key,
                    value)

        log.info("installing to %s", self.bdist_dir)
        install.ensure_finalized()

        # avoid warning of 'install_lib' about installing
        # into a directory not in sys.path
        sys.path.insert(0, os.path.join(self.bdist_dir, 'PURELIB'))

        install.run()

        del sys.path[0]

        # And make an archive relative to the root of the
        # pseudo-installation tree.
        from tempfile import mktemp
        archive_basename = mktemp()
        fullname = self.distribution.get_fullname()
        arcname = self.make_archive(archive_basename, "zip",
                                    root_dir=self.bdist_dir)
        # create an exe containing the zip-file
        self.create_exe(arcname, fullname, self.bitmap)
        # remove the zip-file again
        log.debug("removing temporary file '%s'", arcname)
        os.remove(arcname)

        if not self.keep_temp:
            remove_tree(self.bdist_dir, dry_run=self.dry_run)

    def get_exe_bytes (self):
        if win_compiling:
            # wininst.exe is in the same directory as bdist_wininst
            # XXX for python2.4, use wininst-X.Y.exe
            directory = os.path.dirname(distutils.command.__file__)
            filename = os.path.join(directory, "wininst.exe")
            return open(filename, "rb").read()
        return super(MyBdistWininst, self).get_exe_bytes()


# global include dirs
include_dirs = []
# global macros
define_macros = []
# compiler args
extra_compile_args = []
# library directories
library_dirs = []
# libraries
libraries = []

# distinguish the different platforms
if os.name=='nt':
    # windows does not have unistd.h
    define_macros.append(('YY_NO_UNISTD_H', None))
else:
    # for gcc 3.x we could add -std=gnu99 to get rid of warnings, but
    # that breaks other compilers
    extra_compile_args.append("-pedantic")
    if win_compiling:
        # we are cross compiling with mingw
        # add directory for pyconfig.h
        include_dirs.append(win_python_dir)
        # add directory for Python.h
        include_dirs.append(os.path.join(win_python_dir, "Include"))
        # for finding libpythonX.Y.a
        library_dirs.append(win_python_dir)
        libraries.append("python%s" % get_python_version())

# C extension modules
extensions = []

# HTML parser
extensions.append(Extension('wc.HtmlParser.htmlsax',
              sources = [normpath('wc/HtmlParser/htmllex.c'),
                         normpath('wc/HtmlParser/htmlparse.c'),
                         normpath('wc/HtmlParser/s_util.c'),
                        ],
              depends = [normpath("wc/HtmlParser/htmlsax.h"),
                         normpath('wc/HtmlParser/s_util.h')],
              include_dirs = include_dirs + [normpath("wc/HtmlParser")],
              define_macros = define_macros,
              extra_compile_args = extra_compile_args,
              library_dirs = library_dirs,
              libraries = libraries,
             ))

# levenshtein distance method
extensions.append(Extension('wc.levenshtein',
              sources = [normpath('wc/levenshtein.c'),],
              include_dirs = include_dirs,
              define_macros = define_macros,
              extra_compile_args = extra_compile_args,
              library_dirs = library_dirs,
              libraries = libraries,
             ))

# javascript extension
if win_compiling:
    define_macros = [('WIN32', None),
                     ('XP_WIN', None),
                     ('EXPORT_JS_API', None),
                    ]
else:
    define_macros = []
extensions.append(Extension('wc.js.jslib',
                  sources=['wc/js/jslib.c'],
                  include_dirs = include_dirs + ['libjs'],
                  define_macros = define_macros,
                  extra_compile_args = extra_compile_args,
                  extra_objects = ['libjs/.libs/libjs.a'],
                  library_dirs = library_dirs,
                  libraries = libraries,
                 ))

# scripts
scripts = [
    'webcleaner',
    'webcleaner-certificates',
]
if win_compiling:
    scripts.append('install-webcleaner.py')

# now to the main stuff
myname = "Bastian Kleineidam"
myemail = "calvin@users.sourceforge.net"
setup (name = "webcleaner",
       version = "2.23",
       description = "a filtering HTTP proxy",
       keywords = "proxy,server,http,filters,daemon",
       author = myname,
       author_email = myemail,
       maintainer = myname,
       maintainer_email = myemail,
       url = "http://webcleaner.sourceforge.net/",
       download_url = "http://sourceforge.net/project/showfiles.php?group_id=7692",
       license = "GPL",
       packages = ['wc', 'wc.filter', 'wc.js', 'wc.magic',
           'wc.dns', 'wc.dns.rdtypes', 'wc.dns.rdtypes.IN',
           'wc.dns.rdtypes.ANY', 'wc.HtmlParser', 'wc.proxy', 'wc.proxy.auth',
           'wc.filter.rules', 'wc.webgui', 'wc.webgui.PageTemplates',
           'wc.webgui.TAL', 'wc.webgui.ZTUtils', 'wc.webgui.context',
           'wc.dns.tests', 'wc.tests', ],
       ext_modules = extensions,
       scripts = scripts,
       long_description = """WebCleaner features:
* remove unwanted HTML (adverts, flash, etc.)
* popup blocker
* disable animated GIFs
* filter images by size, remove banner adverts
* compress documents on-the-fly (with gzip)
* reduce images to low-bandwidth JPEGs
* remove/add/modify arbitrary HTTP headers
* configurable over a web interface
* usage of SquidGuard domain and url blacklists
* antivirus filter module
* detection and correction of known HTML security flaws
* Basic, Digest and (untested) NTLM proxy authentication support
* per-host access control
* HTTP/1.1 support (persistent connections, pipelining)
* HTTPS proxy CONNECT and optional SSL gateway support
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
                   'install_data': MyInstallData,
                   'bdist_wininst': MyBdistWininst,
                  },
       data_files = [('share/webcleaner/config',
      ['config/webcleaner.conf',
       'config/webcleaner.dtd',
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
       'config/rating.zap',
       'config/plugins.zap',
       'config/rating.zap',
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
       'templates/classic/adminpass.html',
       'templates/classic/blocked.html',
       'templates/classic/blocked.js',
       'templates/classic/blocked.swf',
       'templates/classic/blocked.png',
       'templates/classic/config.html',
       'templates/classic/delete.png',
       'templates/classic/disabled.png',
       'templates/classic/down.png',
       'templates/classic/edit.png',
       'templates/classic/error.html',
       'templates/classic/favicon.png',
       'templates/classic/favicon.ico',
       'templates/classic/feedback.html',
       'templates/classic/filterconfig.html',
       'templates/classic/google.html',
       'templates/classic/help.html',
       'templates/classic/iconbig.png',
       'templates/classic/index.html',
       'templates/classic/mail.png',
       'templates/classic/minidoc.png',
       'templates/classic/minifolder.png',
       'templates/classic/minifolderopen.png',
       'templates/classic/pi.js',
       'templates/classic/rated.html',
       'templates/classic/rating.html',
       'templates/classic/rating_mail.html',
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
