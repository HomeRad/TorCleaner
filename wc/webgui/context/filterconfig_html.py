# -*- coding: iso-8859-1 -*-
import tempfile, os
from wc import i18n, AppName, ConfigDir, rulenames
from wc import Configuration as _Configuration
from wc.webgui.context import getval
from wc.filter.rules.RewriteRule import partvalnames, partnames
from wc.filter.rules.FolderRule import FolderRule
from wc.filter import GetRuleFromName

t_title = i18n._("%s filter configuration") % AppName
t_back = i18n._("Back")
t_apply = i18n._("Apply")
t_removefolder = i18n._("Remove folder")
t_renamefolder = i18n._("Rename folder")
t_enablefolder = i18n._("Enable folder")
t_disablefolder = i18n._("Disable folder")
t_disabledfoldericon = i18n._("Disabled folder icon")
t_foldericon = i18n._("Folder icon")
t_removerule = i18n._("Remove rule")
t_enablerule = i18n._("Enable rule")
t_disablerule = i18n._("Disable rule")
t_disabledruleicon = i18n._("Disabled rule icon")
t_ruleicon = i18n._("Rule icon")
t_newfolder = i18n._("New folder")
t_newrule = i18n._("New rule")
t_folders = i18n._("Folders")
t_rules = i18n._("Folder Rules")
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
t_rulefallback = i18n._("Fallback URL")

# config vars
info = []
error = []
config = _Configuration()
# current selected folder
curfolder = None
# current selected rule
currule = None
# only some rules allowed for new
newrulenames = list(rulenames[:])
newrulenames.remove('allowdomains')
newrulenames.remove('allowurls')
newrulenames.remove('blockdomains')
newrulenames.remove('blockurls')
newrulenames.sort()
# ruletype flag for tal condition
ruletype = {}


# form execution
def exec_form (form):
    # reset info/error and form vals
    _form_reset()
    # select a folder
    if form.has_key('selfolder'):
        _form_selfolder(getval(form, 'selfolder'))
    # select a rule
    if form.has_key('selrule') and curfolder:
        _form_selrule(getval(form, 'selrule'))
    # make a new folder
    if form.has_key('newfolder'):
        _form_newfolder(getval(form, 'newfoldername'))
    # rename current folder
    elif curfolder and form.has_key('renamefolder'):
        _form_renamefolder(getval(form, 'foldername'))
    # disable current folder
    elif curfolder and form.has_key('disablefolder%d'%curfolder.oid):
        _form_disablefolder(curfolder)
    # enable current folder
    elif curfolder and form.has_key('enablefolder%d'%curfolder.oid):
        _form_enablefolder(curfolder)
    # remove current folder
    elif curfolder and form.has_key('removefolder%d'%curfolder.oid):
        _form_removefolder(curfolder)
    # make a new rule in current folder
    elif curfolder and form.has_key('newrule'):
        _form_newrule(getval(form, 'newruletype'))
    # disable current rule
    elif currule and form.has_key('disablerule%d'%currule.oid):
        _form_disablerule(currule)
    # enable current rule
    elif currule and form.has_key('enablerule%d'%currule.oid):
        _form_enablerule(currule)
    # remove current rule
    elif currule and form.has_key('removerule%d'%currule.oid):
        _form_removerule(currule)
    # apply rule values
    elif currule and form.has_key('apply'):
        _form_apply(form)
    if info:
        config.write_filterconf()
    _form_set_selected()


def _form_reset ():
    del info[:]
    del error[:]
    global curfolder, currule, curparts
    curfolder = None
    currule = None
    curparts = None


def _form_set_selected ():
    for f in config['folderrules']:
        f.selected = False
        for r in f.rules:
            r.selected = False
    if curfolder:
        curfolder.selected = True
    if currule:
        currule.selected = True


def _form_selfolder (index):
    try:
        index = int(index)
        global curfolder
        curfolder = [ f for f in config['folderrules'] if f.oid==index ][0]
    except (ValueError, IndexError):
        error.append(i18n._("Invalid folder index"))


def _form_selrule (index):
    try:
        index = int(index)
        global currule
        currule = [ r for r in curfolder.rules if r.oid==index ][0]
        # fill ruletype flags
        for rt in rulenames:
            ruletype[rt] = (currule.get_name()==rt)
        # fill part flags
        if currule.get_name()=="rewrite":
            global curparts
            curparts = {}
            for i, part in enumerate(partvalnames):
                curparts[part] = (currule.part==i)
    except (ValueError, IndexError):
        error.append(i18n._("Invalid filter index"))


def _form_newfolder (foldername):
    if not foldername:
        error.append(i18n._("Empty folder name"))
        return
    fd, filename = tempfile.mkstemp(".zap", "local_", ConfigDir, text=True)
    # select the new folder
    global curfolder
    curfolder = FolderRule(title=foldername, desc="", disable=0, filename=filename)
    config['folderrules'].append(curfolder)
    info.append(i18n._("New folder %s created")%`os.path.basename(filename)`)


def _form_renamefolder (foldername):
    if not foldername:
        error.append(i18n._("Empty folder name"))
        return
    curfolder.title = foldername
    info.append(i18n._("Folder successfully renamed"))


def _form_disablefolder (folder):
    if folder.disable:
        error.append(i18n._("Folder already disabled"))
        return
    folder.disable = 1
    info.append(i18n._("Folder disabled"))


def _form_enablefolder (folder):
    if not folder.disable:
        error.append(i18n._("Folder already enabled"))
        return
    folder.disable = 0
    info.append(i18n._("Folder enabled"))


def _form_removefolder (folder):
    config['folderrules'].remove(folder)
    global curfolder, currule
    curfolder = None
    currule = None
    os.remove(folder.filename)
    info.append(i18n._("Folder removed"))


def _form_newrule (ruletype):
    if ruletype not in rulenames:
        error.append(i18n._("Invalid rule type"))
        return
    # add new rule
    rule = GetRuleFromName(ruletype)
    rule.parent = curfolder
    curfolder.append_rule(rule)
    # select new rule
    global currule
    currule = rule
    info.append(i18n._("New rule created"))


def _form_disablerule (rule):
    if rule.disable:
        error.append(i18n._("Rule already disabled"))
        return
    rule.disable = 1
    info.append(i18n._("Rule disabled"))


def _form_enablerule (rule):
    if not rule.disable:
        error.append(i18n._("Rule already enabled"))
        return
    rule.disable = 0
    info.append(i18n._("Rule enabled"))


def _form_removerule (rule):
    curfolder.rules.remove(rule)
    global currule
    currule = None
    info.append("Rule removed")


def _form_apply (form):
    """delegate rule apply to different apply_* functions"""
    # title and description apply for all rules:
    _form_rule_titledesc(form)
    # delegate
    attr = "_form_apply_%s" % currule.get_name()
    globals()[attr](form)


def _form_rule_titledesc (form):
    title = getval(form, 'rule_title')
    if not title:
        error.append("Empty rule title")
        return
    if title!=currule.title:
        currule.title = title
        info.append("Rule title changed")
    desc = getval(form, 'rule_description')
    if desc!=currule.desc:
        currule.desc = desc
        info.append("Rule description changed")


def _form_rule_matchurl (form):
    matchurl = getval(form, 'rule_matchurl').strip()
    if matchurl!=currule.matchurl:
        currule.matchurl = matchurl
        info.append("Rule match url changed")
    dontmatchurl = getval(form, 'rule_dontmatchurl').strip()
    if dontmatchurl!=currule.dontmatchurl:
        currule.dontmatchurl = dontmatchurl
        info.append("Rule dontmatch url changed")


def _form_rule_urlparts (form):
    scheme = getval(form, 'rule_urlscheme').strip()
    if scheme!=currule.scheme:
        currule.scheme = scheme
        info.append("Rule url scheme changed")
    host = getval(form, 'rule_urlhost').strip()
    if host!=currule.host:
        currule.host = host
        info.append("Rule url host changed")
    port = getval(form, 'rule_urlport').strip()
    if port!=currule.port:
        currule.port = port
        info.append("Rule url port changed")
    path = getval(form, 'rule_urlpath').strip()
    if path!=currule.path:
        currule.path = path
        info.append("Rule url path changed")
    parameters = getval(form, 'rule_urlparameters').strip()
    if parameters!=currule.parameters:
        currule.parameters = parameters
        info.append("Rule url parameters changed")
    query = getval(form, 'rule_urlquery').strip()
    if query!=currule.query:
        currule.query = query
        info.append("Rule url query changed")
    fragment = getval(form, 'rule_urlfragment').strip()
    if fragment!=currule.fragment:
        currule.fragment = fragment
        info.append("Rule url fragment changed")


def _form_apply_allow (form):
    _form_rule_urlparts(form)


def _form_apply_block (form):
    _form_rule_urlparts(form)
    url = getval(form, 'rule_blockedurl').strip()
    if url!=currule.url:
        currule.url = url
        info.append("Rule blocked url changed")


def _form_apply_header (form):
    _form_rule_matchurl(form)
    name = getval(form, 'rule_headername').strip()
    if name!=currule.name:
        currule.name = name
        info.append("Rule header name changed")
    value = getval(form, 'rule_headervalue').strip()
    if value!=currule.value:
        currule.value = value
        info.append("Rule header value changed")


def _form_apply_image (form):
    _form_rule_matchurl(form)
    width = getval(form, 'rule_imgwidth').strip()
    try:
        width = int(width)
    except ValueError:
        error.append("Invalid image width value")
        return
    if width!=currule.width:
        currule.width = width
        info.append("Rule image width changed")
    height = getval(form, 'rule_imgheight').strip()
    try:
        height = int(height)
    except ValueError:
        error.append("Invalid image height value")
        return
    if height!=currule.height:
        currule.height = height
        info.append("Rule image height changed")
    # XXX todo: image types


def _form_apply_javascript (form):
    _form_rule_matchurl(form)


def _form_apply_nocomments (form):
    _form_rule_matchurl(form)


def _form_apply_pics (form):
    _form_rule_matchurl(form)
    print "XXX apply pics"


def _form_apply_replace (form):
    _form_rule_matchurl(form)
    # note: do not strip() the search and replace form values
    search = getval(form, 'rule_search')
    if search!=currule.search:
        currule.search = search
        info.append("Rule replace search changed")
    replace = getval(form, 'rule_replace')
    if replace!=currule.replace:
        currule.replace = replace
        info.append("Rule replacement changed")


# XXX other submit buttons
def _form_apply_rewrite (form):
    _form_rule_matchurl(form)
    tag = getval(form, 'rule_tag').strip()
    if tag!=currule.tag:
        currule.tag = tag
        info.append("Rule rewrite tag changed")
    enclosed = getval(form, 'rule_enclosedblock').strip()
    if enclosed!=currule.enclosed:
        currule.enclosed = enclosed
        info.append("Rule rewrite enclosed block changed")
    part = getval(form, 'rule_rewritepart')
    if part!=currule.part:
        currule.part = part
        info.append("Rule rewrite part changed")
    replacement = getval(form, 'rule_rewritereplacement').strip()
    if replacement!=currule.replacement:
        currule.replacement = replacement
        info.append("Rule rewrite replacement changed")
