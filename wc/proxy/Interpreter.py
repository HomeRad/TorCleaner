__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

# A Python expression interpreter for the proxy
from Connection import Connection

class Interpreter (Connection):
    def __init__ (self, socket, addr):
        self.addr = addr
        Connection.__init__(self, socket)
        self.write('>> ')

    def __repr__ (self):
        return '<interpreter>'

    def process_read (self):
        while 1:
            i = self.recv_buffer.find('\n')
            if i < 0: break

            line = self.read(i+1).strip()
            if line == '\004': # Ctrl-D (Unix EOF)
                self.handle_close()
                break
            
            self.write('%s => ' % line)
            try:
                self.write('%s\n' % repr(eval(line)))
            except:
                # TODO: add traceback information
                self.write('Error\n')
            self.write('>> ')

# TODO: make other modules accessible somehow
#import proxy4_dns, proxy4_web


