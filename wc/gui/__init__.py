import sys, os, time, wc
from FXPy.fox import *


def get_time (secs):
    """return formatted timestamp"""
    t = time.localtime(secs)
    return time.strftime("%Y-%m-d %H:%M:%S", t)

# names of the filter types
Filternames = ['block', 'rewrite', 'allow', 'header', 'image', 'nocomments']

def error (msg):
    sys.stderr.write("error: "+msg+"\n")

def loadIcon (app, filename):
    """load PNG icons from the ConfigDir directory"""
    filename = os.path.join(wc.ConfigDir, filename)
    if filename[-3:].lower()=='png':
        return FXPNGIcon(app, open(filename, 'rb').read())
    raise Exception("only PNG graphics supported")

