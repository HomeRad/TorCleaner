# -*- coding: iso-8859-1 -*-
import tempfile, os
from wc import i18n, AppName, ConfigDir, rulenames, Version
from wc import Configuration as _Configuration
from wc.webgui.context import getval as _getval
from wc.webgui.context import getlist as _getlist
from wc.webgui.context import filter_safe as _filter_safe
from wc.filter.rules.RewriteRule import partvalnames, partnames
from wc.filter.rules.RewriteRule import part_num as _part_num
from wc.filter.rules.FolderRule import FolderRule as _FolderRule
from wc.filter import GetRuleFromName as _GetRuleFromName
from wc.filter.PICS import services as pics_data

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
# pics data
pics_services = pics_data.keys()
pics_services.sort()
pics_categories = {}
for service in pics_services:
    pics_categories[service] = pics_data[service]['categories'].keys()
    pics_categories[service].sort()


def _exec_form (form):
    """form execution"""
    # reset info/error and form vals
    _form_reset()
    # select a folder
    if form.has_key('selfolder'):
        _form_selfolder(_getval(form, 'selfolder'))
    # select a rule
    if form.has_key('selrule') and curfolder:
        _form_selrule(_getval(form, 'selrule'))
    # make a new folder
    if form.has_key('newfolder'):
        _form_newfolder(_getval(form, 'newfoldername'))
    # rename current folder
    elif curfolder and form.has_key('renamefolder'):
        _form_renamefolder(_getval(form, 'foldername'))
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
        _form_newrule(_getval(form, 'newruletype'))
    # disable current rule
    elif currule and form.has_key('disablerule%d'%currule.oid):
        _form_disablerule(currule)
    # enable current rule
    elif currule and form.has_key('enablerule%d'%currule.oid):
        _form_enablerule(currule)
    # remove current rule
    elif currule and form.has_key('removerule%d'%currule.oid):
        _form_removerule(currule)

    # rule specific submit buttons
    elif currule and form.has_key('addattr'):
        _form_rewrite_addattr(form)
    elif currule and form.has_key('removeattrs') and form.has_key('delattr'):
        _form_rewrite_removeattrs(form)

    # generic apply rule values
    elif currule and form.has_key('apply'):
        _form_apply(form)
    # look for rule up/down moves
    elif curfolder:
        for rule in curfolder.rules:
            # note: image submits can append ".x" and ".y" to key
            if form.has_key('rule_up_%d' % rule.oid) or \
               form.has_key('rule_up_%d.x' % rule.oid):
                _form_rule_up(rule.oid)
            elif form.has_key('rule_down_%d' % rule.oid) or \
                 form.has_key('rule_down_%d.x' % rule.oid):
                _form_rule_down(rule.oid)
    # look for folder up/down moves
    else:
        for folder in config['folderrules']:
            if form.has_key('folder_up_%d' % folder.oid) or \
               form.has_key('folder_up_%d.x' % folder.oid):
                _form_folder_up(folder.oid)
            elif form.has_key('folder_down_%d' % folder.oid) or \
                 form.has_key('folder_down_%d.x' % folder.oid):
                _form_folder_down(folder.oid)

    if info:
        config.write_filterconf()
    _form_set_tags()


def _form_reset ():
    del info[:]
    del error[:]
    global curfolder, currule, curparts
    curfolder = None
    currule = None
    curparts = None


def _form_set_tags ():
    for folder in config['folderrules']:
        folder.selected = False
        for i, rule in enumerate(folder.rules):
            rule.selected = False
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
        # XXX this side effect on rule parts is bad :(
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
    curfolder = _FolderRule(title=foldername, desc="", disable=0, filename=filename)
    config['folderrules'].append(curfolder)
    info.append(i18n._("New folder %s created.")%`os.path.basename(filename)`)


def _form_renamefolder (foldername):
    if not foldername:
        error.append(i18n._("Empty folder name."))
        return
    curfolder.title = foldername
    info.append(i18n._("Folder successfully renamed."))


def _form_disablefolder (folder):
    if folder.disable:
        error.append(i18n._("Folder already disabled."))
        return
    folder.disable = 1
    info.append(i18n._("Folder disabled."))


def _form_enablefolder (folder):
    if not folder.disable:
        error.append(i18n._("Folder already enabled."))
        return
    folder.disable = 0
    info.append(i18n._("Folder enabled."))


def _form_removefolder (folder):
    config['folderrules'].remove(folder)
    global curfolder, currule
    curfolder = None
    currule = None
    os.remove(folder.filename)
    info.append(i18n._("Folder removed."))


def _form_newrule (ruletype):
    if ruletype not in rulenames:
        error.append(i18n._("Invalid rule type."))
        return
    # add new rule
    rule = _GetRuleFromName(ruletype)
    rule.parent = curfolder
    curfolder.append_rule(rule)
    # select new rule
    _form_selrule(rule.oid)
    info.append(i18n._("New rule created."))


def _form_disablerule (rule):
    if rule.disable:
        error.append(i18n._("Rule already disabled."))
        return
    rule.disable = 1
    info.append(i18n._("Rule disabled."))


def _form_enablerule (rule):
    if not rule.disable:
        error.append(i18n._("Rule already enabled."))
        return
    rule.disable = 0
    info.append(i18n._("Rule enabled."))


def _form_removerule (rule):
    curfolder.rules.remove(rule)
    global currule
    currule = None
    info.append(i18n._("Rule removed."))


def _form_rewrite_addattr (form):
    name = _getval(form, "attrname").strip()
    if not name:
        error.append(i18n._("Empty attribute name."))
        return
    value = _getval(form, "attrval")
    currule.attrs[name] = value
    info.append(i18n._("Rewrite attribute added."))


def _form_rewrite_removeattrs (form):
    toremove = _getlist(form, 'delattr')
    if toremove:
        for attr in toremove:
            del currule.attrs[attr]
        info.append(i18n._("Rewrite attributes removed."))


def _form_folder_up (oid):
    """move folder with given oid one up"""
    folders = config['folderrules']
    for i, folder in enumerate(folders):
        if folder.oid==oid and i>0:
            # swap oids
            folders[i-1].oid,folders[i].oid = folders[i].oid,folders[i-1].oid
            # sort folders
            config.sort()
            # deselet rule and folder
            global currule, curfolder
            currule = None
            curfolder = None
            info.append(i18n._("Folder moved up."))
            return
    error.append(i18n._("Invalid folder move up id."))


def _form_folder_down (oid):
    """move folder with given oid one down"""
    folders = config['folderrules']
    for i, folder in enumerate(folders):
        if folder.oid==oid and i<(len(folders)-1):
            # swap oids
            folders[i].oid,folders[i+1].oid = folders[i+1].oid,folders[i].oid
            # sort folders
            config.sort()
            # deselet rule and folder
            global currule, curfolder
            currule = None
            curfolder = None
            info.append(i18n._("Folder moved down."))
            return
    error.append(i18n._("Invalid folder move down id."))


def _form_rule_up (oid):
    """move rule with given oid one up"""
    rules = curfolder.rules
    for i, rule in enumerate(rules):
        if rule.oid==oid and i>0:
            # swap oids
            rules[i-1].oid,rules[i].oid = rules[i].oid,rules[i-1].oid
            # sort folder
            curfolder.sort()
            # deselect rule
            global currule
            currule = None
            info.append(i18n._("Rule moved up."))
            return
    error.append(i18n._("Invalid rule move up id."))


def _form_rule_down (oid):
    """move rule with given oid one down"""
    rules = curfolder.rules
    for i, rule in enumerate(rules):
        if rule.oid==oid and i<(len(rules)-1):
            # swap oids
            rules[i].oid,rules[i+1].oid = rules[i+1].oid,rules[i].oid
            # sort folder
            curfolder.sort()
            # deselect rule
            global currule
            currule = None
            info.append(i18n._("Rule moved down."))
            return
    error.append(i18n._("Invalid rule move down id."))


def _form_apply (form):
    """delegate rule apply to different apply_* functions"""
    # title and description apply for all rules:
    _form_rule_titledesc(form)
    # delegate
    attr = "_form_apply_%s" % currule.get_name()
    globals()[attr](form)


def _form_rule_titledesc (form):
    title = _getval(form, 'rule_title')
    if not title:
        error.append(i18n._("Empty rule title"))
        return
    if title!=currule.title:
        currule.title = title
        info.append(i18n._("Rule title changed."))
    desc = _getval(form, 'rule_description')
    if desc!=currule.desc:
        currule.desc = desc
        info.append(i18n._("Rule description changed."))


def _form_rule_matchurl (form):
    matchurl = _getval(form, 'rule_matchurl').strip()
    if matchurl!=currule.matchurl:
        currule.matchurl = matchurl
        info.append(i18n._("Rule match url changed."))
    dontmatchurl = _getval(form, 'rule_dontmatchurl').strip()
    if dontmatchurl!=currule.dontmatchurl:
        currule.dontmatchurl = dontmatchurl
        info.append(i18n._("Rule dontmatch url changed."))


def _form_rule_urlparts (form):
    scheme = _getval(form, 'rule_urlscheme').strip()
    if scheme!=currule.scheme:
        currule.scheme = scheme
        info.append(i18n._("Rule url scheme changed."))
    host = _getval(form, 'rule_urlhost').strip()
    if host!=currule.host:
        currule.host = host
        info.append(i18n._("Rule url host changed."))
    port = _getval(form, 'rule_urlport').strip()
    if port!=currule.port:
        currule.port = port
        info.append(i18n._("Rule url port changed."))
    path = _getval(form, 'rule_urlpath').strip()
    if path!=currule.path:
        currule.path = path
        info.append(i18n._("Rule url path changed."))
    parameters = _getval(form, 'rule_urlparameters').strip()
    if parameters!=currule.parameters:
        currule.parameters = parameters
        info.append(i18n._("Rule url parameters changed."))
    query = _getval(form, 'rule_urlquery').strip()
    if query!=currule.query:
        currule.query = query
        info.append(i18n._("Rule url query changed."))
    fragment = _getval(form, 'rule_urlfragment').strip()
    if fragment!=currule.fragment:
        currule.fragment = fragment
        info.append(i18n._("Rule url fragment changed."))


def _form_apply_allow (form):
    _form_rule_urlparts(form)


def _form_apply_block (form):
    _form_rule_urlparts(form)
    url = _getval(form, 'rule_blockedurl').strip()
    if url!=currule.url:
        currule.url = url
        info.append(i18n._("Rule blocked url changed."))


def _form_apply_header (form):
    _form_rule_matchurl(form)
    name = _getval(form, 'rule_headername').strip()
    if not name:
        error.append(i18n._("Empty header rule name."))
    elif name!=currule.name:
        currule.name = name
        info.append(i18n._("Rule header name changed."))
    value = _getval(form, 'rule_headervalue').strip()
    if value!=currule.value:
        currule.value = value
        info.append(i18n._("Rule header value changed."))


def _form_apply_image (form):
    _form_rule_matchurl(form)
    width = _getval(form, 'rule_imgwidth').strip()
    try:
        width = int(width)
    except ValueError:
        error.append(i18n._("Invalid image width value."))
        return
    if width!=currule.width:
        currule.width = width
        info.append(i18n._("Rule image width changed."))
    height = _getval(form, 'rule_imgheight').strip()
    try:
        height = int(height)
    except ValueError:
        error.append(i18n._("Invalid image height value."))
        return
    if height!=currule.height:
        currule.height = height
        info.append(i18n._("Rule image height changed."))
    # XXX todo: image types


def _form_apply_javascript (form):
    _form_rule_matchurl(form)


def _form_apply_nocomments (form):
    _form_rule_matchurl(form)


def _form_apply_pics (form):
    _form_rule_matchurl(form)
    # PICS services
    for service in pics_services:
        if form.has_key("service_%s"%service):
            if not currule.ratings.has_key(service):
                currule.ratings[service] = {}
                for category in pics_categories[service]:
                    currule.ratings[service][category] = 0
                info.append(i18n._("PICS service %s enabled.") % \
                            pics_data[service]['name'])
        else:
            if currule.ratings.has_key(service):
                del currule.ratings[service]
                info.append(i18n._("PICS service %s disabled.") % \
                            pics_data[service]['name'])
        # service categories
        if currule.ratings.has_key(service):
            for category in pics_categories[service]:
                if form.has_key("category_%s_%s" % (service, category)):
                    if not currule.ratings[service][category]:
                        currule.ratings[service][category] = 1
                        info.append(i18n._("PICS service %s, category %s enabled.") %\
                               (pics_data[service]['name'], category))
                else:
                    if currule.ratings[service][category]:
                        currule.ratings[service][category] = 0
                        info.append(i18n._("PICS service %s, category %s disabled.") %\
                               (pics_data[service]['name'], category))


def _form_apply_replace (form):
    _form_rule_matchurl(form)
    # note: do not strip() the search and replace form values
    search = _getval(form, 'rule_search')
    if not search:
        error.append(i18n._("Empty replace search value."))
        return
    if search!=currule.search:
        currule.search = search
        info.append(i18n._("Rule replace search changed."))
    replace = _getval(form, 'rule_replace')
    if replace!=currule.replace:
        currule.replace = replace
        info.append(i18n._("Rule replacement changed."))


def _form_apply_rewrite (form):
    _form_rule_matchurl(form)
    tag = _getval(form, 'rule_tag').strip()
    if not tag:
        error.append(i18n._("Empty rewrite tag name."))
        return
    if tag!=currule.tag:
        currule.tag = tag
        info.append(i18n._("Rule rewrite tag changed."))
    enclosed = _getval(form, 'rule_enclosedblock').strip()
    if enclosed!=currule.enclosed:
        currule.enclosed = enclosed
        info.append(i18n._("Rule rewrite enclosed block changed."))
    part = _getval(form, 'rule_rewritepart')
    partnum = _part_num(part)
    if partnum is None:
        error.append(i18n._("Invalid part value %s.") % _filter_safe(part))
        return
    if partnum!=currule.part:
        currule.part = partnum
        info.append(i18n._("Rule rewrite part changed."))
        # select again because of side effect (XXX see above)
        _form_selrule(currule.oid)
    replacement = _getval(form, 'rule_rewritereplacement').strip()
    if replacement!=currule.replacement:
        currule.replacement = replacement
        info.append(i18n._("Rule rewrite replacement changed."))
