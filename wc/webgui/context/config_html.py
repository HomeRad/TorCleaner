# -*- coding: iso-8859-1 -*-
# be sure not to import something in the context namespace we do not want
import base64
from wc import i18n, AppName, filtermodules, ip, sort_seq
from wc import Configuration as _Configuration

# translations
title = i18n._("%s configuration") % AppName
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
nofilterhosts = i18n._("No filter hosts")
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

# form execution
def exec_form (form):
    # reset info/error
    del info[:]
    del error[:]
    # proxy port
    if form.has_key('port'):
        _form_proxyport(form['port'].value)
    # proxy user
    if form.has_key('proxyuser'):
        _form_proxyuser(form['proxyuser'].value.strip())
    # proxy pass
    if form.has_key('proxypass'):
        _form_proxypass(base64.encodestring(form['proxypass'].value.strip()))
    # parent proxy host
    if form.has_key('parentproxy'):
        _form_parentproxy(form['parentproxy'].value.strip())
    # parent proxy port
    if form.has_key('parentproxyport'):
        _form_parentproxyport(form['parentproxyport'].value)
    # parent proxy user
    if form.has_key('parentproxyuser'):
        _form_parentproxyuser(form['parentproxyuser'].value.strip())
    # parent proxy pass
    if form.has_key('parentproxypass'):
        _form_parentproxypass(
                       base64.encodestring(form['parentproxypass'].value))
    # timeout
    if form.has_key('timeout'):
        _form_timeout(form['timeout'].value)
    # filter modules
    _form_filtermodules(form)
    # allowed hosts
    if form.has_key('addallowed') and form.has_key('newallowed'):
        _form_addallowed(form['newallowed'].value.strip())
    elif form.has_key('delallowed') and form.has_key('allowedhosts'):
        _form_delallowed(form['allowedhosts'])
    # no filter hosts
    # XXX
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
            config['filterdict'][m] = True
            info.append(i18n._("Enabled filter modules %s") % m)
        if m not in newfilters and m in config['filters']:
            config['filters'].remove(m)
            config['filterdict'][m] = False
            info.append(i18n._("Disabled filter modules %s") % m)


def _form_addallowed (host):
    hosts = ip.map2hosts(config['allowedhosts'])
    if host not in hosts:
        hosts.add(host)
        config['allowedhosts'] = ip.hosts2map(hosts)
        config['allowedhostlist'] = sort_seq(hosts)
        info.append(i18n._("Allowed host successfully added"))


def _form_delallowed (hosts):
    print "del hosts", hosts.value
    # XXX
