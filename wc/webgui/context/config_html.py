# -*- coding: iso-8859-1 -*-
# be sure not to import something in the context namespace we do not want
import base64
from wc import AppName, filtermodules, ip, Version, config
from wc import sort_seq as _sort_seq
from wc import daemon as _daemon
from wc.webgui.context import getval as _getval
from wc.webgui.context import getlist as _getlist

# config vars
info = {}
error = {}
config['filterdict'] = {}
for _i in filtermodules:
    config['filterdict'][_i] = False
for _i in config['filters']:
    config['filterdict'][_i] = True
config['allowedhostlist'] = _sort_seq(ip.map2hosts(config['allowedhosts']))
config['nofilterhostlist'] = _sort_seq(ip.map2hosts(config['nofilterhosts']))
filterenabled = ""
filterdisabled = ""

# form execution
def _exec_form (form):
    # reset info/error
    global filterenabled, filterdisabled
    filterenabled = ""
    filterdisabled = ""
    info.clear()
    error.clear()
    res = [None]
    # proxy port
    if form.has_key('port'):
        _form_proxyport(_getval(form, 'port'))
    elif config['port']!=8080:
        _form_proxyport(8080)
    # proxy user
    if form.has_key('proxyuser'):
        _form_proxyuser(_getval(form, 'proxyuser').strip(), res)
    elif config['proxyuser']:
        config['proxyuser'] = ''
        info['proxyuser'] = True
    # proxy pass
    if form.has_key('proxypass'):
        val = _getval(form, 'proxypass')
        # ignore dummy values
        if val!='__dummy__':
            _form_proxypass(base64.encodestring(val).strip(), res)
    elif config['proxypass']:
        config['proxypass'] = ''
        info['proxypass'] = True
        if config['proxyuser']:
            res[0] = 407
    # ntlm authentication
    if form.has_key('auth_ntlm'):
        if not config['auth_ntlm']:
            config['auth_ntlm'] = 1
            info['auth_ntlm'] = True
    elif config['auth_ntlm']:
        config['auth_ntlm'] = 0
        info['auth_ntlm'] = True
    # use google cache
    if form.has_key('try_google'):
        if not config['try_google']:
            config['try_google'] = 1
            info['try_google'] = True
    elif config['try_google']:
        config['try_google'] = 0
        info['try_google'] = True
    # parent proxy host
    if form.has_key('parentproxy'):
        _form_parentproxy(_getval(form, 'parentproxy').strip())
    elif config['parentproxy']:
        config['parentproxy'] = ''
        info['parentproxy'] = True
    # parent proxy port
    if form.has_key('parentproxyport'):
        _form_parentproxyport(_getval(form, 'parentproxyport'))
    elif config['parentproxyport'] != 3128:
        config['parentproxyport'] = 3128
        info['parentproxyport'] = True
    # parent proxy user
    if form.has_key('parentproxyuser'):
        _form_parentproxyuser(_getval(form, 'parentproxyuser').strip())
    elif config['parentproxyuser']:
        config['parentproxyuser'] = ''
        info['parentproxyuser'] = True
    # parent proxy pass
    if form.has_key('parentproxypass'):
        val = _getval(form, 'parentproxypass')
        # ignore dummy values
        if val!='__dummy__':
            _form_parentproxypass(base64.encodestring(val).strip())
    elif config['parentproxypass']:
        config['parentproxypass'] = ''
        info['parentproxypass'] = True
    # timeout
    if form.has_key('timeout'):
        _form_timeout(_getval(form, 'timeout'))
    elif config['timeout']!=30:
        config['timeout'] = 30
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
        _form_delnofilter(form)
    return res[0]



def _form_proxyport (port):
    try:
        port = int(port)
        if port != config['port']:
            # note: port change takes effect after restart
            oldport = config['port']
            config['port'] = port
            config.write_proxyconf()
            config['port'] = oldport
            info['port'] = True
    except ValueError:
        error['port'] = True


def _form_proxyuser (proxyuser, res):
    if proxyuser != config['proxyuser']:
        config['proxyuser'] = proxyuser
        config.write_proxyconf()
        info['proxyuser'] = True
        res[0] = 407


def _form_proxypass (proxypass, res):
    if proxypass != config['proxypass']:
        config['proxypass'] = proxypass
        config.write_proxyconf()
        info['proxypass'] = True
        if config['proxyuser']:
            res[0] = 407


def _form_parentproxy (parentproxy):
    if parentproxy != config['parentproxy']:
        config['parentproxy'] = parentproxy
        config.write_proxyconf()
        info['parentproxy'] = True


def _form_parentproxyport (parentproxyport):
    try:
        parentproxyport = int(parentproxyport)
        if parentproxyport != config['parentproxyport']:
            config['parentproxyport'] = parentproxyport
            config.write_proxyconf()
            info['parentproxyport'] = True
    except ValueError:
        error['parentproxyport'] = True


def _form_parentproxyuser (parentproxyuser):
    if parentproxyuser != config['parentproxyuser']:
        config['parentproxyuser'] = parentproxyuser
        config.write_proxyconf()
        info['parentproxyuser'] = True


def _form_parentproxypass (parentproxypass):
    if parentproxypass != config['parentproxypass']:
        config['parentproxypass'] = parentproxypass
        config.write_proxyconf()
        info['parentproxypass'] = True


def _form_timeout (timeout):
    try:
        timeout = int(timeout)
        if timeout != config['timeout']:
            config['timeout'] = timeout
            config.write_proxyconf()
            info['timeout'] = True
    except ValueError:
        error['timeout'] = True


def _form_filtermodules (form):
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
    global filterenabled, filterdisabled
    filterenabled = ", ".join(enabled)
    filterdisabled = ", ".join(disabled)


def _form_addallowed (host):
    hosts = ip.map2hosts(config['allowedhosts'])
    if host not in hosts:
        hosts.add(host)
        config['allowedhosts'] = ip.hosts2map(hosts)
        config['allowedhostlist'] = _sort_seq(hosts)
        info['addallowed'] = True
        config.write_proxyconf()


def _form_removehosts (form, key):
    toremove = _getlist(form, key)
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
        config['allowedhostlist'] = _sort_seq(hosts)
        config.write_proxyconf()
        info['delallowed'] = True


def _form_addnofilter (host):
    hosts = ip.map2hosts(config['nofilterhosts'])
    if host not in hosts:
        hosts.add(host)
        config['nofilterhosts'] = ip.hosts2map(hosts)
        config['nofilterhostlist'] = _sort_seq(hosts)
        config.write_proxyconf()
        info['addnofilter'] = True


def _form_delnofilter (form):
    removed, hosts = _form_removehosts(form, 'nofilterhosts')
    if removed > 0:
        config['nofilterhosts'] = ip.hosts2map(hosts)
        config['nofilterhostlist'] = _sort_seq(hosts)
        config.write_proxyconf()
        info['delnofilter'] = True

