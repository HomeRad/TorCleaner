# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Filter invalid binary chars from HTML.
"""
import string
import re
from . import Filter, STAGE_RESPONSE_MODIFY

# for utf charset check (see below)
is_utf = re.compile(r"text/html;\s*charset=utf-8", re.I).search

# character replacement table.
charmap = (
    # Replace Null byte with space
    (chr(0x0), chr(0x20)),  # ' '
    # Replace Microsoft quotes
    (chr(0x84), chr(0x22)), # '"'
    (chr(0x91), chr(0x60)), # '`'
    (chr(0x92), chr(0x27)), # '\''
    (chr(0x93), chr(0x22)), # '"'
    (chr(0x94), chr(0x22)), # '"'
)
charmap_in = ''.join(x[0] for x in charmap)
charmap_out = ''.join(x[1] for x in charmap)


class BinaryCharFilter(Filter.Filter):
    """
    Replace binary characters, often found in Microsoft HTML documents,
    with their correct HTML equivalent.
    """

    enable = True

    def __init__(self):
        """
        Initialize stages and mime list.
        """
        stages = [STAGE_RESPONSE_MODIFY]
        mimes = ['text/html']
        super(BinaryCharFilter, self).__init__(stages=stages, mimes=mimes)
        self.transe = string.maketrans(charmap_in, charmap_out)

    def doit(self, data, attrs):
        """
        Filter given data.
        """
        # The HTML parser does not yet understand Unicode, so this hack
        # disables the binary char filter in this case.
        if is_utf(data):
            attrs['charset'] = "utf-8"
        if attrs.get('charset') == "utf-8":
            return data
        return data.translate(self.transe)
