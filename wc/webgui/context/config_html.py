# be sure not to import something in the context namespace we do not want
import base64
from wc import i18n, AppName, filtermodules
from wc import Configuration as _Configuration

title = i18n._("%s configuration") % AppName
port = i18n._("Port number")
configapply = i18n._("Apply")
info = []
error = []


def exec_form (form):
    # reset info/error
    del info[:]
    del error[:]
    # read current config (without filter stuff)
    _config = _Configuration()
    # proxy port
    if form.has_key('port'):
        try:
            _port = int(form['port'].value)
            if _port != _config['port']:
                _config['port'] = _port
                info.append(i18n._("Port successfully changed"))
        except ValueError:
            error.append(i18n._("Invalid proxy port"))
    # proxy user
    if form.has_key('proxyuser'):
        _proxyuser = form['proxyuser'].value.strip()
        if _proxyuser != _config['proxyuser']:
            _config['proxyuser'] = _proxyuser
            info.append(i18n._("Proxy user successfully changed"))
    # proxy pass
    if form.has_key('proxypass'):
        _proxypass = base64.encodestring(form['proxypass'].value.strip())
        if _proxypass != _config['proxypass']:
            _config['proxypass'] = _proxypass
            info.append(i18n._("Proxy password successfully changed"))
    # parent proxy host
    if form.has_key('parentproxy'):
        _parentproxy = form['parentproxy'].value.strip()
        if _parentproxy != _config['parentproxy']:
            _config['parentproxy'] = _parentproxy
            info.append(i18n._("Parent proxy successfully changed"))
    # parent proxy port
    if form.has_key('parentproxyport'):
        try:
            _parentproxyport = int(form['parentproxyport'].value)
            if _parentproxyport != _config['parentproxyport']:
                _config['parentproxyport'] = _parentproxyport
                info.append(i18n._("Parent proxy port successfully changed"))
        except ValueError:
            error.append(i18n._("Invalid parent proxy port"))
    # parent proxy user
    if form.has_key('parentproxyuser'):
        _parentproxyuser = form['parentproxyuser'].value.strip()
        if _parentproxyuser != _config['parentproxyuser']:
            _config['parentproxyuser'] = _parentproxyuser
            info.append(i18n._("Parent proxy user successfully changed"))
    # parent proxy pass
    if form.has_key('parentproxypass'):
        _parentproxypass = \
             base64.encodestring(form['parentproxypass'].value.strip())
        if _parentproxypass != _config['parentproxypass']:
            _config['parentproxypass'] = _parentproxypass
            info.append(i18n._("Parent proxy password successfully changed"))
    newmodules = []
    for key in form.keys():
        if key.startswith('filter'):
            newmodules.append(key[6:])
    for m in filtermodules:
        if m in newmodules and m not in _config['filters']:
            _config['filters'].append(m)
            info.append(i18n._("Enabled filter modules %s") % m)
        if m not in newmodules and m in _config['filters']:
            _config['filters'].remove(m)
            info.append(i18n._("Disabled filter modules %s") % m)
    if info:
        # write changed config
        _config.write_proxyconf()

