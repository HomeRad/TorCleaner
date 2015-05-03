# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Filter a HTML stream.
"""
from . import Filter, STAGE_RESPONSE_MODIFY
from .html.HtmlParser import HtmlParser
from .html.HtmlFilter import HtmlFilter
from .. import configuration


DefaultCharset = 'iso-8859-1'

class HtmlRewriter(Filter.Filter):
    """
    This filter can rewrite HTML tags. It uses a parser class.
    """

    enable = True

    def __init__(self):
        """
        Init HTML stages and mimes.
        """
        stages = [STAGE_RESPONSE_MODIFY]
        rulenames = ['htmlrewrite', 'nocomments', 'javascript', 'rating']
        mimes = ['text/html']
        super(HtmlRewriter, self).__init__(stages=stages, rulenames=rulenames,
                                       mimes=mimes)

    def filter(self, data, attrs):
        """
        Feed data to HTML parser.
        """
        if 'htmlrewriter_filter' not in attrs:
            return data
        p = attrs['htmlrewriter_filter']
        p.feed(data)
        if p.bom is not None:
            bom, p.bom = p.bom, None
            return bom + p.getoutput()
        return p.getoutput()

    def finish(self, data, attrs):
        """
        Feed data to HTML parser and flush buffers.
        """
        if 'htmlrewriter_filter' not in attrs:
            return data
        p = attrs['htmlrewriter_filter']
        # feed even if data is empty
        p.feed(data)
        # flushing can raise FilterWait exception
        p.flush()
        p.tagbuf2data()
        return p.getoutput()

    def update_attrs(self, attrs, url, localhost, stages, headers):
        """
        We need a separate filter instance for stateful filtering.
        """
        if not self.applies_to_stages(stages):
            return
        super(HtmlRewriter, self).update_attrs(attrs, url, localhost,
                                               stages, headers)
        rewrites = []
        ratings = []
        # look if headers already have rating info
        opts = {'comments': True, 'jscomments': True, 'javascript': False}
        for rule in self.rules:
            if not rule.applies_to_url(url):
                continue
            if rule.name == 'htmlrewrite':
                rewrites.append(rule)
            elif rule.name == 'nocomments':
                opts['comments'] = False
            elif rule.name == 'nojscomments':
                opts['jscomments'] = False
            elif rule.name == 'javascript':
                opts['javascript'] = True
            elif rule.name == 'rating' and rule.use_extern:
                rating_storage = configuration.config['rating_storage']
                if url not in rating_storage:
                    ratings.append(rule)
        # generate the HTML filter
        handler = HtmlFilter(rewrites, ratings, url, localhost, **opts)
        p = HtmlParser(handler)
        #htmlparser.debug(1)
        # the handler is modifying parser buffers and state
        handler.htmlparser = p
        attrs['htmlrewriter_filter'] = p
