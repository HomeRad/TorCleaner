# -*- coding: iso-8859-1 -*-
"""parameters for filterconfig.html page"""
# Copyright (C) 2003-2004  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import tempfile, os, re
import wc.i18n
from wc import AppName, ConfigDir, rulenames, Version, config
from wc.webgui.context import getval as _getval
from wc.webgui.context import getlist as _getlist
from wc.webgui.context import filter_safe as _filter_safe
from wc.filter.rules.Rule import compileRegex as _compileRegex
from wc.filter.rules.RewriteRule import partvalnames, partnames
from wc.filter.rules.RewriteRule import part_num as _part_num
from wc.filter.rules.FolderRule import FolderRule as _FolderRule
from wc.filter.rules.FolderRule import recalc_up_down as _recalc_up_down
from wc.filter.rules import register_rule as _register_rule
from wc.filter.rules import generate_sids as _generate_sids
from wc.filter import GetRuleFromName as _GetRuleFromName
from wc.filter.Rating import service, rangenames
from wc.filter.Rating import rating_is_valid_value as _rating_is_valid_value

# config vars
info = {}
error = {}
_rules_per_page = 50
# current selected folder
curfolder = None
# current selected rule
currule = None
# current index of first rule in folder to display
curindex = 0
# current parts
curparts = None
# current filterstage value
curfilterstage = None
# only some rules allowed for new
newrulenames = list(rulenames[:])
newrulenames.remove('allowdomains')
newrulenames.remove('allowurls')
newrulenames.remove('blockdomains')
newrulenames.remove('blockurls')
newrulenames.sort()
# ruletype flag for tal condition
ruletype = {}


def _exec_form (form, lang):
    """form execution"""
    # reset info/error and form vals
    _form_reset()
    # select a folder
    if form.has_key('selfolder'):
        _form_selfolder(_getval(form, 'selfolder'))
    if form.has_key('selindex') and curfolder:
        _form_selindex(_getval(form, 'selindex'))
    if curfolder:
        l = len(curfolder.rules)
        if l > _rules_per_page:
            _calc_selindex(curfolder, curindex)
        else:
            curfolder.selindex = []
        curfolder.indexstr = u"(%d-%d/%d)"%(curindex+1,
                                         min(curindex+_rules_per_page, l), l)
    # select a rule
    if form.has_key('selrule') and curfolder:
        _form_selrule(_getval(form, 'selrule'))
    # make a new folder
    if form.has_key('newfolder'):
        _form_newfolder(_getval(form, 'newfoldername'), lang)
    # rename current folder
    elif curfolder and form.has_key('renamefolder'):
        _form_renamefolder(_getval(form, 'foldername'), lang)
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
        _form_newrule(_getval(form, 'newruletype'), lang)
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
    elif currule and form.has_key('addmatchurl'):
        _form_rule_addmatchurl(form)
    elif currule and form.has_key('delmatchurls'):
        _form_rule_delmatchurls(form)
    elif currule and form.has_key('addnomatchurl'):
        _form_rule_addnomatchurl(form)
    elif currule and form.has_key('delnomatchurls'):
        _form_rule_delnomatchurls(form)
    elif currule and form.has_key('addattr'):
        _form_rewrite_addattr(form)
    elif currule and form.has_key('removeattrs') and form.has_key('delattr'):
        _form_rewrite_removeattrs(form)

    # generic apply rule values
    elif currule and form.has_key('apply'):
        _form_apply(form, lang)
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
    for folder in config['folderrules']:
        if form.has_key('folder_up_%d' % folder.oid) or \
           form.has_key('folder_up_%d.x' % folder.oid):
            _form_folder_up(folder.oid)
        elif form.has_key('folder_down_%d' % folder.oid) or \
             form.has_key('folder_down_%d.x' % folder.oid):
            _form_folder_down(folder.oid)

    _form_set_tags()


def _form_reset ():
    info.clear()
    error.clear()
    global curfolder, currule, curparts, curindex, curfilterstage
    curfolder = None
    currule = None
    curparts = None
    curfilterstage = None
    curindex = 0


def _form_set_tags ():
    for folder in config['folderrules']:
        folder.selected = False
        for i, rule in enumerate(folder.rules):
            rule.selected = False
    if curfolder:
        curfolder.selected = True
        curfolder.rules_display = curfolder.rules[curindex:curindex+_rules_per_page]
    if currule:
        currule.selected = True


def _form_selfolder (index):
    try:
        index = int(index)
        global curfolder
        curfolder = [ f for f in config['folderrules'] if f.oid==index ][0]
    except (ValueError, IndexError):
        error['folderindex'] = True


def _form_selrule (index):
    try:
        index = int(index)
        global currule
        currule = [ r for r in curfolder.rules if r.oid==index ][0]
        # fill ruletype flags
        for rt in rulenames:
            ruletype[rt] = (currule.get_name()==rt)
        # XXX this side effect is bad :(
        # fill part flags
        if currule.get_name()==u"rewrite":
            global curparts
            curparts = {}
            for i, part in enumerate(partvalnames):
                curparts[part] = (currule.part==i)
        elif currule.get_name()==u"header":
            global curfilterstage
            curfilterstage = {
                u'both': currule.filterstage==u'both',
                u'request': currule.filterstage==u'request',
                u'response': currule.filterstage==u'response',
            }
    except (ValueError, IndexError):
        error['ruleindex'] = True


def _form_selindex (index):
    """display rules in curfolder from given index"""
    global curindex
    try:
        curindex = int(index)
    except ValueError:
        error['selindex'] = True


def _calc_selindex (folder, index):
    res = [index-1000, index-250, index-50, index, index+50, index+250, index+1000]
    folder.selindex = [ x for x in res if 0 <= x < len(folder.rules) and x!=index ]


def _reinit_filters ():
    config.init_filter_modules()


def _form_newfolder (foldername, lang):
    if not foldername:
        error['newfolder'] = True
        return
    fd, filename = tempfile.mkstemp(u".zap", u"local_", ConfigDir, text=True)
    # create and select the new folder
    global curfolder
    curfolder = _FolderRule(titles={lang:foldername}, filename=filename)
    _register_rule(curfolder)
    prefix = config['development'] and u"wc" or u"lc"
    _generate_sids(prefix)
    if not config['folderrules']:
        curfolder.oid = 0
    else:
        curfolder.oid = config['folderrules'][-1].oid+1
    curfolder.write()
    config['folderrules'].append(curfolder)
    _recalc_up_down(config['folderrules'])
    info['newfolder'] = True


def _form_renamefolder (foldername, lang):
    if not foldername:
        error['renamefolder'] = True
        return
    curfolder.titles[lang] = foldername
    curfolder.write()
    info['renamefolder'] = True


def _form_disablefolder (folder):
    if folder.disable:
        error['disablefolder'] = True
        return
    folder.disable = 1
    folder.write()
    _reinit_filters()
    info['disablefolder'] = True


def _form_enablefolder (folder):
    if not folder.disable:
        error['enablefolder'] = True
        return
    folder.disable = 0
    folder.write()
    _reinit_filters()
    info['enablefolder'] = True


def _form_removefolder (folder):
    # XXX error handling
    config['folderrules'].remove(folder)
    global curfolder, currule
    curfolder = None
    currule = None
    os.remove(folder.filename)
    _reinit_filters()
    info['removefolder'] = True


def _form_newrule (rtype, lang):
    if rtype not in rulenames:
        error['newrule'] = True
        return
    # add new rule
    rule = _GetRuleFromName(rtype)
    rule.parent = curfolder
    rule.titles[lang] = wc.i18n._("No title")
    # compile data and register
    rule.compile_data()
    prefix = config['development'] and u"wc" or u"lc"
    _generate_sids(prefix)
    curfolder.append_rule(rule)
    _recalc_up_down(curfolder.rules)
    curfolder.write()
    _reinit_filters()
    # select new rule
    _form_selrule(rule.oid)
    info['newrule'] = True


def _form_disablerule (rule):
    if rule.disable:
        error['disablerule'] = True
        return
    rule.disable = 1
    curfolder.write()
    _reinit_filters()
    info['disablerule'] = True


def _form_enablerule (rule):
    if not rule.disable:
        error['enablerule'] = True
        return
    rule.disable = 0
    curfolder.write()
    _reinit_filters()
    info['enablerule'] = True


def _form_removerule (rule):
    # XXX error handling
    rules = curfolder.rules
    rules.remove(rule)
    for i in range(rule.oid, len(rules)):
        rules[i].oid = i
    curfolder.write()
    _reinit_filters()
    # deselect current rule
    global currule
    currule = None
    info['removerule'] = True


def _form_rewrite_addattr (form):
    name = _getval(form, "attrname").strip()
    if not name:
        error['rewrite_addattr'] = True
        return
    value = _getval(form, "attrval")
    currule.attrs[name] = value
    currule.attrs_ro[name] = re.compile(name)
    curfolder.write()
    info['rewrite_addattr'] = True


def _form_rewrite_removeattrs (form):
    toremove = _getlist(form, 'delattr')
    if toremove:
        for attr in toremove:
            if not currule.attrs.has_key(attr):
                error['rewrite_delattr'] = True
                return
        for attr in toremove:
            del currule.attrs[attr]
            del currule.attrs_ro[attr]
        curfolder.write()
        info['rewrite_delattr'] = True


def _swap_rules (rules, idx):
    # swap rules
    rules[idx].oid, rules[idx+1].oid = rules[idx+1].oid, rules[idx].oid
    rules[idx], rules[idx+1] = rules[idx+1], rules[idx]


def _form_folder_down (oid):
    """move folder with given oid one down"""
    folders = config['folderrules']
    if not (0 <= oid < len(folders)):
        error['folderdown'] = True
        return
    # swap folders
    _swap_rules(folders, oid)
    folders[oid].write()
    folders[oid+1].write()
    _recalc_up_down(folders)
    # deselet rule and folder
    global currule, curfolder
    currule = None
    curfolder = None
    info['folderdown'] = True


def _form_folder_up (oid):
    """move folder with given oid one up"""
    folders = config['folderrules']
    if not (0 < oid <= len(folders)):
        error['folderup'] = True
        return
    # swap folders
    _swap_rules(folders, oid-1)
    folders[oid-1].write()
    folders[oid].write()
    _recalc_up_down(folders)
    # deselet rule and folder
    global currule, curfolder
    currule = None
    curfolder = None
    info['folderup'] = True


def _form_rule_down (oid):
    """move rule with given oid one down"""
    rules = curfolder.rules
    if not (0 <= oid < len(rules)):
        error['ruledown'] = True
        return
    # swap rules
    _swap_rules(rules, oid)
    curfolder.write()
    _recalc_up_down(rules)
    # deselect rule
    global currule
    currule = None
    info['ruledown'] = True


def _form_rule_up (oid):
    """move rule with given oid one up"""
    rules = curfolder.rules
    if not (0 < oid <= len(rules)):
        error['ruleup'] = True
        return
    # swap rules
    _swap_rules(rules, oid-1)
    curfolder.write()
    _recalc_up_down(rules)
    # deselect rule
    global currule
    currule = None
    info['ruleup'] = True


def _form_apply (form, lang):
    """delegate rule apply to different apply_* functions"""
    # title and description apply for all rules:
    _form_rule_titledesc(form, lang)
    # delegate
    attr = "_form_apply_%s" % currule.get_name()
    globals()[attr](form)
    if info:
        curfolder.write()


def _form_rule_titledesc (form, lang):
    title = _getval(form, 'rule_title')
    if not title:
        error['ruletitle'] = True
        return
    if title!=currule.titles[lang]:
        currule.titles[lang] = title
        info['ruletitle'] = True
    desc = _getval(form, 'rule_description')
    if desc!=currule.descriptions[lang]:
        currule.descriptions[lang] = desc
        info['ruledesc'] = True


def _form_rule_addmatchurl (form):
    if not form.has_key('newmatchurl'):
        return
    matchurl = _getval(form, 'newmatchurl').strip()
    if matchurl not in currule.matchurls:
        currule.matchurls.append(matchurl)
        currule.compile_matchurls()
        curfolder.write()
        info['rulematchurl'] = True


def _form_rule_delmatchurls (form):
    toremove = [u for u in _getlist(form, 'rule_matchurls') if u in currule.matchurls]
    if toremove:
        for matchurl in toremove:
            currule.matchurls.remove(matchurl)
        currule.compile_matchurls()
        curfolder.write()
        info['rulematchurl'] = True


def _form_rule_addnomatchurl (form):
    if not form.has_key('newnomatchurl'):
        return
    nomatchurl = _getval(form, 'newnomatchurl').strip()
    if nomatchurl not in currule.nomatchurls:
        currule.nomatchurls.append(nomatchurl)
        currule.compile_nomatchurls()
        curfolder.write()
        info['rulenomatchurl'] = True


def _form_rule_delnomatchurls (form):
    toremove = [u for u in _getlist(form, 'rule_nomatchurls') if u in currule.nomatchurls]
    if toremove:
        for nomatchurl in toremove:
            currule.nomatchurls.remove(nomatchurl)
        currule.compile_nomatchurls()
        curfolder.write()
        info['rulenomatchurl'] = True


def _form_apply_allow (form):
    url = _getval(form, 'rule_url').strip()
    if url!=currule.url:
        currule.url = url
        info['ruleurl'] = True


def _form_apply_block (form):
    _form_apply_allow(form)
    replacement = _getval(form, 'rule_replacement').strip()
    if replacement!=currule.replacement:
        currule.replacement = replacement
        info['rulereplacement'] = True


def _form_apply_header (form):
    name = _getval(form, 'rule_headername').strip()
    if not name:
        error['ruleheadername'] = True
    elif name!=currule.name:
        currule.name = name
        info['ruleheadername'] = True
    value = _getval(form, 'rule_headervalue').strip()
    if value!=currule.value:
        currule.value = value
        info['ruleheadervalue'] = True
    filterstage = _getval(form, 'rule_headerfilter')
    if filterstage!=currule.filterstage:
        currule.filterstage = filterstage
        info['ruleheaderfilter'] = True
        # select again because of side effect (XXX see above)
        _form_selrule(currule.oid)


def _form_apply_image (form):
    width = _getval(form, 'rule_imgwidth').strip()
    try:
        width = int(width)
    except ValueError:
        error['ruleimgwidth'] = True
        return
    if width!=currule.width:
        currule.width = width
        info['ruleimgwidth'] = True
    height = _getval(form, 'rule_imgheight').strip()
    try:
        height = int(height)
    except ValueError:
        error['ruleimgheight'] = True
        return
    if height!=currule.height:
        currule.height = height
        info['ruleimgheight'] = True
    # XXX todo: image types


def _form_apply_imagereduce (form):
    quality = _getval(form, 'rule_imgquality').strip()
    try:
        quality = int(quality)
    except ValueError:
        error['ruleimgquality'] = True
        return
    if quality!=currule.quality:
        currule.quality = quality
        info['ruleimgquality'] = True
    minsize = _getval(form, 'rule_imgminsize').strip()
    try:
        minsize = int(minsize)
    except ValueError:
        error['ruleimgminsize'] = True
        return
    if minsize!=currule.minimal_size_bytes:
        currule.minimal_size_bytes = minsize
        info['ruleimgminsize'] = True


def _form_apply_javascript (form):
    pass

def _form_apply_antivirus (form):
    pass

def _form_apply_nocomments (form):
    pass


def _form_apply_rating (form):
    # rating categories
    for category, catdata in service['categories'].items():
        key = "category_%s"%category
        if form.has_key(key):
            value = _getval(form, key)
            if not _rating_is_valid_value(catdata, value):
                error['categoryvalue'] = True
                return
            if category not in currule.ratings:
                currule.ratings[category] = value
                info['rulecategory'] = True
            elif currule.ratings[category]!=value:
                currule.ratings[category] = value
                info['rulecategory'] = True
        elif category in currule.ratings:
            info['rulecategory'] = True
            del currule.ratings[category]
    if info:
        currule.compile_values()


def _form_apply_replace (form):
    # note: do not strip() the search and replace form values
    search = _getval(form, 'rule_search')
    if not search:
        error['rulesearch'] = True
        return
    if search!=currule.search:
        currule.search = search
        _compileRegex(currule, "search")
        info['rulesearch'] = True
    replacement = _getval(form, 'rule_replace')
    if replacement!=currule.replacement:
        currule.replacement = replacement
        info['rulereplace'] = True


def _form_apply_rewrite (form):
    tag = _getval(form, 'rule_tag').strip()
    if not tag:
        error['ruletag'] = True
        return
    if tag!=currule.tag:
        currule.tag = tag
        info['ruletag'] = True
    enclosed = _getval(form, 'rule_enclosedblock').strip()
    if enclosed!=currule.enclosed:
        currule.enclosed = enclosed
        _compileRegex(currule, "enclosed")
        info['ruleenclosedblock'] = True
    part = _getval(form, 'rule_rewritepart')
    partnum = _part_num(part)
    if partnum is None:
        error['rulerewritepart'] = True
        return
    if partnum!=currule.part:
        currule.part = partnum
        info['rulerewritepart'] = True
        # select again because of side effect (XXX see above)
        _form_selrule(currule.oid)
    replacement = _getval(form, 'rule_rewritereplacement').strip()
    if replacement!=currule.replacement:
        currule.replacement = replacement
        info['rulerewritereplacement'] =  True
