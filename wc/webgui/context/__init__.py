# -*- coding: iso-8859-1 -*-
"""for each template/<theme>/<file>.html there is a context/<file>_html.py
module delivering the page content values"""

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
