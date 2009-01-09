# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
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
Filter modules.

Welcome to the wonderful world of software OSI layer 5 filtering.
To be able to filter every aspect of the HTTP protocol data, different
data stages are defined. Each of these can be separately filtered.

- HTTP request line
- HTTP request headers
- HTTP request content body
- HTTP response line
- HTTP response headers
- HTTP response content body

Since content bodies can be encoded (specified by the Content-Encoding
header) they both have methods for decoding, filtering and re-encoding
the body data.

The content body is usual HTML data for the browser, but could also be
something else. The type of data is specified by the Content-Type
header and resembles a MIME type.
Each filter for content bodies can apply to specific MIME type. For
example the XmlRewriter filter applies only to XML data.

You can add extern states for the filter by making a separate class
and passing it with the "attrs" parameter. Look at the HtmlRewriter
filter to see how it is done.

To communicate with the proxy, filters can throw FilterExceptions.
These must be handled in the appropriate proxy functions to work
properly.
"""
from __future__ import with_statement
import cgi
import os
from .. import log, LOG_FILTER, configuration, HtmlParser, TemplateDir
from ..http.header import WcMessage

# filter stages

# Filter complete request (eg. Block filter module)
# XXX make enum
STAGE_REQUEST = "Request"
# Outgoing header manglers
STAGE_REQUEST_HEADER = "Request header"
# May decode outgoing content.
STAGE_REQUEST_DECODE = "Request decode"
# May modify outgoing content.
STAGE_REQUEST_MODIFY = "Request modify"
# May modify outgoing content.
STAGE_REQUEST_ENCODE = "Request encode"
# Filter complete response
STAGE_RESPONSE = "Response"
# Filter complete response
STAGE_RESPONSE_HEADER = "Response header"
# May decode incoming content
STAGE_RESPONSE_DECODE = "Response decode"
# May modify incoming content
STAGE_RESPONSE_MODIFY = "Response modify"
# May encode incoming content
STAGE_RESPONSE_ENCODE = "Response encode"

FilterStages = (
    STAGE_REQUEST,
    STAGE_REQUEST_HEADER,
    STAGE_REQUEST_DECODE,
    STAGE_REQUEST_MODIFY,
    STAGE_REQUEST_ENCODE,
    STAGE_RESPONSE,
    STAGE_RESPONSE_HEADER,
    STAGE_RESPONSE_DECODE,
    STAGE_RESPONSE_MODIFY,
    STAGE_RESPONSE_ENCODE,
)
# shortcuts for decode/modify/encode
ClientFilterStages = FilterStages[2:5]
ServerFilterStages = FilterStages[7:10]


class FilterException (StandardError):
    """Generic filter exception."""
    pass


class FilterWait (FilterException):
    """Raised when a filter waits for more data. The filter should
    buffer the already passed data until the next call (and until
    it has enough data to proceed)."""
    pass


class FilterRating (FilterException):
    """Raised when a filter detected rated content.
    The proxy must not have sent any content."""
    pass


class FilterProxyError (FilterException):
    """Raised to signal a proxy error which should be delegated to
    the HTTP client."""

    def __init__ (self, status, msg, text):
        self.status = status
        self.msg = msg
        self.text = text


def GetRuleFromName (name):
    """Return new rule instance for given rule name."""

    name = '%sRule' % name.capitalize()
    mod = __import__("wc.filter.rules.%s" % name, {}, {}, [name])
    return getattr(mod, name)()


def applyfilter (filterstage, data, fun, attrs):
    """Apply all filters which are registered in the given filter stage.
    For different filter stages we have different data objects.
    Look at the filter examples.
    One can prevent all filtering with the 'nofilter' attribute,
    or deactivate single filter modules with 'nofilter-<name>',
    for example 'nofilter-blocker'."""
    attrs['filterstage'] = filterstage
    log.debug(LOG_FILTER, "Filter (%s) %d bytes in %s..",
                        fun, len(data), filterstage)
    if attrs.get('nofilter') or (fun != 'finish' and not data):
        log.debug(LOG_FILTER, "..don't filter")
        return data
    for f in configuration.config['filterlist'][filterstage]:
        log.debug(LOG_FILTER, "..filter with %s" % f)
        if f.applies_to_mime(attrs['mime']) and \
           not "nofilter-%s" % str(f).lower() in attrs:
            log.debug(LOG_FILTER, "..applying")
            data = getattr(f, fun)(data, attrs)
        else:
            log.debug(LOG_FILTER, "..not applying (mime %s)" % attrs['mime'])
    log.debug(LOG_FILTER, "..result %d bytes", len(data))
    return data


def get_filterattrs (url, localhost, filterstages, browser='Calzilla/6.0',
                     clientheaders=None, serverheaders=None, headers=None):
    """Init external state objects."""
    if clientheaders is None:
        clientheaders = WcMessage()
    if serverheaders is None:
        serverheaders = WcMessage()
    if headers is None:
        headers = WcMessage()
    attrheaders = {
        'client': clientheaders,
        'server': serverheaders,
        'data': headers,
    }
    attrs = {
        'url': url,
        'nofilter': configuration.config.nofilter(url),
        'mime' : headers.get('Content-Type'),
        'mime_types': None,
        'headers': attrheaders,
        'browser': browser,
    }
    if attrs['mime']:
        charset = HtmlParser.get_ctype_charset(attrs['mime'])
        if charset is not None:
            attrs['charset'] = charset
    for f in configuration.config['filtermodules']:
        # note: get attributes of _all_ filters since the
        # mime type can change dynamically
        f.update_attrs(attrs, url, localhost, filterstages, attrheaders)
    return attrs


def which_filters (url, mime):
    """Deduce which filters apply to the given url/mime."""
    filters_by_stage = {}
    for stage in FilterStages:
        filters = configuration.config['filterlist'][stage]
        applies = []
        for filter in filters:
            rules = filter.which_rules(url, mime)
            if not filter.applies_to_stages([stage]):
                applies.append((False, 'stage', filter, rules))
            elif not filter.applies_to_mime(mime):
                applies.append((False, 'mime', filter, rules))
            else:
                applies.append((True, '', filter, rules))
        filters_by_stage[stage] = applies
    return filters_by_stage


def show_rules (url, mime):
    """Build an html document showing which rules are enabled for the given
    url and mime type."""
    lang = 'en'
    filters_by_stage = which_filters(url, mime)
    s = ''
    for stage in FilterStages:
        s += '<h3>Stage: %s</h3>\n<ul>\n' % stage
        filters = filters_by_stage[stage]
        for enabled, why, filter, rules in filters:
            klass = enabled and 'filter_on' or 'filter_off hide'
            filter_name = cgi.escape(str(filter))
            s += '<li class="%s" title="%s">filter %s with %d rules\n<ul>\n' % \
                (klass, why, filter_name, len(rules))
            for enabled, why, rule in rules:
                klass = enabled and 'rule_on' or 'rule_off hide'
                name = cgi.escape(rule.titles[lang])
                desc = cgi.escape(rule.descriptions[lang], True)
                folder = cgi.escape(rule.parent.titles[lang])
                base = 'http://localhost:8088/filterconfig.html.en'
                folder_loc = '%s?selfolder=%d' % (base, rule.parent.oid)
                folder_link = '<a href="%s">%s</a>' % (folder_loc, folder)
                rule_loc = '%s&selrule=%d' % (folder_loc, rule.oid)
                rule_link = '<a href="%s">%s</a>' % (rule_loc, name)
                s += '<li class="%s" title="%s">rule %s in folder %s</li>\n' % \
                    (klass, why, rule_link, folder_link)
            s += '</ul></li>\n'
        s += '</ul>\n'
    ruleset = s
    theme = configuration.config["gui_theme"]
    page_template = os.path.join(TemplateDir, theme, 'show_rules.html')
    proxy = configuration.config['bindaddress'], configuration.config['port']
    enabled_img = 'http://%s:%s/rule_enabled.png' % proxy
    disabled_img = 'http://%s:%s/rule_disabled.png' % proxy
    with open(page_template, 'r') as fd:
        return fd.read() % locals()

