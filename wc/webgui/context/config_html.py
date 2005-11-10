# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2005  Bastian Kleineidam
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
Parameters for config.html page.
"""

# be sure not to import something in the context namespace we do not want
import base64
import socket
import os
from wc import AppName, Version, HasSsl
from wc.configuration import config, filtermodules
from wc.webgui.context import getval as _getval
from wc.webgui.context import getlist as _getlist
from wc.ip import hosts2map as _hosts2map
from wc.proxy.dns_lookups import resolver as _resolver
from wc.strformat import is_ascii as _is_ascii
import wc.filter

# config vars
info = {
    'adminuser': False,
    'adminpass': False,
    'proxyuser': False,
    'proxypass': False,
    'clamavconf': False,
    'auth_ntlm': False,
    'try_google': False,
    'parentproxy': False,
    'parentproxyport': False,
    'parentproxyuser': False,
    'parentproxypass': False,
    'timeout': False,
    'bindaddress': False,
    'port': False,
    'sslport': False,
    'sslgateway': False,
    'addallowed': False,
    'delallowed': False,
    'addnofilter': False,
    'delnofilter': False,
}
error = {
    'port': False,
    'sslport': False,
    'parentproxyport': False,
    'timeout': False,
    'addallowed': False,
    'adminuser': False,
    'adminpass': False,
    'proxyuser': False,
    'proxypass': False,
    'parentproxyuser': False,
    'parentproxypass': False,
}
config['filterdict'] = {}
config['filterenable'] = {}
for _i in filtermodules:
    config['filterdict'][_i] = False
    # import filter module
    exec "from wc.filter import %s" % _i
    # Filter class has same name as module.
    _clazz = getattr(getattr(wc.filter, _i), _i)
    config['filterenable'][_i] = _clazz.enable
for _i in config.get('filters', []):
    config['filterdict'][_i] = True
config['newbindaddress'] = config.get('bindaddress', '')
config['newport'] = config.get('port', 8080)
config['newsslport'] = config.get('sslport', 8443)
config['newsslgateway'] = config.get('sslgateway', 0)
filterenabled = u""
filterdisabled = u""
ifnames = []
ifvalues = {'all_hosts': config['newbindaddress'] == ""}
for _i in _resolver.interfaces:
    ifnames.append(_i)
    ifvalues[_i] = _i == config['newbindaddress']


# default clamav configs for various platforms
if os.name == 'posix':
    clamavconf = "/etc/clamav/clamd.conf"
elif os.name == 'nt':
    clamavconf = r"c:\clamav-devel\etc\clamd.conf"
else:
    clamavconf = "clamd.conf"


def _form_reset ():
    """
    Reset info/error and global variables.
    """
    global filterenabled, filterdisabled
    filterenabled = u""
    filterdisabled = u""
    for key in info.keys():
        info[key] = False
    for key in error.keys():
        error[key] = False


# form execution
def _exec_form (form, lang):
    """
    HTML CGI form handling.
    """
    res = [None]
    # bind address
    if form.has_key('bindaddress'):
        _form_bindaddress(_getval(form, 'bindaddress'))
    # proxy port
    if form.has_key('port'):
        _form_proxyport(_getval(form, 'port'))
    elif config['port'] != 8080:
        _form_proxyport(8080)
    # ssl server port
    if form.has_key('sslport'):
        _form_sslport(_getval(form, 'sslport'))
    elif config['sslport'] != 8443:
        _form_sslport(8443)
    # ssl gateway
    if form.has_key('sslgateway'):
        _form_sslgateway(1)
    else:
        _form_sslgateway(0)
    # admin user
    if form.has_key('adminuser'):
        _form_adminuser(_getval(form, 'adminuser').strip(), res)
    elif config['adminuser']:
        config['adminuser'] = u''
        config.write_proxyconf()
        info['adminuser'] = True
    # admin pass
    if form.has_key('adminpass'):
        val = _getval(form, 'adminpass')
        # ignore dummy values
        if val != u'__dummy__':
            _form_adminpass(base64.b64encode(val), res)
    elif config['adminpass']:
        config['adminpass'] = u''
        config.write_proxyconf()
        info['adminpass'] = True
        if config['adminuser']:
            res[0] = 401
    # proxy user
    if form.has_key('proxyuser'):
        _form_proxyuser(_getval(form, 'proxyuser').strip())
    elif config['proxyuser']:
        config['proxyuser'] = u''
        config.write_proxyconf()
        info['proxyuser'] = True
    # proxy pass
    if form.has_key('proxypass'):
        val = _getval(form, 'proxypass')
        # ignore dummy values
        if val != u'__dummy__':
            _form_proxypass(base64.b64encode(val))
    elif config['proxypass']:
        config['proxypass'] = u''
        config.write_proxyconf()
        info['proxypass'] = True
    # ClamAV config
    if form.has_key('clamav_conf'):
        _form_clamavconf(_getval(form, 'clamav_conf').strip())
    elif config['clamavconf']:
        config['clamavconf'] = ""
        config.write_proxyconf()
        info['clamavconf'] = True
    # ntlm authentication
    if form.has_key('auth_ntlm'):
        if not config['auth_ntlm']:
            config['auth_ntlm'] = 1
            config.write_proxyconf()
            info['auth_ntlm'] = True
    elif config['auth_ntlm']:
        config['auth_ntlm'] = 0
        config.write_proxyconf()
        info['auth_ntlm'] = True
    # use google cache
    if form.has_key('try_google'):
        if not config['try_google']:
            config['try_google'] = 1
            config.write_proxyconf()
            info['try_google'] = True
    elif config['try_google']:
        config['try_google'] = 0
        config.write_proxyconf()
        info['try_google'] = True
    # parent proxy host
    if form.has_key('parentproxy'):
        _form_parentproxy(_getval(form, 'parentproxy').strip())
    elif config['parentproxy']:
        config['parentproxy'] = u''
        config.write_proxyconf()
        info['parentproxy'] = True
    # parent proxy port
    if form.has_key('parentproxyport'):
        _form_parentproxyport(_getval(form, 'parentproxyport'))
    elif config['parentproxyport'] != 3128:
        config['parentproxyport'] = 3128
        config.write_proxyconf()
        info['parentproxyport'] = True
    # parent proxy user
    if form.has_key('parentproxyuser'):
        _form_parentproxyuser(_getval(form, 'parentproxyuser').strip())
    elif config['parentproxyuser']:
        config['parentproxyuser'] = u''
        config.write_proxyconf()
        info['parentproxyuser'] = True
    # parent proxy pass
    if form.has_key('parentproxypass'):
        val = _getval(form, 'parentproxypass')
        # ignore dummy values
        if val != u'__dummy__':
            _form_parentproxypass(base64.b64encode(val))
    elif config['parentproxypass']:
        config['parentproxypass'] = u''
        config.write_proxyconf()
        info['parentproxypass'] = True
    # timeout
    if form.has_key('timeout'):
        _form_timeout(_getval(form, 'timeout'))
    elif config['timeout']!=30:
        config['timeout'] = 30
        config.write_proxyconf()
        info['timeout'] = True
    # filter modules
    _form_filtermodules(form)
    # allowed hosts
    if form.has_key('addallowed') and form.has_key('newallowed'):
        _form_addallowed(_getval(form, 'newallowed').strip())
    elif form.has_key('delallowed') and form.has_key('allowedhosts'):
        _form_delallowed(form)
    # no filter hosts
    if form.has_key('addnofilter') and form.has_key('newnofilter'):
        _form_addnofilter(_getval(form, 'newnofilter').strip())
    elif form.has_key('delnofilter') and form.has_key('nofilterhosts'):
        _form_delnofilter(_getlist(form, 'nofilterhosts'))
    # nofilter shortcut: disable all filtering
    if form.has_key('disablefilter'):
        _form_addnofilter('1.1.1.1/0')
    elif form.has_key('enablefilter'):
        _form_delnofilter(['1.1.1.1/0'])
    return res[0]


def _form_bindaddress (addr):
    """
    Form handling for bind address changes.
    """
    if addr != config['newbindaddress']:
        # note: bind address change takes effect after restart
        config['newbindaddress'] = addr
        oldaddr = config['bindaddress']
        config['bindaddress'] = addr
        config.write_proxyconf()
        config['bindaddress'] = oldaddr
        info['bindaddress'] = True


def _form_proxyport (port):
    """
    Form handling for proxy port changes.
    """
    try:
        port = int(port)
        if port != config['newport']:
            # note: port change takes effect after restart
            config['newport'] = port
            oldport = config['port']
            config['port'] = port
            config.write_proxyconf()
            config['port'] = oldport
            info['port'] = True
    except ValueError:
        error['port'] = True


def _form_sslport (port):
    """
    Form handling for proxy SSL port changes.
    """
    try:
        port = int(port)
        if port != config['newsslport']:
            # note: port change takes effect after restart
            config['newsslport'] = port
            oldport = config['sslport']
            config['sslport'] = port
            config.write_proxyconf()
            config['sslport'] = oldport
            info['sslport'] = True
    except ValueError:
        error['sslport'] = True


def _form_sslgateway (enable):
    """
    Form handling for SSL gateway flag changes.
    """
    if enable != config['newsslgateway']:
        config['newsslgateway'] = enable
        oldval = config['sslgateway']
        config['sslgateway'] = enable
        config.write_proxyconf()
        config.check_ssl_certificates()
        config['sslgateway'] = oldval
        info['sslgateway'] = True


def _form_adminuser (adminuser, res):
    """
    Form handling for admin user changes.
    """
    if not _is_ascii(adminuser):
        error['adminuser'] = True
    elif adminuser != config['adminuser']:
        config['adminuser'] = adminuser
        config.write_proxyconf()
        info['adminuser'] = True
        res[0] = 401


def _form_adminpass (adminpass, res):
    """
    Form handling for admin password changes.
    """
    if not _is_ascii(adminpass):
        error['adminpass'] = True
    elif adminpass != config['adminpass']:
        config['adminpass'] = adminpass
        config.write_proxyconf()
        info['adminpass'] = True
        if config['adminuser']:
            res[0] = 401


def _form_proxyuser (proxyuser):
    """
    Form handling for proxy user changes.
    """
    if not _is_ascii(proxyuser):
        error['proxyuser'] = True
    elif proxyuser != config['proxyuser']:
        config['proxyuser'] = proxyuser
        config.write_proxyconf()
        info['proxyuser'] = True


def _form_proxypass (proxypass):
    """
    Form handling for proxy password changes.
    """
    if not _is_ascii(proxypass):
        error['proxypass'] = True
    elif proxypass != config['proxypass']:
        config['proxypass'] = proxypass
        config.write_proxyconf()
        info['proxypass'] = True


def _form_clamavconf (clamavconf):
    """
    Form handling for clamav config changes.
    """
    if clamavconf != config['clamavconf']:
        config['clamavconf'] = clamavconf
        config.write_proxyconf()
        info['clamavconf'] = True


def _form_parentproxy (parentproxy):
    """
    Form handling for parent proxy host changes.
    """
    if parentproxy != config['parentproxy']:
        config['parentproxy'] = parentproxy
        config.write_proxyconf()
        info['parentproxy'] = True


def _form_parentproxyport (parentproxyport):
    """
    Form handling for parent proxy port changes.
    """
    try:
        parentproxyport = int(parentproxyport)
        if parentproxyport != config['parentproxyport']:
            config['parentproxyport'] = parentproxyport
            config.write_proxyconf()
            info['parentproxyport'] = True
    except ValueError:
        error['parentproxyport'] = True


def _form_parentproxyuser (parentproxyuser):
    """
    Form handling for parent proxy user changes.
    """
    if not _is_ascii(parentproxyuser):
        error['parentproxyuser'] = True
    elif parentproxyuser != config['parentproxyuser']:
        config['parentproxyuser'] = parentproxyuser
        config.write_proxyconf()
        info['parentproxyuser'] = True


def _form_parentproxypass (parentproxypass):
    """
    Form handling for parent proxy password changes.
    """
    if not _is_ascii(parentproxypass):
        error['parentproxypass'] = True
    elif parentproxypass != config['parentproxypass']:
        config['parentproxypass'] = parentproxypass
        config.write_proxyconf()
        info['parentproxypass'] = True


def _form_timeout (timeout):
    """
    Form handling for timeout value changes.
    """
    try:
        timeout = int(timeout)
        if timeout != config['timeout']:
            config['timeout'] = timeout
            config.write_proxyconf()
            info['timeout'] = True
    except ValueError:
        error['timeout'] = True


def _form_filtermodules (form):
    """
    Form handling for filter module list changes.
    """
    newfilters = []
    for key in form.keys():
        if key.startswith('filter'):
            newfilters.append(key[6:])
    enabled = []
    disabled = []
    for m in filtermodules:
        if m in newfilters and m not in config['filters']:
            config['filters'].append(m)
            config['filters'].sort()
            config['filterdict'][m] = True
            enabled.append(m)
        if m not in newfilters and m in config['filters']:
            config['filters'].remove(m)
            config['filters'].sort()
            config['filterdict'][m] = False
            disabled.append(m)
    if enabled or disabled:
        config.write_proxyconf()
    global filterenabled, filterdisabled
    filterenabled = u", ".join(enabled)
    filterdisabled = u", ".join(disabled)


def _form_addallowed (host):
    """
    Form handling for allowed host list additions.
    """
    if host not in config['allowedhosts']:
        try:
            hosts = config['allowedhosts'][:]
            hosts.append(host)
            hostset = _hosts2map(hosts)
            config['allowedhostset'] = hostset
            config['allowedhosts'] = hosts
            info['addallowed'] = True
            config.write_proxyconf()
        except socket.error:
            error['addallowed'] = True


def _form_delallowed (form):
    """
    Form handling for allowed host list deletions.
    """
    removed = 0
    for host in _getlist(form, 'allowedhosts'):
        if host in config['allowedhosts']:
            config['allowedhosts'].remove(host)
            removed += 1
    if removed > 0:
        config['allowedhostset'] = _hosts2map(config['allowedhosts'])
        config.write_proxyconf()
        info['delallowed'] = True


def _form_addnofilter (host):
    """
    Form handling for nofilter host list additions.
    """
    if host not in config['nofilterhosts']:
        config['nofilterhosts'].append(host)
        config.write_proxyconf()
        info['addnofilter'] = True


def _form_delnofilter (hosts):
    """
    Form handling for nofilter host list deletions.
    """
    removed = 0
    for host in hosts:
        if host in config['nofilterhosts']:
            config['nofilterhosts'].remove(host)
            removed += 1
    if removed > 0:
        config.write_proxyconf()
        info['delnofilter'] = True
