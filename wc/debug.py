# debug level constants (Quake-style)
ALWAYS = 0
BRING_IT_ON = 1
HURT_ME_PLENTY = 2
NIGHTMARE = 3

# the global debug level
DebugLevel = 0

from AnsiColor import colorize

def _text (color=None, *args):
    print >>sys.stderr, colorize(" ".join(map(str, args)), color=color)

# debug function, using the debug level
def debug (level, *args):
    if level <= DebugLevel:
        _text(*args)

def info (*args):
    args = list(args)
    args.append("info:")
    _text(color="default", *args)

def warn (*args):
    args = list(args)
    args.append("warning:")
    _text(color="bold;yellow", *args)

def error (*args):
    args = list(args)
    args.append("error:")
    _text(color="bold;red", *args)
