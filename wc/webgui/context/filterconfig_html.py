# -*- coding: iso-8859-1 -*-
from wc import i18n, AppName
from wc import Configuration as _Configuration
from wc.webgui.context import getval

t_title = i18n._("%s filter configuration") % AppName
t_back = i18n._("Back")
t_apply = i18n._("Apply")
t_remove = i18n._("Remove selected")
tt_enablefolder = i18n._("Enable/disable folder")
tt_enablerule = i18n._("Enable/disable rule")
t_newfolder = i18n._("New folder")
t_newrule = i18n._("New rule")
t_folders = i18n._("Folders")
t_rules = i18n._("Rules")
t_rule = i18n._("Rule")

# config vars
info = []
error = []
config = _Configuration()
folders = [ r for r in config['rules'] if r.get_name()=='folder' ]
# current selected folder
curfolder = None
# current selected rule
currule = None
ruletypes = [
    "Allow",
    "Block",
    "Header",
    "Image",
    "Nocomments",
    "Rewrite",
    "Replacer",
]
# ruletype flag for tal condition
ruletype = {}


# form execution
def exec_form (form):
    # reset info/error
    # reset form vals
    _form_reset()
    if form.has_key('selfolder'):
        _form_selfolder(getval(form['selfolder']))
    if form.has_key('selrule') and curfolder:
        _form_selrule(getval(form['selrule']))
    # make a new folder
    # XXX
    # disable selected folders
    # XXX
    # make a new rule
    if form.has_key('newrule') and form.has_key('newruletype') and \
        currule:
        _form_newrule(getval(form['newruletype']))
    # remove selected rule
    # XXX
    # disable selected rule
    # XXX
    # XXX submit buttons
    if info:
        # XXX write changed config
        pass


def _form_reset ():
    del info[:]
    del error[:]
    global curfolder, currule
    curfolder = None
    currule = None


def _form_selfolder (index):
    try:
        index = int(index)
        global curfolder
        curfolder = [ f for f in folders if f.oid==index ][0]
    except (ValueError, IndexError):
        error.append(i18n._("Invalid folder index"))


def _form_selrule (index):
    try:
        index = int(index)
        global currule
        currule = [ r for r in curfolder.rules if r.oid==index ][0]
        for rt in ruletypes:
            ruletype[rt] = (currule.get_name()==rt.lower())
    except (ValueError, IndexError):
        error.append(i18n._("Invalid filter index"))
