from wc import i18n, AppName
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
    if form.has_key('port'):
        try:
            _config['port'] = int(form['port'].value)
            info.append(i18n._("Port successfully changed"))
        except ValueError:
            error.append(i18n._("Invalid proxy port"))
    if info:
        # write changed config
        _config.write_proxyconf()

