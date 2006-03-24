# -*- coding: iso-8859-1 -*-
# snatched from pythoncard CVS
# Documentation is at:
# http://docs.python.org/dist/postinstallation-script.html

# THIS FILE IS ONLY FOR USE WITH MS WINDOWS
# It is run as parts of the bdist_wininst installer
# Be sure to build the installer with
# 'python setup.py --install-script=install-webcleaner.py'
# or insert this into setup.cfg:
# [bdist_wininst]
# install-script=install-webcleaner.py

import sys
if not sys.platform.startswith('win'):
    # not for us
    sys.exit(1)
if not hasattr(sys, "version_info"):
    raise SystemExit, "This program requires Python 2.4 or later."
if sys.version_info < (2, 4, 0, 'final', 0):
    raise SystemExit, "This program requires Python 2.4 or later."
import os
import glob
import time
import webbrowser
import distutils.sysconfig
import win32service
import win32serviceutil
import pywintypes
# dummy translation to calm down source code checkers
_ = lambda s: s


#################### utility functions ####################

def init_tk ():
    """
    Initialize Tk: create a root window and hide it, since only simple
    modal dialogs are used.
    @return: root window
    @rtype: Tkinter.Tk
    """
    import Tkinter as tk
    root = tk.Tk()
    root.withdraw()
    return root


def execute (args):
    """
    Execute command with arguments.
    @return: return code of executed command
    @rtype: int
    """
    # If both the executable and arguments contain spaces, ie. need to
    # be quoted, the only option is to use os.spawnv(). But then
    # the command output is not printable. Bummer. At least we have
    # the return code.
    executable = args[0]
    import wc.win32start
    wc.win32start.nt_quote_args(args)
    return os.spawnv(os.P_WAIT, executable, args)


def state_nt_service (name):
    """
    Return status of NT service.
    """
    try:
        return win32serviceutil.QueryServiceStatus(name)[1]
    except pywintypes.error, msg:
        print _("Service status error: %s") % str(msg)
    return None


def install_service ():
    """
    Install WebCleaner NT service.
    """
    import wc
    import wc.win32start
    oldargs = sys.argv
    print _("Installing %s service...") % wc.AppName
    sys.argv = ['webcleaner', 'install']
    win32serviceutil.HandleCommandLine(wc.win32start.ProxyService)
    sys.argv = oldargs


def remove_service ():
    """
    Remove WebCleaner NT service.
    """
    import wc
    import wc.win32start
    oldargs = sys.argv
    print _("Removing %s service...") % wc.AppName
    sys.argv  = ['webcleaner', 'remove']
    win32serviceutil.HandleCommandLine(wc.win32start.ProxyService)
    sys.argv = oldargs


def start_service ():
    """
    Start WebCleaner NT service.
    """
    import wc
    import wc.win32start
    print _("Starting %s proxy...") % wc.AppName
    oldargs = sys.argv
    sys.argv = ['webcleaner', 'start']
    win32serviceutil.HandleCommandLine(wc.win32start.ProxyService)
    sys.argv = oldargs


def stop_service ():
    """
    Stop WebCleaner NT service (if it is running).
    """
    import wc
    import wc.win32start
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


_wc_config = None
def get_wc_config ():
    """
    Get WebCleaner configuration object.
    """
    global _wc_config
    if _wc_config is None:
        import wc
        _wc_config = wc.configuration.init()
    return _wc_config


#################### installation ####################

def do_install ():
    """
    Install shortcuts and NT service.
    """
    fix_configdata()
    import wc
    # initialize i18n
    wc.init_i18n()
    install_shortcuts()
    install_certificates()
    install_service()
    stop_service()
    install_adminpassword()
    start_service()
    open_browser_config()


def fix_configdata ():
    """
    Fix install and config paths in the config file.
    """
    name = "_webcleaner2_configdata.py"
    conffile = os.path.join(sys.prefix, "Lib", "site-packages", name)
    lines = []
    for line in file(conffile):
        if line.startswith("install_") or \
           line.startswith("config_") or \
           line.startswith("template_"):
            lines.append(fix_install_path(line))
        else:
            lines.append(line)
    f = file(conffile, "w")
    f.write("".join(lines))
    f.close()


# windows install scheme for python >= 2.3
# snatched from PC/bdist_wininst/install.c
# this is used to fix install_* paths when cross compiling for windows
win_path_scheme = {
    "purelib": ("PURELIB", "Lib\\site-packages\\"),
    "platlib": ("PLATLIB", "Lib\\site-packages\\"),
    # note: same as platlib because of C extensions, else it would be purelib
    "lib": ("PLATLIB", "Lib\\site-packages\\"),
    # 'Include/dist_name' part already in archive
    "headers": ("HEADERS", "."),
    "scripts": ("SCRIPTS", "Scripts\\"),
    "data": ("DATA", "."),
}

def fix_install_path (line):
    """
    Replace placeholders written by bdist_wininst with those specified
    in win_path_scheme.
    """
    key, eq, val = line.split()
    # unescape string (do not use eval())
    val = val[1:-1].replace("\\\\", "\\")
    for d in win_path_scheme.keys():
        # look for placeholders to replace
        oldpath, newpath = win_path_scheme[d]
        oldpath = "%s%s" % (os.sep, oldpath)
        if oldpath in val:
            val = val.replace(oldpath, newpath)
            val = os.path.join(sys.prefix, val)
            val = os.path.normpath(val)
    return "%s = %r%s" % (key, val, os.linesep)


def install_shortcuts ():
    """
    create_shortcut(target, description, filename[, arguments[, \
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
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    directory_created(dest_dir)
    # create configuration shortcut
    path = os.path.join(dest_dir, "Configure WebCleaner.URL")
    f = open(path, "w")
    try:
        f.write("[InternetShortcut]\r\n")
        f.write("URL=http://localhost:8080/\r\n")
    finally:
        f.close()
    file_created(path)
    # create uninstall shortcut
    target = os.path.join(sys.prefix, "RemoveWebCleaner.exe")
    path = os.path.join(dest_dir, "Uninstall WebCleaner.lnk")
    arguments = '-u "%s"' % os.path.join(sys.prefix, "WebCleaner-wininst.log")
    create_shortcut(target, _("Uninstall WebCleaner"), path, arguments)
    file_created(path)


def install_certificates ():
    """
    Generate SSL certificates for SSL gateway functionality.
    """
    pythonw = os.path.join(sys.prefix, "pythonw.exe")
    import wc
    script = os.path.join(wc.ScriptDir, "webcleaner-certificates")
    if execute([pythonw, script, "install"]) != 0:
        print _("""Could not install SSL certificates.
Perhaps PyOpenSSL is not installed?
You have to install the SSL certificates manually with
'webcleaner-certificates install'.""")


def install_adminpassword ():
    """
    Ask for admin password if not already set.
    """
    if has_adminpassword():
        # already got one (from wherever that may be)
        return
    import wc
    import Tkinter as tk
    root = init_tk()
    import tkSimpleDialog

    class PasswordDialog (tkSimpleDialog.Dialog):
        """
        Admin password dialog.
        """

        def body(self, master):
            d = {"appname": wc.AppName}
            msg = _("""The administrator password protects the web
configuration frontend of %s.
The default username is "admin" (without the quotes).
You have to enter a non-empty password. If you press cancel,
the administrator password has to be entered manually (don't
worry, the web interface will tell you how to do that).""")
            label = tk.Label(master, text=msg % d, anchor=tk.W, justify=tk.LEFT)
            label.grid(row=0, columnspan=2, sticky=tk.W)
            label = tk.Label(master, text=_("Password:"))
            label.grid(row=1, sticky=tk.W)
            self.pass_entry = tk.Entry(master)
            self.pass_entry.grid(row=1, column=1)
            return self.pass_entry # initial focus

        def apply(self):
            password = self.pass_entry.get()
            if password:
                save_adminpassword(password)
            else:
                print _("Not saving empty password.")

    title = _("%s administrator password") % wc.AppName
    PasswordDialog(root, title=title)


def has_adminpassword ():
    """
    Check if admin password is already set.
    """
    return get_wc_config()["adminpass"]


def save_adminpassword (password):
    """
    Save new admin password to WebCleaner configuration.
    Also checks for invalid password format.
    """
    import base64
    import wc.strformat
    password = base64.b64encode(password)
    if not password or not wc.strformat.is_ascii(password):
        print _("Not saving binary password.")
        return
    config = get_wc_config()
    config["password"] = password
    config.write_proxyconf()


def open_browser_config ():
    """
    Open the WebCleaner administration web interface.
    """
    import wc
    import wc.configuration
    state = state_nt_service(wc.AppName)
    while state==win32service.SERVICE_START_PENDING:
        time.sleep(1)
        state = state_nt_service(wc.AppName)
    # sleep a while to let the proxy start...
    time.sleep(3)
    # open configuration
    config = wc.configuration.init()
    config_url = "http://localhost:%d/" % config['port']
    open_browser(config_url)


def open_browser (url):
    """
    Open a URL in the default browser.
    """
    print _("Opening proxy configuration interface...")
    # The windows webbrowser.open function raises an exception for http://
    # urls, but works nevertheless. Just ignore the error.
    # This is a known bug with browsers not setting up the correct file type
    # associations (ie. FireFox).
    # See also http://mail.python.org/pipermail/python-list/2004-July/228312.html
    try:
        webbrowser.open(url)
    except WindowsError, msg:
        pass


#################### removal ####################

def do_remove ():
    """
    Stop and remove the installed NT service.
    """
    import wc
    # initialize i18n
    wc.init_i18n()
    stop_service()
    remove_service()
    remove_certificates()
    remove_tempfiles()
    purge_tempfiles()
    # make sure empty directories are removed
    remove_empty_directories(wc.ConfigDir)


def remove_certificates ():
    """
    Generate SSL certificates for SSL gateway functionality.
    """
    import wc
    pythonw = os.path.join(sys.prefix, "pythonw.exe")
    script = os.path.join(wc.ScriptDir, "webcleaner-certificates")
    if execute([pythonw, script, "remove"]) != 0:
        print _("""Could not remove SSL certificates.
Perhaps PyOpenSSL is not installed?
You have to remove the SSL certificates manually.""")


def remove_tempfiles ():
    """
    Remove log, custom config files and magic(1) cache file.
    """
    import wc
    remove_file(os.path.join(wc.ConfigDir, "magic.mime.mgc"))
    for pat in ("webcleaner.log*", "webcleaner-access.log*"):
        for fname in glob.glob(os.path.join(wc.ConfigDir, pat)):
            remove_file(fname)


def purge_tempfiles ():
    """
    Ask if user wants to purge local config files.
    """
    import wc
    files = glob.glob(os.path.join(wc.ConfigDir, "local_*.zap"))
    if not files:
        return
    init_tk()
    import tkMessageBox
    answer = tkMessageBox.askyesno(_("%s config purge") % wc.AppName,
         _("""There are local filter rules in the configuration directory.
Do you want to remove them? They can be re-used in other
installations of %s, but are useless otherwise.""") % wc.AppName)
    if answer:
        for fname in files:
            remove_file(fname)


def remove_file (fname):
    """
    Remove a single file if it exists. Errors are printed to stdout.
    """
    if os.path.exists(fname):
        try:
            os.remove(fname)
        except OSError, msg:
            print _("Could not remove file %r: %s") % (fname, str(msg))


def is_empty_dir (name):
    """
    Check if given name is a non-empty directory.
    """
    return os.path.isdir(name) and not os.listdir(name)


def remove_empty_directories (dname):
    """
    Remove empty directory structure.
    """
    try:
        if is_empty_dir(dname):
            os.rmdir(dname)
            remove_empty_directories(os.path.dirname(dname))
    except OSError, msg:
        print _("Could not remove directory %r: %s") % (dname, str(msg))


#################### main ####################
if __name__ == '__main__':
    if "-install" == sys.argv[1]:
        do_install()
    elif "-remove" == sys.argv[1]:
        do_remove()
