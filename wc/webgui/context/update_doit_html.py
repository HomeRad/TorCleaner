# -*- coding: iso-8859-1 -*-
from wc import AppName, Version, BaseUrl, config
from wc.update import update as _update
from cStringIO import StringIO as _StringIO

updatelog = ""

def _exec_form (form):
    global updatelog
    log = _StringIO()
    doreload = False
    try:
        doreload = _update(config, BaseUrl, log=log, dryrun=False)
        updatelog = log.getvalue()
        config.write_filterconf()
    except IOError, msg:
        updatelog = "Error: %s" % msg
    else:
        if doreload:
            from wc import daemon as _daemon
            _daemon.reload()

