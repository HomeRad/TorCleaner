from wc import i18n, AppName
from wc import config as _config

title = i18n._("%s configuration") % AppName
port = i18n._("Port number")
configapply = i18n._("Apply")
info = []
error = []

def exec_form (form):
    if form.has_key('port'):
        try:
            print "port", form['port'].value
            #config['port'] = int(form['port'].value)
            info.append(i18n._("Port successfully changed"))
        except ValueError:
            error.append(i18n._("Invalid proxy port"))
    # XXX save changed config!

