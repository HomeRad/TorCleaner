import sys,os,time,wc
from wc import _
from FXPy.fox import *

HelpText = _("""

Proxy settings
==============

User/Password
-------------
Require proxy authentication with the given user and password.
The password is saved base64 encoded.

Port
----
Set the port adress the WebCleaner proxy is listening on.

Logfile
-------
The name for the logfile can be empty (no logging), '<stdout>'
(standard out) or a filename (relative or absolute).

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
This is known NOT to work with a squid proxy as a parent proxy.

Debug level
-----------
Set the debugging level. Debug output is on stderr.
Debug levels:
0 - disabled (default)
1 - normal debug messages
2 - print requests and filtering
3 - detailed filter messages

Parent Proxy Host/Port
----------------------
The hostname/port adress of the parent proxy WebCleaner should use.

Parent Proxy User/Password
--------------------------
Authentication for the parent proxy. The password is saved base64
encoded.

Rewriter
--------
Rewrite HTML code. This is very powerful and can filter
almost all advertising and other crap.

Replacer
--------
Replace regular expressions in (HTML) data streams.

BinaryCharFilter
----------------
Replace illegal binary characters in HTML code like the quote
chars often found in Microsoft pages.

Header
------
Add, modify and delete HTTP headers of request and response.

Blocker
-------
Block or allow specific sites by URL name.

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
The title of the filter rule

Description
-----------
A description what this filter rule does.

Language
--------
If you specify incompatible regular expressions
choose the appropriate programming language here.

Filename
--------
The name of the configuration file where these
filters are stored (cannot be changed).

disable
-------
You can disable a single rule or all rules in a folder.

Match url
---------
Applies this rule only to urls matching the regular expression

Dont match url
--------------
Applies this rule only to urls not matching the regular expression
Match url entries are tested first.


ImageRule settings (requires GifImage module)
==================

Image width/height
------------------
The width/height of the image to be blocked.


HeaderRule settings (requires Header module)
===================

Header name
-----------
Name of the header to be modified/added/deleted.

Header value
------------
If empty, delete the header. Else add or, if already there modify the
header.


RewriteRule settings (requires Rewriter module)
====================


BlockRule settings (requires Blocker module)
==================

URL Scheme/Host/Port/Path/Parameters/Query/Fragment
---------------------------------------------------
If any of these are non-empty, the respective url part must match
the regular expression.

Blocked URL
-----------
Fetch data from this url instead the default block url. Be sure to
provide the correct document type.


AllowRule settings (requires Blocker module)
==================

URL Scheme/Host/Port/Path/Parameters/Query/Fragment
---------------------------------------------------
If any of these are non-empty, the corresponding url part must match
the regular expression.

""")


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
    raise Exception, "only PNG graphics supported"

