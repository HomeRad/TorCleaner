# -*- coding: iso-8859-1 -*-
"""for each template/<theme>/<file>.html there is a context/<file>_html.py
module delivering the page content values"""
import re

def getval (form, key):
    """return a formfield value"""
    if not form.has_key(key):
        return ''
    item = form[key]
    if isinstance(item, list):
        return item[0]
    if hasattr(item, "value"):
        return item.value
    return item


def getlist (form, key):
    """return a list of formfield values"""
    if not form.has_key(key):
        return []
    item = form[key]
    if isinstance(item, list):
        return [x.value for x in item]
    if hasattr(item, "value"):
        return [item.value]
    return [item]

is_safe = re.compile(r"^[a-zA-Z0-9 ]$").match
def filter_safe (text):
    """safe whitelist quoting for html content"""
    return "".join([c for c in text if is_safe(c)])
