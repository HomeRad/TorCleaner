# -*- coding: iso-8859-1 -*-
"""experimental Python expression interpreter for the proxy"""

import wc.proxy.Connection

class Interpreter (wc.proxy.Connection.Connection):
    """accept python commands on a telnet-like prompt and send them
       to a running proxy instance"""

    def __init__ (self, sock, addr):
        """start interpreter on given address"""
        self.addr = addr
        super(Interpreter, self).__init__(sock=sock)
        self.write('>> ')

    def __repr__ (self):
        """return class name"""
        return '<interpreter>'

    def process_read (self):
        """read and send commands given at the displayed prompt until
           Ctrl-D is pressed"""
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
