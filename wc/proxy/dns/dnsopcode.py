# See RFC 1035 for more info

# Opcode values in message header (section 4.1.1)

QUERY = 0
IQUERY = 1
STATUS = 2

# Construct reverse mapping dictionary

_names = dir()
opcodemap = {}
for _name in _names:
    if _name[0]!='_':
        opcodemap[eval(_name)] = _name

def opcodestr(opcode):
    return opcodemap.get(opcode, `opcode`)
