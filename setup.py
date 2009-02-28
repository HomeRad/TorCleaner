#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
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
if not (hasattr(sys, 'version_info') or
        sys.version_info < (2, 6, 0, 'final', 0)):
    raise SystemExit("This program requires Python 2.6 or later.")
import os
import subprocess
import stat
import glob
import distutils
from distutils.core import setup, Extension
from distutils.spawn import find_executable
from distutils.cmd import Command
from distutils.command.install import install
from distutils.command.install_data import install_data
from distutils.command.build_ext import build_ext
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.command.sdist import sdist
from distutils.dir_util import remove_tree
from distutils.file_util import write_file
from distutils.util import convert_path

# installed file list
INSTALL_LIST = "install_log.txt"

def normpath (path):
    """Norm a path name."""
    return os.path.normpath(path)


def cnormpath (path):
    """Norm a path name to platform specific notation."""
    path = normpath(path)
    if os.name == 'nt':
        # replace slashes with backslashes
        path = path.replace("/", "\\")
    if not os.path.isabs(path):
        path= normpath(os.path.join(sys.prefix, path))
    return path


# snatched from setuptools :)
def find_packages(where='.', exclude=()):
    """Return a list all Python packages found within directory 'where'

    'where' should be supplied as a "cross-platform" (i.e. URL-style) path; it
    will be converted to the appropriate local path syntax.  'exclude' is a
    sequence of package names to exclude; '*' can be used as a wildcard in the
    names, such that 'foo.*' will exclude all subpackages of 'foo' (but not
    'foo' itself).
    """
    out = []
    stack=[(convert_path(where), '')]
    while stack:
        where, prefix = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if (os.path.isdir(fn) and
                os.path.isfile(os.path.join(fn,'__init__.py'))
               ):
                out.append(prefix+name)
                stack.append((fn, prefix + name + '.'))
    for pat in exclude:
        from fnmatch import fnmatchcase
        out = [item for item in out if not fnmatchcase(item, pat)]
    return out


class MyInstall (install, object):

    def run (self):
        global INSTALL_LIST
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
        # Write out the installed file list.
        fd = open(INSTALL_LIST, 'wb')
        try:
            for item in self.get_outputs():
                fd.write(item)
                fd.write(os.linesep)
        finally:
            fd.close()

    def get_outputs (self):
        """
        Add the generated config file from distribution.create_conf_file()
        to the list of outputs.
        """
        outs = super(MyInstall, self).get_outputs()
        outs.append(self.distribution.get_conf_filename(self.install_lib))
        return outs


class MyInstallData (install_data, object):
    """My own data installer to handle permissions."""

    def run (self):
        """Install .mo files and adjust permissions on POSIX systems."""
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


class MyUninstall (Command):
    description = "Remove all installed files"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def get_command_name(self):
        return 'uninstall'

    def run(self):
        global INSTALL_LIST
        if not os.path.isfile(INSTALL_LIST):
            self.announce("Unable to uninstall, can't find the file list %s." % INSTALL_LIST)
            return
        # Suck in the file list.
        fd = open(INSTALL_LIST,'r')
        try:
            file_list = fd.readlines()
        finally:
            fd.close()
        # Remove the files first.
        for item in file_list:
            item = item.strip()
            if os.path.isfile(item) or os.path.islink(item):
                self.announce("removing '%s'" % item)
                if not self.dry_run:
                    try:
                        os.remove(item)
                    except OSError, details:
                        self.warn("Could not remove file: %s" % details)
            elif not os.path.isdir(item):
                self.announce("skipping removal of '%s' (does not exist)" % item)
        # Remove the directories.
        file_list.sort()
        file_list.reverse()
        # Starting with the longest paths first.
        for item in file_list:
            item = item.strip()
            if os.path.isdir(item):
                self.announce("removing '%s'" % item)
                if not self.dry_run:
                    try:
                        os.rmdir(item)
                    except OSError, details:
                        self.warn("Could not remove directory: %s" % details)


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
        distutils.util.execute(write_file, (filename, data),
                     "creating %s" % filename, self.verbose>=1, self.dry_run)


def cc_run (args):
    """Run the C compiler with a simple main program.

    @return: successful exit flag
    @rtype: bool
    """
    prog = "int main(){}\n"
    pipe = subprocess.Popen(args,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
    pipe.communicate(input=prog)
    if os.WIFEXITED(pipe.returncode):
        return os.WEXITSTATUS(pipe.returncode) == 0
    return False


def cc_supports_option (cc, option):
    """Check if the given C compiler supports the given option.

    @return: True if the compiler supports the option, else False
    @rtype: bool
    """
    return cc_run([cc[0], "-E", option, "-"])


def cc_remove_option (compiler, option):
    for optlist in (compiler.compiler, compiler.compiler_so):
        if option in optlist:
            optlist.remove(option)


def cc_has_library (cc, lib):
    return cc_run([cc[0], "-x", "c", "-l", lib, "-"])


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
        # For gcc >= 4.1 we can add -fstack-protector
        extra = []
        libs = []
        if self.compiler.compiler_type == 'unix':
            if cc_supports_option(self.compiler.compiler, "-std=gnu99"):
                extra.append("-std=gnu99")
            if cc_supports_option(self.compiler.compiler, "-fstack-protector") and \
               cc_has_library(self.compiler.compiler, "ssp_nonshared") and \
               cc_has_library(self.compiler.compiler, "ssp"):
                extra.append("-fstack-protector")
                libs.append("ssp_nonshared")
                libs.append("ssp")

        # First, sanity-check the 'extensions' list
        self.check_extensions_list(self.extensions)
        for ext in self.extensions:
            for opt in extra:
                if opt not in ext.extra_compile_args:
                    ext.extra_compile_args.append(opt)
            for lib in libs:
                if lib not in ext.libraries:
                    ext.libraries.append(lib)
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
    distutils.log.info("upx-compressing %s", filename)
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
    Snatched from roundup.sourceforge.net.
    Check that the files listed in the MANIFEST are present when the
    source is unpacked.
    """
    try:
        f = open('MANIFEST')
    except (IOError, OSError):
        print '\n*** SOURCE WARNING: The MANIFEST file is missing!'
        return
    try:
        manifest = [l.strip() for l in f.readlines()]
    finally:
        f.close()
    err = [line for line in manifest if not os.path.exists(line)]
    if err:
        n = len(manifest)
        print '\n*** SOURCE WARNING: There are files missing (%d/%d found)!' \
              % (n - len(err), n)
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
                distutils.log.info("compiling %s -> %s" % (_src, _build_dst))
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
                distutils.log.warn("'%s' does not exist -- can't clean it",
                                   directory)
        clean.run(self)


class MySdist (sdist, object):
    """
    Custom sdist command.
    """

    def get_file_list (self):
        super(MySdist, self).get_file_list()
        self.filelist.append("MANIFEST")


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
              define_macros = define_macros + [('YY_NO_INPUT', None)],
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

# network module
extensions.append(Extension("wc.network._network",
                  sources = [normpath("wc/network/_network.c"),],
                  include_dirs = include_dirs,
                  define_macros = define_macros,
                  extra_compile_args = extra_compile_args,
                  library_dirs = library_dirs,
                  libraries = libraries,
                  ))

# javascript extension
#if os.name == 'nt':
#    define_macros = [('WIN32', None),
#                     ('XP_WIN', None),
#                     ('EXPORT_JS_API', None),
#                    ]
#else:
define_macros = []
extensions.append(Extension('wc.js.jslib',
                  sources=[normpath('wc/js/jslib.c')],
                  include_dirs = include_dirs + ['libjs'],
                  define_macros = define_macros,
                  extra_compile_args = extra_compile_args,
                  extra_objects = [normpath('libjs/.libs/libjs.a')],
                  library_dirs = library_dirs,
                  libraries = libraries,
                 ))

# scripts
scripts = [
    'webcleaner',
    'webcleaner-certificates',
]
#if win_compiling:
#    scripts.append('install-webcleaner.py')

data_files = [
     ('share/webcleaner/config',
      glob.glob('config/*.zap')),
     ('share/webcleaner/config',
      ['config/webcleaner.conf',
       'config/webcleaner.dtd',
       'config/filter.dtd',
       'config/logging.conf',
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
      ['config/blacklists/violence/domains.gz',
       'config/blacklists/violence/urls.gz']),
     ('share/webcleaner/templates/classic',
      glob.glob('templates/classic/*.html')),
     ('share/webcleaner/templates/classic',
      glob.glob('templates/classic/*.png')),
     ('share/webcleaner/templates/classic',
      ['templates/classic/blocked.js',
       'templates/classic/blocked.swf',
       'templates/classic/favicon.ico',
       'templates/classic/pi.js',
       'templates/classic/robots.txt',
       'templates/classic/wc.css',
      ]),
     ('share/webcleaner/templates/classic/macros',
      glob.glob('templates/classic/macros/*.html')),
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
       version = "2.42",
       description = "a filtering HTTP proxy",
       keywords = "proxy,server,http,filters,daemon",
       author = myname,
       author_email = myemail,
       maintainer = myname,
       maintainer_email = myemail,
       url = "http://webcleaner.sourceforge.net/",
       download_url = \
               "http://sourceforge.net/project/showfiles.php?group_id=7692",
       license = "GPL",
       # Note: don't install test modules
       packages = find_packages(exclude=("tests", "*.tests", "*.tests.*")),
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
                   'uninstall' : MyUninstall,
                   'build_ext': MyBuildExt,
                   'build': MyBuild,
                   'clean': MyClean,
                   'sdist': MySdist,
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
