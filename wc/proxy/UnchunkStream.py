# encoding_chunked, amitp@cs.stanford.edu, March 2000
#
# Deal with Transfer-encoding: chunked [HTTP/1.1]

# TEST CASE:
#    http://www.apache.org/

from string import strip,find,atoi

class UnchunkStream:
    # States:
    #   if bytes_remaining is None:
    #      we're in the "need chunk size" state
    #   else:
    #      we're reading up to bytes_remaining elements of data
    def __init__(self):
        self.buffer = ''
        self.bytes_remaining = None
        self.closed = 0
        
    def decode(self, s):
        self.buffer += s
        s = ''

        while self.buffer and not self.closed:
            # Keep looking for alternating chunk lengths and chunk content
            
            if self.bytes_remaining is None:
                # We want to find a chunk length
                i = find(self.buffer, '\n')
                if i >= 0:
                    # We have a line; let's hope it's a chunk length
                    line = strip(self.buffer[:i])
                    # Remove this line from the buffer
                    self.buffer = self.buffer[i+1:]
                    if line:
                        # NOTE: chunklen can be followed by r";.*"
                        self.bytes_remaining = atoi(line, 16) # chunklen is hex
                        #print 'chunk len:', self.bytes_remaining
                        if self.bytes_remaining == 0:
                            # End of stream
                            self.closed = 1
                            # NOTE: at this point, we should read 
                            # footers until we get to a blank line
                else:
                    break
            if self.bytes_remaining is not None:
                # We know how many bytes we need
                data = self.buffer[:self.bytes_remaining]
                s += data
                self.buffer = self.buffer[self.bytes_remaining:]
                self.bytes_remaining -= len(data)
                assert self.bytes_remaining >= 0
                if self.bytes_remaining == 0:
                    # We reached the end of the chunk
                    self.bytes_remaining = None
        return s

    def flush(self):
        s = self.buffer
        self.buffer = ''
        return s

