# -*- coding: iso-8859-1 -*-
from wc import i18n, AppName
from wc import Configuration as _Configuration
from wc.webgui.context import getval
from wc.filter.rules.RewriteRule import replaceparts

t_title = i18n._("%s filter configuration") % AppName
t_back = i18n._("Back")
t_apply = i18n._("Apply")
t_removefolder = i18n._("Remove this folder")
t_enablefolder = i18n._("Enable this folder")
t_disablefolder = i18n._("Disable this folder")
t_disabledfoldericon = i18n._("Disabled folder icon")
t_foldericon = i18n._("Folder icon")
t_removerule = i18n._("Remove this rule")
t_enablerule = i18n._("Enable this rule")
t_disablerule = i18n._("Disable this rule")
t_disabledruleicon = i18n._("Disabled rule icon")
t_ruleicon = i18n._("Rule icon")
t_newfolder = i18n._("New folder")
t_newrule = i18n._("New rule")
t_folders = i18n._("Folders")
t_rules = i18n._("Rules")
t_rule = i18n._("Rule")
t_ruletitle = i18n._("Title")
t_ruledescription = i18n._("Description")
t_rulematchurl = i18n._("Match url")
t_ruledontmatchurl = i18n._("Don't match url")
t_ruleurlscheme = i18n._("URL scheme")
t_ruleurlhost = i18n._("URL host")
t_ruleurlport = i18n._("URL port")
t_ruleurlpath = i18n._("URL path")
t_ruleurlparameters = i18n._("URL parameters")
t_ruleurlquery = i18n._("URL query")
t_ruleurlfragment = i18n._("URL fragment")
t_ruleblockedurl = i18n._("Blocked URL")
t_rulefile = i18n._("Filename")
t_ruleheadername = i18n._("Header name")
t_ruleheadervalue = i18n._("Header value")
t_ruleimgwidth = i18n._("Image width")
t_ruleimgheight = i18n._("Image height")
t_ruleimgurl = i18n._("Blocked image url")
t_rulesearch = i18n._("Replace regex")
t_rulereplace = i18n._("Replacement")
t_ruletag = i18n._("Tag name")
t_ruleattrs = i18n._("Attributes")
t_attrname = i18n._("Name")
t_attrval = i18n._("Value")
t_removeattrs = i18n._("Remove selected attributes")
t_addattr = i18n._("Add attribute")
t_enclosedblock = i18n._("Enclosed block")
t_replacepart = i18n._("Replace part")
t_replacevalue = i18n._("Replace value")

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
    "Allowdomains",
    "Allowurls",
    "Blockdomains",
    "Blockurls",
    "Block",
    "Header",
    "Image",
    "Javascript",
    "Nocomments",
    "Pics",
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
    curparts = None


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
        if currule.get_name()=="rewrite":
            global curparts
            curparts = {}
            for i, part in enumerate(replaceparts):
                curparts[part['valname']] = (currule.part==i)
    except (ValueError, IndexError):
        error.append(i18n._("Invalid filter index"))
