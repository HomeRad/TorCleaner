from wc import i18n, AppName
from wc import config as _config

title = i18n._("%s configuration") % AppName
port = i18n._("Port number")
configapply = i18n._("Apply")
info = []
error = []

def exec_form (form):
    # reset info/error
    del info[:]
    del error[:]
    if form.has_key('port'):
        try:
            _config['port'] = int(form['port'].value)
            info.append(i18n._("Port successfully changed"))
        except ValueError:
            error.append(i18n._("Invalid proxy port"))
    # save changed config
    if info:
        _config.write_proxyconf()

