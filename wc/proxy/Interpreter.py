# A Python expression interpreter for the proxy
from string import find,strip
from Connection import Connection

class Interpreter(Connection):
    def __init__(self, socket, addr):
        self.addr = addr
        Connection.__init__(self, socket)
        self.write('>> ')

    def __repr__(self):
        return '<interpreter>'

    def process_read(self):
        while 1:
            i = find(self.recv_buffer, '\n')
            if i < 0: break

            line = strip(self.read(i+1))
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


