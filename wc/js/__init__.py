"""JavaScript helper classes and a Spidermonkey wrapper module"""

import re

def escape_js (script):
    script = script.replace('--', '-&#45;')
    script = re.sub(r'(?i)</script>', '&#60;/script>', script)
    return script


def unescape_js (script):
    script = script.replace('-&#45;', '--')
    script = script.replace('&#60;/script>', '</script>')
    return script
