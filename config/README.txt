                    Configuration Help
                   ====================

For the configuration file syntax see webcleaner.dtd and filter.dtd.

Some settings explained
-----------------------

Proxy GUI settings (configfile settings):
Port (port)
        Set the port adress the WebCleaner proxy is listening on.
	Default value is 8080.

Logfile (logfile)
        The name for the logfile can be empty (no logging), 'stdout'
	(standard out) or a filename (relative or absolute).

Buffer size (buffersize)
        The buffer size tells the proxy to read data in chunks with the
	given size.

Timeout (timeout)
        Network timeout after which the connection is disabled. Currently
	this is used only with HTTPS connections, the other connections
	have the system defined socket timeout.

Obfuscate IP (obfuscateip)
        When this checkbox is active (configuration file value = 1) the
	proxy translates the numerical IP name into an integer number.
	For example '5.7.9.11' gets mapped to
	5*2^24 + 7*2^16 + 9*2^8 + 11*2^0 = 84347147

Debug level (debuglevel)
        Set the debugging level. Debug output is on stderr.
	Debug levels:
        0 - disabled (default)
        1 - normal debug messages
        2 - print requests and filtering
        3 - detailed filter messages

Rewriter (Rewriter):
        Rewrite HTML code. This is very powerful and can filter almost all
        advertising and other crap.

BinaryCharFilter (BinaryCharFilter):
        Replace illegal binary characters in HTML code like the quote chars
        often found in Microsoft pages.

Header (Header):
        Add, modify and delete HTTP headers of request and response.

Blocker (Blocker):
        Block specific sites by URL name.

GifImage (GifImage):
        Deanimates GIFs and removes all unwanted GIF image extensions
        (for example GIF comments).

Compress (Compress):
        Compression of documents with good compression ratio like HTML, 
	WAV, etc.

Filter GUI settings (configfile settings):
Title (title):
        The title of the filter.

Description (desc):
        Some good description what this filter does.
	
Language (language):
        If you specify incompatible regular expressions choose the 
	appropriate language here.

Filename ():
        The name of the configuration file where these filters are
	stored.
