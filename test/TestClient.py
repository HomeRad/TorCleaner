# -*- coding: iso-8859-1 -*-
from wc.proxy import Connection
class TestClient (Connection.Connection):
    """States:
        request (read first line)
        headers (read HTTP headers)
        content (read HTTP POST content data)
        receive (read any additional data and forward it to the server)
        done    (done reading data, response already sent)
    """

    def __init__ (self, sock, addr):
        super(TestClient, self).__init__(sock=sock)
        self.addr = addr
        self.state = 'request'
        self.sequence_number = 1
        self.request = ''
        self.decoders = [] # Handle each of these, left to right
        self.headers = {}
        self.bytes_remaining = None # for content only
        self.content = ''
        self.protocol = 'HTTP/1.0'
        self.url = ''


    def error (self, status, msg, txt='', auth=''):
        self.state = 'done'
        debug(PROXY, '%s error %s (%d)', str(self), `msg`, status)
        err = i18n._('Proxy Error %d %s') % (status, msg)
        if txt:
            err = "%s (%s)" % (err, txt)
        form = None
        # this object will call server_connected at some point
        WebConfig(self, '/error.html', form, self.protocol, self.headers,
              context={'error': err,}, status=status, msg=msg, auth=auth)


    def __repr__ (self):
        if self.request:
            try:
                extra = self.request.split()[1]
            except IndexError:
                extra = '???' + self.request
        else:
            extra = 'being read'
        return '<%s:%-8s persistent=%s %s>'%('testclient', self.state, self.persistent, extra)


    def process_read (self):
        # hmm, this occurs with WebCleaner as a parent of Oops Http Proxy
        assert not (self.state in ('receive','closed') and self.recv_buffer and self.method!='CONNECT'),\
         'client in state %s sent data %s'%(self.state, `self.recv_buffer`)

        while True:
            bytes_before = len(self.recv_buffer)
            state_before = self.state
            try:
                handler = getattr(self, 'process_'+self.state)
            except AttributeError:
                handler = lambda: None # NO-OP
            handler()
            bytes_after = len(self.recv_buffer)
            if (self.state=='done' or
                (bytes_before==bytes_after and state_before==self.state)):
                break


    def process_request (self):
        # One newline ends request
        i = self.recv_buffer.find('\r\n')
        if i < 0: return
        # self.read(i) is not including the newline
        self.request = self.read(i)
        try:
            self.method, self.url, protocol = self.request.split()
        except ValueError:
            self.error(400, i18n._("Can't parse request"))
            return
        if self.method not in allowed_methods:
            self.error(405, i18n._("Method Not Allowed"))
            return
        # fix broken url paths
        self.url = norm_url(self.url)
        if not self.url:
            self.error(400, i18n._("Empty URL"))
            return
        self.protocol = fix_http_version(protocol)
        self.http_ver = get_http_version(self.protocol)
        self.request = "%s %s %s" % (self.method, self.url, self.protocol)
        debug(PROXY, "%s request %s", str(self), `self.request`)
        # enforce a maximum url length
        if len(self.url) > 1024:
            error(PROXY, "%s request url length %d chars is too long", str(self), len(self.url))
            self.error(400, i18n._("URL too long"))
            return
        if len(self.url) > 255:
            warn(PROXY, "%s request url length %d chars is very long", str(self), len(self.url))
        self.state = 'headers'


    def process_headers (self):
        # Two newlines ends headers
        i = self.recv_buffer.find('\r\n\r\n')
        if i < 0: return
        i += 4 # Skip over newline terminator
        # the first 2 chars are the newline of request
        fp = StringIO(self.read(i)[2:])
        msg = WcMessage(fp)
        # put unparsed data (if any) back to the buffer
        msg.rewindbody()
        self.recv_buffer = fp.read() + self.recv_buffer
        debug(PROXY, "%s client headers \n%s", str(self), str(msg))
        # look if client wants persistent connections
        if self.http_ver >= (1,1):
            self.persistent = not has_header_value(msg, 'Proxy-Connection', 'Close') and \
                              not has_header_value(msg, 'Connection', 'Close')
        elif self.http_ver >= (1,0):
            self.persistent = has_header_value(msg, 'Proxy-Connection', 'Keep-Alive') or \
                              has_header_value(msg, 'Connection', 'Keep-Alive')
        else:
            self.persistent = False
        # work on these headers
        self.compress = client_set_headers(msg)
        # filter headers
        self.headers = msg
        # add decoders
        self.decoders = []
        self.bytes_remaining = get_content_length(self.headers)
        # chunked encoded
        if self.headers.has_key('Transfer-Encoding'):
            # XXX don't look at value, assume chunked encoding for now
            debug(PROXY, '%s Transfer-encoding %s', str(self), `self.headers['Transfer-encoding']`)
            self.decoders.append(UnchunkStream())
            client_remove_encoding_headers(self.headers)
            self.bytes_remaining = None
        if self.method in ['OPTIONS', 'TRACE'] and \
           client_get_max_forwards(self.headers)==0:
            # XXX display options ?
            self.state = 'done'
            ServerHandleDirectly(self, '%s 200 OK'%self.protocol, 200,
                      WcMessage(StringIO('Content-Type: text/plain\r\n\r\n')), '')
            return
        self.state = 'content'


    def process_content (self):
        data = self.read(self.bytes_remaining)
        if self.bytes_remaining is not None:
            # Just pass everything through to the server
            # NOTE: It's possible to have 'chunked' encoding here,
            # and then the current system of counting bytes remaining
            # won't work; we have to deal with chunks
            self.bytes_remaining -= len(data)
        is_closed = False
        for decoder in self.decoders:
            data = decoder.decode(data)
            is_closed = decoder.closed or is_closed
        self.content += data
        underflow = self.bytes_remaining is not None and \
                    self.bytes_remaining < 0
        if underflow:
            warn(PROXY, "client received %d bytes more than content-length",
                 (-self.bytes_remaining))
        if is_closed or self.bytes_remaining==0:
            if self.content and not self.headers.has_key('Content-Length'):
                self.headers['Content-Length'] = "%d\r"%len(self.content)
            # We're done reading content
            self.state = 'response'
            self.server_request()


    def server_request (self):
        assert self.state=='response', "%s server_request in state response" % str(self)
        # XXX make test


    def handle_close (self):
        # The client closed the connection, so cancel the server connection
        debug(PROXY, '%s handle_close', str(self))
        self.send_buffer = ''
        super(TestClient, self).handle_close()


    def handle_local (self):
        assert self.state=='receive'
        # reject invalid methods
        if self.method not in ['GET', 'POST', 'HEAD']:
            self.error(403, i18n._("Invalid Method"))
            return
        # get cgi form data
        form = self.get_form_data()
        debug(PROXY, '%s handle_local', str(self))
        # this object will call server_connected at some point
        WebConfig(self, self.url, form, self.protocol, self.headers)


    def get_form_data (self):
        form = None
        if self.method=='GET':
            # split off query string and parse it
            qs = urlparse.urlsplit(self.url)[3]
            if qs:
                form = cgi.parse_qs(qs)
        elif self.method=='POST':
            # XXX this uses FieldStorage internals
            form = cgi.FieldStorage(fp=StringIO(self.content),
                                    headers=self.headers,
                                    environ={'REQUEST_METHOD': 'POST'})
        return form


    def close (self):
        debug(PROXY, '%s close', str(self))
        self.state = 'closed'
        super(TestClient, self).close()


    def reuse (self):
        debug(PROXY, '%s reuse', str(self))
        self.state = 'request'
        self.persistent = False
