import sys,os,string,time,webfilter

_ = webfilter.config._
from FXPy import *

HelpText = _("""

Proxy settings
==============

Port
----
Set the port adress the WebCleaner proxy is listening on.
Default value is 8080.

Logfile
-------
The name for the logfile can be empty (no logging), 'stdout'
(standard out) or a filename (relative or absolute).

Buffer size
-----------
The buffer size tells the proxy to read data in chunks with the
given size.

Timeout
-------
Network timeout after which the connection is disabled. Currently
this is used only with HTTPS connections, the other connections
have the system defined socket timeout.

Obfuscate IP
------------
When this checkbox is active (configuration file value = 1) the
proxy translates the numerical IP name into an integer number.
For example '5.7.9.11' gets mapped to
5*2^24 + 7*2^16 + 9*2^8 + 11*2^0 = 84347147

Debug level
-----------
Set the debugging level. Debug output is on stderr.
Debug levels:
0 - disabled (default)
1 - normal debug messages
2 - print requests and filtering
3 - detailed filter messages

Parent Proxy
------------
The parent proxy WebCleaner should use.

Parent Proxy Port
-----------------
The parent proxy port WebCleaner should use.

Rewriter
--------
Rewrite HTML code. This is very powerful and can filter
almost all advertising and other crap.

BinaryCharFilter
----------------
Replace illegal binary characters in HTML code like the quote
chars often found in Microsoft pages.

Header
------
Add, modify and delete HTTP headers of request and response.

Blocker
-------
Block specific sites by URL name.

GifImage
--------
Deanimates GIFs and removes all unwanted GIF image
extensions (for example GIF comments).

Compress
--------
Compression of documents with good compression ratio
like HTML, WAV, etc.


Rule settings
===================

Title
-----
The title of the filter

Description
-----------
A description what this filter does.

Language
--------
If you specify incompatible regular expressions
choose the appropriate language here.

Filename
--------
The name of the configuration file where these
filters are stored.

disable
-------
You can disable a whole folder (if its a FolderRule)
or single filter rules.


ImageRule settings
==================


FolderRule settings
===================


HeaderRule settings
===================


RewriteRule settings
====================


BlockRule settings
==================


AllowRule settings
==================
""")


def get_time(secs):
    """return formatted timestamp"""
    t = time.localtime(secs)
    return time.strftime("%d.%m.%Y %H:%M:%S", t)


# names of the filter types
Filternames = ['block', 'rewrite', 'allow', 'header', 'image', 'nocomments']

DEBUG_LEVEL=1
def debug(msg):
    if DEBUG_LEVEL:
       sys.stderr.write("DEBUG: "+msg+"\n")

def error(msg):
    sys.stderr.write("error: "+msg+"\n")

def loadIcon(app, filename):
    """load PNG icons from the ConfigDir directory"""
    filename = os.path.join(webfilter.config.ConfigDir, filename)
    if string.lower(filename[-3:])=='png':
        return FXPNGIcon(app, open(filename, 'rb').read())
    raise Exception, "only PNG graphics supported"


from ConfWindow import ConfWindow
