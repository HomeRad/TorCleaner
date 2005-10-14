#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2005  Bastian Kleineidam
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
"""
Setup file for the distuils module.
"""

import sys
if not hasattr(sys, "version_info"):
    raise SystemExit, "This program requires Python 2.4 or later."
if sys.version_info < (2, 4, 0, 'final', 0):
    raise SystemExit, "This program requires Python 2.4 or later."
import os
import popen2
import stat
import string
import glob
from distutils.core import setup, Extension, DEBUG
from distutils.spawn import find_executable
import distutils.dist
import distutils.command
from distutils.command.bdist_wininst import bdist_wininst
from distutils.command.install import install
from distutils.command.install_data import install_data
from distutils.command.build_ext import build_ext
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.dir_util import remove_tree
from distutils.file_util import write_file
from distutils.sysconfig import get_python_version
from distutils.errors import DistutilsPlatformError
from distutils import util, log

# cross compile config
cc = os.environ.get("CC")
# directory with cross compiled (for win32) python
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
    if not os.path.isabs(path):
        path = normpath(os.path.join(sys.prefix, path))
    return path


class MyInstall (install, object):

    def run (self):
        super(MyInstall, self).run()
        # we have to write a configuration file because we need the
        # <install_data> directory (and other stuff like author, url, ...)
        # all paths are made absolute by cnormpath()
        data = []
        for d in ['purelib', 'platlib', 'lib', 'headers', 'scripts', 'data']:
            attr = 'install_%s' % d
            if self.root:
                # cut off root path prefix
                cutoff = len(self.root)
                # don't strip the path separator
                if self.root.endswith(os.sep):
                    cutoff -= 1
                val = getattr(self, attr)[cutoff:]
            else:
                val = getattr(self, attr)
            if attr == 'install_data':
                cdir = os.path.join(val, 'share', 'webcleaner', 'config')
                data.append('config_dir = %r' % cnormpath(cdir))
                tdir = os.path.join(val, 'share', 'webcleaner', 'templates')
                data.append('template_dir = %r' % cnormpath(tdir))
            data.append("%s = %r" % (attr, cnormpath(val)))
        self.distribution.create_conf_file(data, directory=self.install_lib)

    def get_outputs (self):
        """
        Add the generated config file from distribution.create_conf_file()
        to the list of outputs.
        """
        outs = super(MyInstall, self).get_outputs()
        outs.append(self.distribution.get_conf_filename(self.install_lib))
        return outs

    # compatibility bugfix for Python << 2.5, << 2.4.1, << 2.3.5
    # XXX remove this method when depending on one of the above versions
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
    """
    My own data installer to handle permissions.
    """

    def run (self):
        """
        Install .mo files and adjust permissions on POSIX systems.
        """
        # add .mo files to data files
        for (_src, _dst) in list_message_files(self.distribution.get_name()):
            _build_dst = os.path.join("build", _dst)
            item = [os.path.dirname(_dst), [_build_dst]]
            self.data_files.append(item)
        # install data files
        super(MyInstallData, self).run()
        # adjust permissions
        if os.name == 'posix' and not self.dry_run:
            # Make the data files we just installed world-readable,
            # and the directories world-executable as well.
            for path in self.get_outputs():
                mode = os.stat(path)[stat.ST_MODE]
                if stat.S_ISDIR(mode):
                    mode |= 011
                mode |= 044
                os.chmod(path, mode)


class MyDistribution (distutils.dist.Distribution, object):
    """
    Custom distribution class generating config file.
    """

    def run_commands (self):
        """
        Generate config file and run commands.
        """
        cwd = os.getcwd()
        data = []
	data.append('config_dir = %r' % os.path.join(cwd, "config"))
        data.append('template_dir = %r' % os.path.join(cwd, "templates"))
        data.append("install_data = %r" % cwd)
        data.append("install_scripts = %r" % cwd)
        self.create_conf_file(data)
        super(MyDistribution, self).run_commands()

    def get_conf_filename (self, directory):
        """
        Get name for config file.
        """
        return os.path.join(directory, "_%s2_configdata.py"%self.get_name())

    def create_conf_file (self, data, directory=None):
        """
        Create local config file from given data (list of lines) in
        the directory (or current directory if not given).
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
              val = getattr(self.metadata, method)()
              if isinstance(val, str):
                  val = unicode(val)
              cmd = "%s = %r" % (name, val)
              data.append(cmd)
        data.append('appname = "WebCleaner"')
        # write the config file
        util.execute(write_file, (filename, data),
                     "creating %s" % filename, self.verbose>=1, self.dry_run)


class MyBdistWininst (bdist_wininst, object):
    """
    Custom bdist_wininst command supporting cross compilation.
    """

    def run (self):
        if (not win_compiling and
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
            # wininst-X.Y.exe is in the same directory as bdist_wininst
            directory = os.path.dirname(distutils.command.__file__)
            filename = os.path.join(directory, "wininst-7.1.exe")
            return open(filename, "rb").read()
        return super(MyBdistWininst, self).get_exe_bytes()


def cc_supports_option (cc, option):
    """
    Check if the given C compiler supports the given option.

    @return: True if the compiler supports the option, else False
    @rtype: bool
    """
    prog = "int main(){}\n"
    cc_cmd = "%s -E %s -" % (cc[0], option)
    pipe = popen2.Popen4(cc_cmd)
    pipe.tochild.write(prog)
    pipe.tochild.close()
    status = pipe.wait()
    if os.WIFEXITED(status):
        return os.WEXITSTATUS(status)==0
    return False


class MyBuildExt (build_ext, object):
    """
    Custom build extension command.
    """

    def build_extensions (self):
        """
        Add -std=gnu99 to build options if supported.
        And compress extension libraries.
        """
        # For gcc >= 3 we can add -std=gnu99 to get rid of warnings.
        extra = []
        if self.compiler.compiler_type == 'unix':
            option = "-std=gnu99"
            if cc_supports_option(self.compiler.compiler, option):
                extra.append(option)
        # First, sanity-check the 'extensions' list
        self.check_extensions_list(self.extensions)
        for ext in self.extensions:
            for opt in extra:
                if opt not in ext.extra_compile_args:
                    ext.extra_compile_args.append(opt)
            self.build_extension(ext)
        self.compress_extensions()

    def compress_extensions (self):
        """
        Run UPX compression over built extension libraries.
        """
        # currently upx supports only .dll files
        if os.name != 'nt':
            return
        upx = find_executable("upx")
        if upx is None:
            # upx not found
            return
        for filename in self.get_outputs():
            compress_library(upx, filename)


def compress_library (upx, filename):
    """
    Compresses a dynamic library file with upx (currently only .dll
    files are supported).
    """
    log.info("upx-compressing %s", filename)
    os.system('%s -q --best "%s"' % (upx, filename))


def list_message_files (package, suffix=".po"):
    """
    Return list of all found message files and their installation paths.
    """
    _files = glob.glob("po/*" + suffix)
    _list = []
    for _file in _files:
        # basename (without extension) is a locale name
        _locale = os.path.splitext(os.path.basename(_file))[0]
        _list.append((_file, os.path.join(
            "share", "locale", _locale, "LC_MESSAGES", "%s.mo" % package)))
    return _list


def check_manifest ():
    """
    Snatched from roundup.sf.net.
    Check that the files listed in the MANIFEST are present when the
    source is unpacked.
    """
    try:
        f = open('MANIFEST')
    except:
        print '\n*** SOURCE WARNING: The MANIFEST file is missing!'
        return
    try:
        manifest = [l.strip() for l in f.readlines()]
    finally:
        f.close()
    err = [line for line in manifest if not os.path.exists(line)]
    if err:
        n = len(manifest)
        print '\n*** SOURCE WARNING: There are files missing (%d/%d found)!'%(
            n-len(err), n)
        print 'Missing:', '\nMissing: '.join(err)


class MyBuild (build, object):
    """
    Custom build command.
    """

    def build_message_files (self):
        """
        For each po/*.po, build .mo file in target locale directory.
        """
        for (_src, _dst) in list_message_files(self.distribution.get_name()):
            _build_dst = os.path.join("build", _dst)
            destdir = os.path.dirname(_build_dst)
            if not os.path.exists(destdir):
                self.mkpath(destdir)
            if not os.path.exists(_build_dst) or \
              (os.path.getmtime(_build_dst) < os.path.getmtime(_src)):
                log.info("compiling %s -> %s" % (_src, _build_dst))
                from wc import msgfmt
                msgfmt.make(_src, _build_dst)

    def run (self):
        check_manifest()
        self.build_message_files()
        build.run(self)


class MyClean (clean, object):
    """
    Custom clean command.
    """

    def run (self):
        if self.all:
            # remove share directory
            directory = os.path.join("build", "share")
            if os.path.exists(directory):
                remove_tree(directory, dry_run=self.dry_run)
            else:
                log.warn("'%s' does not exist -- can't clean it", directory)
        clean.run(self)


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

if os.name == 'nt':
    # windows does not have unistd.h
    define_macros.append(('YY_NO_UNISTD_H', None))
else:
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
       'config/feeds.zap',
       'config/header.zap',
       'config/meta.zap',
       'config/misc.zap',
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
       'templates/classic/restart.html',
       'templates/classic/restart_ask.html',
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
     ]
if os.name == 'posix':
    data_files.append(('share/man/man1', [
        'doc/en/webcleaner.1',
        'doc/en/webcleaner-certificates.1',
        ]))
    data_files.append(('share/man/man5', [
        'doc/en/webcleaner.conf.5',
        ]))
    data_files.append(('share/man/de/man1', [
        'doc/de/webcleaner.1',
        'doc/de/webcleaner-certificates.1',
        ]))
    data_files.append(('share/man/de/man5', [
        'doc/de/webcleaner.conf.5',
        ]))

# now to the main stuff
myname = "Bastian Kleineidam"
myemail = "calvin@users.sourceforge.net"
setup (name = "webcleaner",
       version = "2.34",
       description = "a filtering HTTP proxy",
       keywords = "proxy,server,http,filters,daemon",
       author = myname,
       author_email = myemail,
       maintainer = myname,
       maintainer_email = myemail,
       url = "http://webcleaner.sourceforge.net/",
       download_url = "http://sourceforge.net/project/showfiles.php?group_id=7692",
       license = "GPL",
       packages = ['wc', 'wc.filter', 'wc.filter.rating', 'wc.filter.rules',
           'wc.filter.rating.storage', 'wc.filter.html', 'wc.filter.xmlfilt',
           'wc.js', 'wc.magic', 'wc.dns', 'wc.dns.rdtypes', 'wc.http',
           'wc.dns.rdtypes.IN', 'wc.dns.rdtypes.ANY', 'wc.HtmlParser',
           'wc.proxy', 'wc.proxy.auth', 'wc.webgui',
           'wc.proxy.decoder', 'wc.proxy.encoder',
           'wc.webgui.PageTemplates', 'wc.webgui.TAL', 'wc.webgui.ZTUtils',
           'wc.webgui.context', ],
       ext_modules = extensions,
       long_description = """WebCleaner features:
* remove unwanted HTML (adverts, flash, etc.)
* popup blocker
* disable animated GIF images
* filter images by size, remove banner adverts
* compress documents on-the-fly (with gzip)
* reduce images to low-bandwidth JPEG images
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
       distclass = MyDistribution,
       cmdclass = {'install': MyInstall,
                   'install_data': MyInstallData,
                   'bdist_wininst': MyBdistWininst,
                   'build_ext': MyBuildExt,
                   'build': MyBuild,
                   'clean': MyClean,
                  },
       scripts = scripts,
       data_files = data_files,
       classifiers = ['Development Status :: 5 - Production/Stable',
           'Environment :: No Input/Output (Daemon)',
           'Programming Language :: Python',
           'Programming Language :: C',
           'Topic :: Internet :: Proxy Servers',
           'License :: OSI Approved :: GNU General Public License (GPL)',
       ],
)
