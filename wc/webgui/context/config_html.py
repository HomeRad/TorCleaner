# be sure not to import something in the context namespace we do not want
import base64
from wc import i18n, AppName, filtermodules
from wc import Configuration as _Configuration

title = i18n._("%s configuration") % AppName
port = i18n._("Port number")
proxyuser = i18n._("Proxy user")
proxypass = i18n._("Proxy password")
parentproxy = i18n._("Parent proxy")
parentproxyport = i18n._("Parent proxy port")
parentproxyuser = i18n._("Parent proxy user")
parentproxypass = i18n._("Parent proxy pass")
proxyfiltermodules = i18n._("Proxy filter modules")
configapply = i18n._("Apply")
info = []
error = []
config = _Configuration()
for _i in ['port', 'parentproxyport']:
    config["str"+_i] = str(config[_i])
config['filterdict'] = {}
for _i in filtermodules:
    config['filterdict'][_i] = None
for _i in config['filters']:
    config['filterdict'][_i] = "True"

def exec_form (form):
    # reset info/error
    del info[:]
    del error[:]
    # proxy port
    if form.has_key('port'):
        try:
            _port = int(form['port'].value)
            if _port != config['port']:
                config['port'] = _port
                info.append(i18n._("Port successfully changed"))
        except ValueError:
            error.append(i18n._("Invalid proxy port"))
    # proxy user
    if form.has_key('proxyuser'):
        _proxyuser = form['proxyuser'].value.strip()
        if _proxyuser != config['proxyuser']:
            config['proxyuser'] = _proxyuser
            info.append(i18n._("Proxy user successfully changed"))
    # proxy pass
    if form.has_key('proxypass'):
        _proxypass = base64.encodestring(form['proxypass'].value.strip())
        if _proxypass != config['proxypass']:
            config['proxypass'] = _proxypass
            info.append(i18n._("Proxy password successfully changed"))
    # parent proxy host
    if form.has_key('parentproxy'):
        _parentproxy = form['parentproxy'].value.strip()
        if _parentproxy != config['parentproxy']:
            config['parentproxy'] = _parentproxy
            info.append(i18n._("Parent proxy successfully changed"))
    # parent proxy port
    if form.has_key('parentproxyport'):
        try:
            _parentproxyport = int(form['parentproxyport'].value)
            if _parentproxyport != config['parentproxyport']:
                config['parentproxyport'] = _parentproxyport
                info.append(i18n._("Parent proxy port successfully changed"))
        except ValueError:
            error.append(i18n._("Invalid parent proxy port"))
    # parent proxy user
    if form.has_key('parentproxyuser'):
        _parentproxyuser = form['parentproxyuser'].value.strip()
        if _parentproxyuser != config['parentproxyuser']:
            config['parentproxyuser'] = _parentproxyuser
            info.append(i18n._("Parent proxy user successfully changed"))
    # parent proxy pass
    if form.has_key('parentproxypass'):
        _parentproxypass = \
             base64.encodestring(form['parentproxypass'].value.strip())
        if _parentproxypass != config['parentproxypass']:
            config['parentproxypass'] = _parentproxypass
            info.append(i18n._("Parent proxy password successfully changed"))
    newfilters = []
    for key in form.keys():
        if key.startswith('filter'):
            newfilters.append(key[6:])
    for m in filtermodules:
        if m in newfilters and m not in config['filters']:
            config['filters'].append(m)
            config['filterdict'][m] = "True"
            info.append(i18n._("Enabled filter modules %s") % m)
        if m not in newfilters and m in config['filters']:
            config['filters'].remove(m)
            config['filterdict'][m] = None
            info.append(i18n._("Disabled filter modules %s") % m)
    if info:
        # write changed config
        config.write_proxyconf()

