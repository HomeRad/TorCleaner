# standard xml entities
xmlentities = {
    'lt': '<',
    'gt': '>',
    'amp': '&',
    'quot': '"',
    'apos': "'",
}

_xml_table = map(lambda x: (x[1], "&"+x[0]+";"), xmlentities.items())
_unxml_table = map(lambda x: ("&"+x[0]+";", x[1]), xmlentities.items())
# order matters!
_xml_table.sort()
_unxml_table.sort()
_unxml_table.reverse()

def _apply_table (table, s):
    "apply a table of replacement pairs to str"
    for mapping in table:
        s = s.replace(mapping[0], mapping[1])
    return s

def xmlify (s):
    """quote characters for XML"""
    return _apply_table(_xml_table, s)

def unxmlify (s):
    """unquote characterx from XML"""
    return _apply_table(_unxml_table, s)

