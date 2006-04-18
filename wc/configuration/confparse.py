# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2006 Bastian Kleineidam
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
Parse configuration data.
"""

import sets
import xml.parsers.expat

from wc.XmlUtils import xmlquoteattr

##### xml parsers #########

rulenames = (
  u'block',
  u'blockurls',
  u'blockdomains',
  u'allowurls',
  u'allowdomains',
  u'allow',
  u'header',
  u'image',
  u'imagereduce',
  u'nocomments',
  u'nojscomments',
  u'javascript',
  u'replace',
  u'rating',
  u'antivirus',
  u'htmlrewrite',
  u'xmlrewrite',
)
_nestedtags = (
  u'title', u'description',
  # urlrule nested tag names
  u'matchurl', u'nomatchurl',
  # htmlrewriter rule nested tag names
  u'attr', u'enclosed', u'replacement',
  # rating rule nested tag names
  u'url', u'limit',
)
# make sure no name clashes occur between tag names
for _x in _nestedtags:
    assert _x not in rulenames


def make_xmlparser ():
    """
    Return a new xml parser object.
    """
    # note: this parser returns unicode strings
    return xml.parsers.expat.ParserCreate()


class ParseException (Exception):
    """
    Exception thrown at parse errors.
    """
    pass


class BaseParser (object):
    """
    Base class for parsing xml config files.
    """

    def __init__ (self, filename):
        """
        Initialize filename and configuration for this parser.
        """
        super(BaseParser, self).__init__()
        self.filename = filename
        # error condition
        self.error = None
        # set by _preparse() and _postparse()
        self.xmlparser = None

    def _preparse (self):
        """
        Set handler functions before parsing.
        """
        self.xmlparser = make_xmlparser()
        self.xmlparser.StartElementHandler = self.start_element
        self.xmlparser.EndElementHandler = self.end_element
        self.xmlparser.CharacterDataHandler = self.character_data

    def _postparse (self):
        """
        Remove handler functions after parsing; avoids cyclic references.
        """
        self.xmlparser.StartElementHandler = None
        self.xmlparser.EndElementHandler = None
        self.xmlparser.CharacterDataHandler = None
        # note: expat parsers cannot be reused
        self.xmlparser = None

    def parse (self, fp=None):
        """
        Parse the stored filename, or another source given by fp.
        """
        assert wc.log.debug(wc.LOG_PROXY, "Parsing %s", self.filename)
        if fp is None:
            fp = file(self.filename)
        self._preparse()
        try:
            try:
                self.xmlparser.ParseFile(fp)
            except (xml.parsers.expat.ExpatError, ParseException):
                wc.log.exception(wc.LOG_PROXY, "Error parsing %s",
                                 self.filename)
                raise SystemExit("parse error in %s" % self.filename)
        finally:
            self._postparse()

    def start_element (self, name, attrs):
        """
        Basic start element method doing nothing.
        """
        pass

    def end_element (self, name):
        """
        Basic end element method doing nothing.
        """
        pass

    def character_data (self, data):
        """
        Basic character data method doing nothing.
        """
        pass


class ZapperParser (BaseParser):
    """
    Parser class for *.zap filter configuration files.
    """

    def __init__ (self, filename, compile_data=True):
        """
        Initialize filename, configuration and compile flag.
        """
        super(ZapperParser, self).__init__(filename)
        from wc.filter.rules.FolderRule import FolderRule
        self.folder = FolderRule(filename=filename)
        self.cmode = None
        self.rule = None
        self.compile_data = compile_data

    def start_element (self, name, attrs):
        """
        Handle start tag of folder, rule or nested element.
        """
        super(ZapperParser, self).start_element(name, attrs)
        if self.error:
            return
        self.cmode = name
        if name in rulenames:
            self.rule = wc.filter.GetRuleFromName(name)
            self.rule.fill_attrs(attrs, name)
            self.folder.append_rule(self.rule)
        # tag has character data
        elif name in _nestedtags:
            if self.rule is None:
                self.folder.fill_attrs(attrs, name)
            else:
                self.rule.fill_attrs(attrs, name)
        elif name == 'folder':
            self.folder.fill_attrs(attrs, name)
        else:
            wc.log.warn(wc.LOG_FILTER, _("unknown tag name %r"), name)
            self.error = name
            self.cmode = None

    def end_element (self, name):
        """
        Handle end tag of folder, rule or nested element.
        """
        if self.error:
            if name == self.error:
                self.error = None
        else:
            self.cmode = None
            if self.rule is None:
                self.folder.end_data(name)
            else:
                self.rule.end_data(name)
            if name in rulenames:
                if self.compile_data:
                    self.rule.compile_data()
            elif name == 'folder':
                if self.compile_data:
                    self.folder.compile_data()

    def character_data (self, data):
        """
        Handle rule of folder character data.
        """
        if self.error:
            pass
        elif self.cmode:
            if self.rule is None:
                self.folder.fill_data(data, self.cmode)
            else:
                self.rule.fill_data(data, self.cmode)


class WConfigParser (BaseParser):
    """
    Parser class for webcleaner.conf configuration files.
    """

    def __init__ (self, filename, _config):
        """
        Initialize filename, configuration and compile flag.
        """
        super(WConfigParser, self).__init__(filename)
        self.config = _config

    def start_element (self, name, attrs):
        """
        Handle xml configuration for webcleaner attributes and filter
        modules.
        """
        if self.error:
            return
        if name == 'webcleaner':
            for key, val in attrs.iteritems():
                self.config[key] = val
            for key in ('port', 'sslport', 'parentproxyport', 'timeout',
                        'auth_ntlm', 'colorize', 'development', 'try_google',
                        'sslgateway',):
                self.config[key] = int(self.config[key])
            if self.config['nofilterhosts'] is not None:
                strhosts = self.config['nofilterhosts']
                self.config['nofilterhosts'] = strhosts.split(",")
            else:
                self.config['nofilterhosts'] = []
            if self.config['allowedhosts'] is not None:
                hosts = self.config['allowedhosts'].split(',')
                self.config['allowedhosts'] = hosts
                self.config['allowedhostset'] = wc.ip.hosts2map(hosts)
            else:
                self.config['allowedhosts'] = []
                self.config['allowedhostset'] = [sets.Set(), []]
        elif name == 'filter':
            assert wc.log.debug(wc.LOG_FILTER, "enable filter module %s",
                         attrs['name'])
            self.config['filters'].append(attrs['name'])
        else:
            wc.log.warn(wc.LOG_PROXY, _("unknown tag name %r"), name)
            self.error = name

    def end_element (self, name):
        """
        Handle error case.
        """
        if self.error:
            if name == self.error:
                self.error = None
