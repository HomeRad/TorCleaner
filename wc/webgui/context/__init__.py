# -*- coding: iso-8859-1 -*-
"""for each template/<theme>/<file>.html there is a context/<file>_html.py
module delivering the page content values"""

def getval (item):
    """return a formfield value"""
    if isinstance(item, list):
        return item[0]
    if hasattr(item, "value"):
        return item.value
    return item
