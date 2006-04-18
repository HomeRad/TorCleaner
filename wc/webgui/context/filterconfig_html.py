# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2006 Bastian Kleineidam
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
"""
Parameters for filterconfig.html page.
"""

import tempfile
import os
import re
from wc import AppName, Version
from wc.configuration import config
from wc.configuration.confparse import rulenames
from wc.webgui.context import getval as _getval
from wc.webgui.context import getlist as _getlist
from wc.webgui.context import get_prefix_vals as _get_prefix_vals
from wc.filter.rules.Rule import compileRegex as _compileRegex
from wc.filter.rules.HtmlrewriteRule import partvalnames, partnames
from wc.filter.rules.HtmlrewriteRule import part_num as _part_num
from wc.filter.rules.XmlrewriteRule import replacetypenums, replacetypenames
from wc.filter.rules.XmlrewriteRule import parse_xpath as _parse_xpath
from wc.filter.rules.FolderRule import FolderRule as _FolderRule
from wc.filter.rules.FolderRule import recalc_up_down as _recalc_up_down
from wc.filter.rules import register_rule as _register_rule
from wc.filter.rules import generate_sids as _generate_sids
from wc.filter import GetRuleFromName as _GetRuleFromName
from wc.rating.service import ratingservice
from wc.rating.service.ratingformat import parse_range as _parse_range

xmlreplacetypenames = sorted(replacetypenums.iterkeys())

# config vars
info = {
    "newfolder": False,
    "renamefolder": False,
    "disablefolder": False,
    "enablefolder": False,
    "removefolder": False,
    "newrule": False,
    "disablerule": False,
    "enablerule": False,
    "removerule": False,
    "htmlrewrite_addattr": False,
    "htmlrewrite_delattr": False,
    "folderup": False,
    "folderdown": False,
    "ruleup": False,
    "ruledown": False,
    "ruletitle": False,
    "ruledesc": False,
    "rulemimetype": False,
    "rulematchurl": False,
    "rulenomatchurl": False,
    "ruleurl": False,
    "rulereplacement": False,
    "ruleheadername": False,
    "ruleheadervalue": False,
    "ruleheaderfilter": False,
    "ruleheaderaction": False,
    "ruleimgwidth": False,
    "ruleimgheight": False,
    "rulerating": False,
    "rulesearch": False,
    "rulereplace": False,
    "ruletag": False,
    "ruleenclosedblock": False,
    "rulerewritepart": False,
    "rulerewritereplacement": False,
    "xmlselector": False,
    "xmlreplacetype": False,
    "xmlreplacevalue": False,
}

error = {
    "newfolder": False,
    "renamefolder": False,
    "disablefolder": False,
    "enablefolder": False,
    "removefolder": False,
    "newrule": False,
    "disablerule": False,
    "enablerule": False,
    "removerule": False,
    "htmlrewrite_addattr": False,
    "htmlrewrite_delattr": False,
    "folderup": False,
    "folderdown": False,
    "ruleup": False,
    "ruledown": False,
    "ruletitle": False,
    "ruleheadername": False,
    "ruleheaderfilter": False,
    "ruleheaderaction": False,
    "ruleimgwidth": False,
    "ruleimgheight": False,
    "ruleimgquality": False,
    "ruleimgminsize": False,
    "rulesearch": False,
    "ruletag": False,
    "rulerewritepart": False,
    "folderindex": False,
    "ruleindex": False,
    "selindex": False,
    "ratingvalue": False,
    "xmlselector": False,
    "xmlreplacetype": False,
}

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
# current header action value
curheaderaction = None
# current replace types
curreplacetypes = None
# only some rules allowed for new
newrulenames = list(rulenames[:])
newrulenames.remove('allowdomains')
newrulenames.remove('allowurls')
newrulenames.remove('blockdomains')
newrulenames.remove('blockurls')
newrulenames.sort()
# ruletype flag for tal condition
ruletype = {}


def _is_valid_header_filterstage (stage):
    """
    Check if stage is a valid header filter stage.
    """
    return stage in ('request', 'response', 'both')


def _is_valid_header_action (action):
    """
    Check if action is a valid header filter action.
    """
    return action in ('add', 'replace', 'remove')


def set_indexstr (folder):
    """
    Add indexstr variable to folder indicating the filter index.
    """
    if not folder:
        return
    l = len(folder.rules)
    if l > _rules_per_page:
        _calc_selindex(folder, curindex)
    else:
        folder.selindex = []
    folder.indexstr = u"(%d-%d/%d)" % \
            (curindex + 1, min(curindex + _rules_per_page, l), l)


def _exec_form (form, lang):
    """
    HTML CGI form handling.
    """
    # select a folder
    if form.has_key('selfolder'):
        _form_selfolder(_getval(form, 'selfolder'))
    if form.has_key('selindex') and curfolder:
        _form_selindex(_getval(form, 'selindex'))
    set_indexstr(curfolder)
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
    elif curfolder and form.has_key('disablefolder%d' % curfolder.oid):
        _form_disablefolder(curfolder)
    # enable current folder
    elif curfolder and form.has_key('enablefolder%d' % curfolder.oid):
        _form_enablefolder(curfolder)
    # remove current folder
    elif curfolder and form.has_key('removefolder%d' % curfolder.oid):
        _form_removefolder(curfolder)
    # make a new rule in current folder
    elif curfolder and form.has_key('newrule'):
        _form_newrule(_getval(form, 'newruletype'), lang)
    # disable current rule
    elif currule and form.has_key('disablerule%d' % currule.oid):
        _form_disablerule(currule)
    # enable current rule
    elif currule and form.has_key('enablerule%d' % currule.oid):
        _form_enablerule(currule)
    # remove current rule
    elif currule and form.has_key('removerule%d' % currule.oid):
        _form_removerule(currule)

    # rule specific submit buttons
    elif currule and form.has_key('addmimetype'):
        _form_rule_addmimetype(form)
    elif currule and form.has_key('delmimetypes'):
        _form_rule_delmimetypes(form)
    elif currule and form.has_key('addmatchurl'):
        _form_rule_addmatchurl(form)
    elif currule and form.has_key('delmatchurls'):
        _form_rule_delmatchurls(form)
    elif currule and form.has_key('addnomatchurl'):
        _form_rule_addnomatchurl(form)
    elif currule and form.has_key('delnomatchurls'):
        _form_rule_delnomatchurls(form)
    elif currule and form.has_key('addattr'):
        _form_htmlrewrite_addattr(form)
    elif currule and form.has_key('removeattrs') and form.has_key('delattr'):
        _form_htmlrewrite_removeattrs(form)

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
    """
    Set default values for form variables.
    """
    for key in info.keys():
        info[key] = False
    for key in error.keys():
        error[key] = False
    for f in config['folderrules']:
        f.selected = False
    global curfolder, currule, curparts, curindex, curfilterstage
    global curheaderaction, curreplacetypes
    curfolder = None
    currule = None
    curparts = None
    curfilterstage = None
    curheaderaction = None
    curindex = 0
    curreplacetypes = None


def _form_set_tags ():
    """
    Set folder and rule tags for displaying.
    """
    for folder in config['folderrules']:
        folder.selected = False
        for i, rule in enumerate(folder.rules):
            rule.selected = False
    if curfolder:
        curfolder.selected = True
        curfolder.rules_display = \
                        curfolder.rules[curindex:curindex+_rules_per_page]
    if currule:
        currule.selected = True


def _form_selfolder (index):
    """
    Select a folder.
    """
    try:
        index = int(index)
        global curfolder
        curfolder = [f for f in config['folderrules'] if f.oid == index][0]
    except (ValueError, IndexError, OverflowError):
        error['folderindex'] = True


def _form_selrule (index):
    """
    Select a rule.
    """
    try:
        index = int(index)
        global currule
        currule = [r for r in curfolder.rules if r.oid == index][0]
        # fill ruletype flags
        for rt in rulenames:
            ruletype[rt] = (currule.name == rt)
        # XXX this side effect is bad :(
        # fill part flags
        if currule.name == u"htmlrewrite":
            global curparts
            curparts = {}
            for i, part in enumerate(partvalnames):
                curparts[part] = (currule.part == i)
        elif currule.name == u"xmlrewrite":
            global curreplacetypes
            curreplacetypes = {}
            for name, num in replacetypenums.iteritems():
                curreplacetypes[name] = (currule.replacetypenum == num)
        elif currule.name == u"header":
            global curfilterstage, curheaderaction
            curfilterstage = {
                u'both': currule.filterstage == u'both',
                u'request': currule.filterstage == u'request',
                u'response': currule.filterstage == u'response',
            }
            curheaderaction = {
                u'add': currule.action == u'add',
                u'replace': currule.action == u'replace',
                u'remove': currule.action == u'remove',
            }
    except (ValueError, IndexError, OverflowError):
        error['ruleindex'] = True


def _form_selindex (index):
    """
    Display rules in curfolder from given index.
    """
    global curindex
    try:
        curindex = int(index)
    except (ValueError, OverflowError):
        error['selindex'] = True


def _calc_selindex (folder, index):
    """
    Calculate rule selection index of given folder.
    """
    # This index scales to several thousand rules per folder
    # which should be enough.
    res = [index-1000, index-250, index-50, index, index+50,
           index+250, index+1000]
    folder.selindex = [x for x in res
                       if 0 <= x < len(folder.rules) and x != index]


def _reinit_filters ():
    """
    Reinitialize filter modules.
    """
    config.init_filter_modules()


def _form_newfolder (foldername, lang):
    """
    Create a new folder.
    """
    if not foldername:
        error['newfolder'] = True
        return
    fd, filename = tempfile.mkstemp(u".zap", u"local_", config.configdir,
                                    text=True)
    # make file object
    fd = os.fdopen(fd, "wb")
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
    curfolder.write(fd=fd)
    fd.close()
    set_indexstr(curfolder)
    config['folderrules'].append(curfolder)
    _recalc_up_down(config['folderrules'])
    info['newfolder'] = True


def _form_renamefolder (foldername, lang):
    """
    Rename a folder.
    """
    if not foldername:
        error['renamefolder'] = True
        return
    curfolder.titles[lang] = foldername
    curfolder.write()
    info['renamefolder'] = True


def _form_disablefolder (folder):
    """
    Disable a folder.
    """
    if folder.disable:
        error['disablefolder'] = True
        return
    folder.disable = 1
    folder.write()
    _reinit_filters()
    info['disablefolder'] = True


def _form_enablefolder (folder):
    """
    Enable a folder.
    """
    if not folder.disable:
        error['enablefolder'] = True
        return
    folder.disable = 0
    folder.write()
    _reinit_filters()
    info['enablefolder'] = True


def _form_removefolder (folder):
    """
    Remove a folder.
    """
    config['folderrules'].remove(folder)
    global curfolder, currule
    curfolder = None
    currule = None
    try:
        os.remove(folder.filename)
        _reinit_filters()
        info['removefolder'] = True
    except OSError:
        error['removefolder'] = True


def _form_newrule (rtype, lang):
    """
    Create a new rule.
    """
    if rtype not in rulenames:
        error['newrule'] = True
        return
    # add new rule
    rule = _GetRuleFromName(rtype)
    rule.parent = curfolder
    rule.titles[lang] = _("No title")
    # compile data and register
    rule.compile_data()
    if config['development']:
        prefix = u"wc"
    else:
        prefix = u"lc"
    _generate_sids(prefix)
    curfolder.append_rule(rule)
    _recalc_up_down(curfolder.rules)
    curfolder.write()
    _reinit_filters()
    # select new rule
    _form_selrule(rule.oid)
    info['newrule'] = True


def _form_disablerule (rule):
    """
    Disable a rule.
    """
    if rule.disable:
        error['disablerule'] = True
        return
    rule.disable = 1
    curfolder.write()
    _reinit_filters()
    info['disablerule'] = True


def _form_enablerule (rule):
    """
    Enable a rule.
    """
    if not rule.disable:
        error['enablerule'] = True
        return
    rule.disable = 0
    curfolder.write()
    _reinit_filters()
    info['enablerule'] = True


def _form_removerule (rule):
    """
    Remove a rule.
    """
    rules = curfolder.rules
    rules.remove(rule)
    for i in range(rule.oid, len(rules)):
        rules[i].oid = i
    try:
        curfolder.write()
        _reinit_filters()
        # deselect current rule
        global currule
        currule = None
        info['removerule'] = True
    except OSError:
        error['removerule'] = True


def _form_htmlrewrite_addattr (form):
    """
    Add attribute to Htmlrewrite rule.
    """
    name = _getval(form, "attrname").strip()
    if not name:
        error['htmlrewrite_addattr'] = True
        return
    value = _getval(form, "attrval")
    currule.attrs[name] = value
    currule.attrs_ro[name] = re.compile(name)
    curfolder.write()
    info['htmlrewrite_addattr'] = True


def _form_htmlrewrite_removeattrs (form):
    """
    Remove attribute from Htmlrewrite rule.
    """
    toremove = _getlist(form, 'delattr')
    if toremove:
        for attr in toremove:
            if not currule.attrs.has_key(attr):
                error['htmlrewrite_delattr'] = True
                return
        for attr in toremove:
            del currule.attrs[attr]
            del currule.attrs_ro[attr]
        curfolder.write()
        info['htmlrewrite_delattr'] = True


def _swap_rules (rules, idx):
    """
    Swap rules[idx] and rules[idx+1]. Helper function for moving
    rules or folders up and down.
    """
    # swap rules
    rules[idx].oid, rules[idx+1].oid = rules[idx+1].oid, rules[idx].oid
    rules[idx], rules[idx+1] = rules[idx+1], rules[idx]


def _form_folder_down (oid):
    """
    Move folder with given oid one down.
    """
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
    """
    Move folder with given oid one up.
    """
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
    """
    Move rule with given oid one down.
    """
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
    """
    Move rule with given oid one up.
    """
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
    """
    Delegate rule apply to different apply_* functions.
    """
    # title and description apply for all rules:
    _form_rule_titledesc(form, lang)
    # delegate
    attr = "_form_apply_%s" % currule.name
    globals()[attr](form)
    if info:
        curfolder.write()


def _form_rule_titledesc (form, lang):
    """
    Change rule title and description.
    """
    title = _getval(form, 'rule_title')
    if not title:
        error['ruletitle'] = True
        return
    if title != currule.titles[lang]:
        currule.titles[lang] = title
        info['ruletitle'] = True
    desc = _getval(form, 'rule_description')
    if desc != currule.descriptions[lang]:
        currule.descriptions[lang] = desc
        info['ruledesc'] = True


def _form_rule_addmimetype (form):
    """
    Add rule MIME type.
    """
    if not form.has_key('newmimetype'):
        return
    mimetype = _getval(form, 'newmimetype').strip()
    if mimetype not in currule.mimes:
        currule.mimes.append(mimetype)
        currule.compile_mimes()
        curfolder.write()
        info['rulemimetype'] = True


def _form_rule_delmimetypes (form):
    """
    Remove rule MIME type.
    """
    toremove = [u for u in _getlist(form, 'rule_mimetypes')
                if u in currule.mimes]
    if toremove:
        for mime in toremove:
            currule.mimes.remove(mime)
        currule.compile_mimes()
        curfolder.write()
        info['rulemimetype'] = True


def _form_rule_addmatchurl (form):
    """
    Add rule match URL.
    """
    if not form.has_key('newmatchurl'):
        return
    matchurl = _getval(form, 'newmatchurl').strip()
    if matchurl not in currule.matchurls:
        currule.matchurls.append(matchurl)
        currule.compile_matchurls()
        curfolder.write()
        info['rulematchurl'] = True


def _form_rule_delmatchurls (form):
    """
    Remove rule match URL.
    """
    toremove = [u for u in _getlist(form, 'rule_matchurls')
                if u in currule.matchurls]
    if toremove:
        for matchurl in toremove:
            currule.matchurls.remove(matchurl)
        currule.compile_matchurls()
        curfolder.write()
        info['rulematchurl'] = True


def _form_rule_addnomatchurl (form):
    """
    Add rule nomatch URL.
    """
    if not form.has_key('newnomatchurl'):
        return
    nomatchurl = _getval(form, 'newnomatchurl').strip()
    if nomatchurl not in currule.nomatchurls:
        currule.nomatchurls.append(nomatchurl)
        currule.compile_nomatchurls()
        curfolder.write()
        info['rulenomatchurl'] = True


def _form_rule_delnomatchurls (form):
    """
    Remove rule nomatch URL.
    """
    toremove = [u for u in _getlist(form, 'rule_nomatchurls')
                if u in currule.nomatchurls]
    if toremove:
        for nomatchurl in toremove:
            currule.nomatchurls.remove(nomatchurl)
        currule.compile_nomatchurls()
        curfolder.write()
        info['rulenomatchurl'] = True


# The _form_apply_* methods handle all rule types.

def _form_apply_allow (form):
    """
    Change AllowRule.
    """
    url = _getval(form, 'rule_url').strip()
    if url != currule.url:
        currule.url = url
        info['ruleurl'] = True


def _form_apply_block (form):
    """
    Change BlockwRule.
    """
    _form_apply_allow(form)
    replacement = _getval(form, 'rule_replacement').strip()
    if replacement != currule.replacement:
        currule.replacement = replacement
        info['rulereplacement'] = True


def _form_apply_header (form):
    """
    Change HeaderRule.
    """
    name = _getval(form, 'rule_headername').strip()
    if not name:
        error['ruleheadername'] = True
    elif name != currule.header:
        currule.header = name
        info['ruleheadername'] = True
    value = _getval(form, 'rule_headervalue').strip()
    if value != currule.value:
        currule.value = value
        info['ruleheadervalue'] = True
    action = _getval(form, "rule_headeraction")
    if action != currule.action:
        if _is_valid_header_action(action):
            currule.action = action
            info['ruleheaderaction'] = True
        else:
            error['ruleheaderaction'] = True
        # select again because of side effect (XXX see above)
        _form_selrule(currule.oid)
    filterstage = _getval(form, 'rule_headerfilter')
    if filterstage != currule.filterstage:
        if _is_valid_header_filterstage(filterstage):
            currule.filterstage = filterstage
            info['ruleheaderfilter'] = True
        else:
            error['ruleheaderfilter'] = True
        # select again because of side effect (XXX see above)
        _form_selrule(currule.oid)


def _form_apply_image (form):
    """
    Change ImageRule.
    """
    width = _getval(form, 'rule_imgwidth').strip()
    try:
        width = int(width)
    except (ValueError, OverflowError):
        error['ruleimgwidth'] = True
        return
    if width != currule.width:
        currule.width = width
        info['ruleimgwidth'] = True
    height = _getval(form, 'rule_imgheight').strip()
    try:
        height = int(height)
    except (ValueError, OverflowError):
        error['ruleimgheight'] = True
        return
    if height != currule.height:
        currule.height = height
        info['ruleimgheight'] = True
    # XXX todo: image types


def _form_apply_imagereduce (form):
    """
    Change ImagereduceRule.
    """
    quality = _getval(form, 'rule_imgquality').strip()
    try:
        quality = int(quality)
    except (ValueError, OverflowError):
        error['ruleimgquality'] = True
        return
    if quality != currule.quality:
        currule.quality = quality
        info['ruleimgquality'] = True
    minsize = _getval(form, 'rule_imgminsize').strip()
    try:
        minsize = int(minsize)
    except (ValueError, OverflowError):
        error['ruleimgminsize'] = True
        return
    if minsize != currule.minimal_size_bytes:
        currule.minimal_size_bytes = minsize
        info['ruleimgminsize'] = True


def _form_apply_javascript (form):
    """
    Change JavascriptRule.
    """
    pass

def _form_apply_antivirus (form):
    """
    Change AntivirusRule.
    """
    pass

def _form_apply_nocomments (form):
    """
    Change NocommentsRule.
    """
    pass

def _form_apply_nojscomments (form):
    """
    Change NojscommentsRule.
    """
    pass


def _form_apply_rating (form):
    """
    Change RatingRule.
    """
    # rating categories
    for name, value in _get_prefix_vals(form, 'rating_'):
        ratingformat = ratingservice.get_ratingformat(name)
        if ratingformat is None:
            # unknown rating
            error['ratingvalue'] = True
            return
        if ratingformat.iterable:
            realvalue = value
        else:
            # Value is a range. The conversion returns None on error.
            realvalue = _parse_range(value)
        if realvalue is None or not ratingformat.valid_value(realvalue):
            error['ratingvalue'] = True
            return
        if currule.rating[name] != value:
            currule.rating[name] = value
            currule.compile_values()
            info['rulerating'] = True


def _form_apply_replace (form):
    """
    Change ReplaceRule.
    """
    # Note: do not strip() the search and replace form values.
    search = _getval(form, 'rule_search')
    if not search:
        error['rulesearch'] = True
        return
    if search != currule.search:
        currule.search = search
        _compileRegex(currule, "search")
        info['rulesearch'] = True
    replacement = _getval(form, 'rule_replace')
    if replacement != currule.replacement:
        currule.replacement = replacement
        info['rulereplace'] = True


def _form_apply_htmlrewrite (form):
    """
    Change HtmlrewriteRule.
    """
    tag = _getval(form, 'rule_tag').strip()
    if not tag:
        error['ruletag'] = True
        return
    if tag != currule.tag:
        currule.tag = tag
        info['ruletag'] = True
    enclosed = _getval(form, 'rule_enclosedblock').strip()
    if enclosed != currule.enclosed:
        currule.enclosed = enclosed
        _compileRegex(currule, "enclosed")
        info['ruleenclosedblock'] = True
    part = _getval(form, 'rule_rewritepart')
    partnum = _part_num(part)
    if partnum is None:
        error['rulerewritepart'] = True
        return
    if partnum != currule.part:
        currule.part = partnum
        info['rulerewritepart'] = True
        # select again because of side effect (XXX see above)
        _form_selrule(currule.oid)
    replacement = _getval(form, 'rule_rewritereplacement').strip()
    if replacement != currule.replacement:
        currule.replacement = replacement
        info['rulerewritereplacement'] =  True


def _form_apply_xmlrewrite (form):
    """
    Change XmlrewriteRule.
    """
    selector = _getval(form, 'rule_xmlselector').strip()
    if not selector:
        error['xmlselector'] = True
        return
    if selector != currule.selector:
        currule.selector = selector
        currule.selector_list = _parse_xpath(selector)
        info['xmlselector'] = True
    replacetypenum = _getval(form, 'rule_xmlreplacetype').strip()
    try:
        replacetypenum = int(replacetypenum)
    except (ValueError, OverflowError):
        error['xmlreplacetype'] = True
        return
    if replacetypenum != currule.replacetypenum:
        currule.replacetype = replacetypenames[replacetypenum]
        currule.replacetypenum = replacetypenum
        info['xmlreplacetype'] = True
    replacevalue = _getval(form, 'rule_xmlreplacevalue').strip()
    if replacevalue:
        if replacevalue != currule.value:
            currule.value = replacevalue
            info['xmlreplacevalue'] = True
    else:
        if currule.value:
            currule.value = u""
            info['xmlreplacevalue'] = True
