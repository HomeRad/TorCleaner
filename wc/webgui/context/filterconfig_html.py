# -*- coding: iso-8859-1 -*-
from wc import i18n, AppName
from wc import Configuration as _Configuration
from wc.webgui.context import getval

t_title = i18n._("%s filter configuration") % AppName
t_back = i18n._("Back")
t_remove = i18n._("Remove selected")
t_newfolder = i18n._("New folder")
t_newrule = i18n._("New rule")
t_folders = i18n._("Folders")
t_filters = i18n._("Filters")
t_rule = i18n._("Rule")

# config vars
info = []
error = []
config = _Configuration()
folders = [ r for r in config['rules'] if r.get_name()=='folder' ]
curfolder = None
filters = []
curfilter = None

# form execution
def exec_form (form):
    # reset info/error
    del info[:]
    del error[:]
    # reset form vals
    del filters[:]
    global curfolder, curfilter
    curfolder = None
    curfilter = None
    if form.has_key('selfolder'):
        _form_selfolder(getval(form['selfolder']))
    if form.has_key('selfilter') and curfolder:
        _form_selfilter(getval(form['selfilter']))
    # XXX submit buttons
    if info:
        # XXX write changed config
        pass


def _form_selfolder (index):
    try:
        index = int(index)
        global curfolder
        curfolder = [ f for f in folders if f.oid==index ][0]
        filters.extend(curfolder.rules)
    except (ValueError, IndexError):
        error.append(i18n._("Invalid folder index"))


def _form_selfilter (index):
    try:
        index = int(index)
        global curfilter
        curfilter = [ r for r in curfolder.rules if r.oid==index ][0]
    except (ValueError, IndexError):
        error.append(i18n._("Invalid filter index"))
