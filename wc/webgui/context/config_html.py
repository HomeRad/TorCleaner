# -*- coding: iso-8859-1 -*-
# be sure not to import something in the context namespace we do not want
import base64
from wc import i18n, AppName, filtermodules, ip, sort_seq
from wc import Configuration as _Configuration
from wc.webgui.context import getval, getlist

# translations
title = i18n._("%s proxy configuration") % AppName
t_webcleaner = AppName
t_proxyconf = i18n._("Proxy configuration")
t_filterconf = i18n._("Filter configuration")
port = i18n._("Port number")
proxyuser = i18n._("Proxy user")
proxypass = i18n._("Proxy password")
parentproxy = i18n._("Parent proxy")
parentproxyport = i18n._("Parent proxy port")
parentproxyuser = i18n._("Parent proxy user")
parentproxypass = i18n._("Parent proxy pass")
timeout = i18n._("Timeout (seconds)")
proxyfiltermodules = i18n._("Proxy filter modules")
allowedhosts = i18n._("Allowed hosts")
remove = i18n._("Remove selected")
add = i18n._("Add new")
nofilterhosts = i18n._("Don't filter hosts")
configapply = i18n._("Apply")
back = i18n._("Back")

# config vars
info = []
error = []
config = _Configuration()
for _i in ['port', 'parentproxyport', 'timeout']:
    config["str"+_i] = str(config[_i])
config['filterdict'] = {}
for _i in filtermodules:
    config['filterdict'][_i] = False
for _i in config['filters']:
    config['filterdict'][_i] = True
config['allowedhostlist'] = sort_seq(ip.map2hosts(config['allowedhosts']))
config['nofilterhostlist'] = sort_seq(ip.map2hosts(config['nofilterhosts']))


# form execution
def exec_form (form):
    # reset info/error
    del info[:]
    del error[:]
    # proxy port
    if form.has_key('port'):
        _form_proxyport(getval(form, 'port'))
    # proxy user
    if form.has_key('proxyuser'):
        _form_proxyuser(getval(form, 'proxyuser').strip())
    # proxy pass
    if form.has_key('proxypass'):
        _form_proxypass(base64.encodestring(getval(form, 'proxypass').strip()))
    # parent proxy host
    if form.has_key('parentproxy'):
        _form_parentproxy(getval(form, 'parentproxy').strip())
    # parent proxy port
    if form.has_key('parentproxyport'):
        _form_parentproxyport(getval(form, 'parentproxyport'))
    # parent proxy user
    if form.has_key('parentproxyuser'):
        _form_parentproxyuser(getval(form, 'parentproxyuser').strip())
    # parent proxy pass
    if form.has_key('parentproxypass'):
        _form_parentproxypass(
                       base64.encodestring(getval(form, 'parentproxypass')))
    # timeout
    if form.has_key('timeout'):
        _form_timeout(getval(form, 'timeout'))
    # filter modules
    _form_filtermodules(form)
    # allowed hosts
    if form.has_key('addallowed') and form.has_key('newallowed'):
        _form_addallowed(getval(form, 'newallowed').strip())
    elif form.has_key('delallowed') and form.has_key('allowedhosts'):
        _form_delallowed(form)
    # no filter hosts
    if form.has_key('addnofilter') and form.has_key('newnofilter'):
        _form_addnofilter(getval(form, 'newnofilter').strip())
    elif form.has_key('delnofilter') and form.has_key('nofilterhosts'):
        _form_delnofilter(form)
    if info:
        # write changed config
        config.write_proxyconf()


def _form_proxyport (port):
    try:
        port = int(port)
        if port != config['port']:
            config['port'] = port
            info.append(i18n._("Port successfully changed"))
    except ValueError:
        error.append(i18n._("Invalid proxy port"))


def _form_proxyuser (proxyuser):
    if proxyuser != config['proxyuser']:
        config['proxyuser'] = proxyuser
        info.append(i18n._("Proxy user successfully changed"))


def _form_proxypass (proxypass):
    if proxypass != config['proxypass']:
        config['proxypass'] = proxypass
        info.append(i18n._("Proxy password successfully changed"))


def _form_parentproxy (parentproxy):
    if parentproxy != config['parentproxy']:
        config['parentproxy'] = parentproxy
        info.append(i18n._("Parent proxy successfully changed"))


def _form_parentproxyport (parentproxyport):
    try:
        parentproxyport = int(parentproxyport)
        if parentproxyport != config['parentproxyport']:
            config['parentproxyport'] = parentproxyport
            info.append(i18n._("Parent proxy port successfully changed"))
    except ValueError:
        error.append(i18n._("Invalid parent proxy port"))


def _form_parentproxyuser (parentproxyuser):
    if parentproxyuser != config['parentproxyuser']:
        config['parentproxyuser'] = parentproxyuser
        info.append(i18n._("Parent proxy user successfully changed"))


def _form_parentproxypass (parentproxypass):
    if parentproxypass != config['parentproxypass']:
        config['parentproxypass'] = parentproxypass
        info.append(i18n._("Parent proxy password successfully changed"))


def _form_timeout (timeout):
    try:
        timeout = int(timeout)
        if timeout != config['timeout']:
            config['timeout'] = timeout
            info.append(i18n._("Timeout sucessfully changed"))
    except valueError:
        error.append(i18n._("Invalid timeout value"))


def _form_filtermodules (form):
    newfilters = []
    for key in form.keys():
        if key.startswith('filter'):
            newfilters.append(key[6:])
    for m in filtermodules:
        if m in newfilters and m not in config['filters']:
            config['filters'].append(m)
            config['filters'].sort()
            config['filterdict'][m] = True
            info.append(i18n._("Enabled filter modules %s") % m)
        if m not in newfilters and m in config['filters']:
            config['filters'].remove(m)
            config['filters'].sort()
            config['filterdict'][m] = False
            info.append(i18n._("Disabled filter modules %s") % m)


def _form_addallowed (host):
    hosts = ip.map2hosts(config['allowedhosts'])
    if host not in hosts:
        hosts.add(host)
        config['allowedhosts'] = ip.hosts2map(hosts)
        config['allowedhostlist'] = sort_seq(hosts)
        info.append(i18n._("Allowed host successfully added"))


def _form_removehosts (form, key):
    toremove = getlist(form, key)
    hosts = ip.map2hosts(config[key])
    removed = 0
    for host in toremove:
        if host in hosts:
            hosts.remove(host)
            removed += 1
    return removed, hosts


def _form_delallowed (form):
    removed, hosts = _form_removehosts(form, 'allowedhosts')
    if removed > 0:
        config['allowedhosts'] = ip.hosts2map(hosts)
        config['allowedhostlist'] = sort_seq(hosts)
        if removed == 1:
            info.append(i18n._("Allowed host successfully removed"))
        else:
            info.append(i18n._("%d allowed hosts successfully removed") % \
                        removed)


def _form_addnofilter (host):
    hosts = ip.map2hosts(config['nofilterhosts'])
    if host not in hosts:
        hosts.add(host)
        config['nofilterhosts'] = ip.hosts2map(hosts)
        config['nofilterhostlist'] = sort_seq(hosts)
        info.append(i18n._("Nofilter host successfully added"))


def _form_delnofilter (form):
    removed, hosts = _form_removehosts(form, 'nofilterhosts')
    if removed > 0:
        config['nofilterhosts'] = ip.hosts2map(hosts)
        config['nofilterhostlist'] = sort_seq(hosts)
        if removed == 1:
            info.append(i18n._("Nofilter host successfully removed"))
        else:
            info.append(i18n._("%d nofilter hosts successfully removed") % \
                        removed)

