"""Win32 specific daemon helper functions"""
#    Copyright (C) 2001  Bastian Kleineidam
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

def _find_executable(executable, path=None):
    """Try to find 'executable' in the directories listed in 'path' (a
    string listing directories separated by 'os.pathsep'; defaults to
    os.environ['PATH']).  Returns the complete filename or None if not
    found.
    """
    if path is None:
        path = os.environ['PATH']
    paths = string.split(path, os.pathsep)
    (base, ext) = os.path.splitext(executable)
    if (sys.platform == 'win32') and (ext != '.exe'):
        executable = executable + '.exe'
    if not os.path.isfile(executable):
        for p in paths:
            f = os.path.join(p, executable)
            if os.path.isfile(f):
                # the file exists, we have a shot at spawn working
                return f
        return None
    else:
        return executable


# snatched from distutils
def _nt_quote_args (args):
    """Quote command-line arguments for DOS/Windows conventions: just
    wraps every argument which contains blanks in double quotes, and
    returns a new argument list.
    """

    # XXX this doesn't seem very robust to me -- but if the Windows guys
    # say it'll work, I guess I'll have to accept it.  (What if an arg
    # contains quotes?  What other magic characters, other than spaces,
    # have to be escaped?  Is there an escaping mechanism other than
    # quoting?)

    for i in range(len(args)):
        if string.find(args[i], ' ') != -1:
            args[i] = '"%s"' % args[i]
    return args


def start():
    cmd = sys.args[:]
    cmd[cmd.index('start')] = 'start_nt'
    executable = cmd[0]
    cmd = _nt_quote_args(cmd)
    # either we find one or it stays the same
    executable = _find_executable(executable) or executable
    try:
        ret = os.spawnv(os.P_NOWAIT, executable, cmd)
    except OSError, exc:
        # this seems to happen when the command isn't found
        raise Exception, \
              "command '%s' failed: %s" % (cmd[0], exc[-1])
    if ret != 0:
        # and this reflects the command running but failing
        raise Exception, \
              "command '%s' failed with exit status %d" % (cmd[0], ret)

def start_nt():
    # no need to spawn in this thing
    startfunc()


def stop():
    if not os.path.exists(pidfile):
        print "webcleaner was not running"
        return
    import win32api
    handle = win32api.OpenProcess(1, 0, int(open(pidfile).read()))
    rc = win32api.TerminateProcess(handle, 0)
    os.remove(pidfile)

def reload():
    raise Exception, "Reload not supported for this platform"
