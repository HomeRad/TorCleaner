# -*- coding: iso-8859-1 -*-
# snatched from pythoncard CVS

# THIS FILE IS ONLY FOR USE WITH MS WINDOWS
# It is run as parts of the bdist_wininst installer
# Be sure to build the installer with
# 'python setup.py --install-script=install-linkchecker.py'
# or insert this into setup.cfg:
# [bdist_wininst]
# install-script=install-linkchecker.py

import sys
if not sys.platform.startswith('win'):
    # not for us
    sys.exit()
if sys.version[:5] < "2.3":
    raise SystemExit, "This program requires Python 2.3 or later."
import os
import time
import webbrowser
import distutils.sysconfig
import win32service
import win32serviceutil
import wc
import wc.configuration
# initialize i18n
wc.init_i18n()
import wc.win32start


def execute (pythonw, script, args):
    """execute given script"""
    cargs = " ".join(args)
    _in, _out = os.popen4("%s %s %s" % (pythonw, script, cargs))
    line = _out.readline()
    while line:
        print line
        line = _out.readline()
    _in.close()
    _out.close()


def do_install ():
    """install shortcuts and NT service"""
    install_shortcuts()
    install_certificates()
    install_service()
    restart_service()
    open_browser_config()


def install_shortcuts ():
    """create_shortcut(target, description, filename[, arguments[, \
                     workdir[, iconpath[, iconindex]]]])

       file_created(path)
         - register 'path' so that the uninstaller removes it

       directory_created(path)
         - register 'path' so that the uninstaller removes it

       get_special_folder_location(csidl_string)
    """
    try:
        prg = get_special_folder_path("CSIDL_COMMON_PROGRAMS")
    except OSError:
        try:
            prg = get_special_folder_path("CSIDL_PROGRAMS")
        except OSError, reason:
            # give up - cannot install shortcuts
            print _("Cannot install shortcuts: %s") % reason
            sys.exit()
    lib_dir = distutils.sysconfig.get_python_lib(plat_specific=1)
    dest_dir = os.path.join(prg, "WebCleaner")
    try:
        os.mkdir(dest_dir)
        directory_created(dest_dir)
    except OSError:
        pass
    target = os.path.join(sys.prefix, "RemoveWebCleaner.exe")
    path = os.path.join(dest_dir, "Uninstall WebCleaner.lnk")
    arguments = "-u " + os.path.join(sys.prefix, "WebCleaner-wininst.log")
    create_shortcut(target, _("Uninstall WebCleaner"), path, arguments)
    file_created(path)


def install_certificates ():
    """generate SSL certificates for SSL gateway functionality"""
    pythonw = os.path.join(sys.prefix, "pythonw.exe")
    script = os.path.join(wc.ScriptDir, "webcleaner-certificates")
    execute(pythonw, script, ["install"])


def state_nt_service (name):
    """return status of NT service"""
    return win32serviceutil.QueryServiceStatus(name)[1]


def install_service ():
    """install WebCleaner as NT service"""
    oldargs = sys.argv
    print _("Installing %s service...") % wc.AppName
    sys.argv = ['webcleaner', 'install']
    win32serviceutil.HandleCommandLine(wc.win32start.ProxyService)
    sys.argv = oldargs


def remove_service ():
    oldargs = sys.argv
    print _("Removing %s service...") % wc.AppName
    sys.argv  = ['webcleaner', 'remove']
    win32serviceutil.HandleCommandLine(wc.win32start.ProxyService)
    sys.argv = oldargs


def restart_service ():
    """restart WebCleaner NT service"""
    stop_service()
    start_service()


def stop_service ()
    """stop WebCleaner NT service (if it is running)"""
    print _("Stopping %s proxy...") % wc.AppName
    oldargs = sys.argv
    state = state_nt_service(wc.AppName)
    while state==win32service.SERVICE_START_PENDING:
        time.sleep(1)
        state = state_nt_service(wc.AppName)
    if state==win32service.SERVICE_RUNNING:
        sys.argv = ['webcleaner', 'stop']
        win32serviceutil.HandleCommandLine(wc.win32start.ProxyService)
    state = state_nt_service(wc.AppName)
    while state==win32service.SERVICE_STOP_PENDING:
        time.sleep(1)
        state = state_nt_service(wc.AppName)
    sys.argv = oldargs


def start_service ():
    """start WebCleaner NT service"""
    print _("Starting %s proxy...") % wc.AppName
    oldargs = sys.argv
    sys.argv = ['webcleaner', 'start']
    win32serviceutil.HandleCommandLine(wc.win32start.ProxyService)
    sys.argv = oldargs


def open_browser_config ():
    # sleep a while to let the proxy start...
    state = state_nt_service(wc.AppName)
    while state==win32service.SERVICE_START_PENDING:
        time.sleep(1)
        state = state_nt_service(wc.AppName)
    time.sleep(3)
    # open configuration
    config = wc.configuration.init()
    config_url = "http://localhost:%d/" % config['port']
    open_browser(config_url)


def open_browser (url):
    print _("Opening proxy configuration interface...")
    # the windows webbrowser.open func raises an exception for http://
    # urls, but works nevertheless. Just ignore the error.
    try:
        webbrowser.open(url)
    except WindowsError, msg:
        print _("Could not open webbrowser: %r") % str(msg)


def do_remove ():
    """stop and remove the installed NT service"""
    stop_service()
    remove_service()
    remove_certificates()
    remove_tempfiles()


def remove_certificates ():
    """generate SSL certificates for SSL gateway functionality"""
    pythonw = os.path.join(sys.prefix, "pythonw.exe")
    script = os.path.join(wc.ScriptDir, "webcleaner-certificates")
    execute(pythonw, script, ["remove"])


def remove_tempfiles ():
    """remove log files and magic(1) cache file"""
    remove_file(os.path.join(wc.ConfigDir, "magic.mime.mgc"))
    remove_file(os.path.join(wc.ConfigDir, "webcleaner.log"))
    remove_file(os.path.join(wc.ConfigDir, "webcleaner-access.log"))


def remove_file (fname):
    """Remove a single file if it exists. Errors are printed to stdout"""
    if os.path.exists(fname):
        try:
            os.remove(fname)
        except OSError, msg:
            print _("Could not remove %r: %s") % (fname, str(msg))


if __name__ == '__main__':
    if "-install" == sys.argv[1]:
        do_install()
    elif "-remove" == sys.argv[1]:
        do_remove()
