#!/usr/bin/env python 
import curses, traceback, string
import proxy4_base

stdscr = None

def color(col, text, bgcol=None):
    return text

def message(labelcolor, label, field1, field2, *args):
    "label can span field1 and 2 if the fields are empty"
    output = []
    label = label+':'
    labelwidth = 6
    if field1 is None:
        labelwidth = 11
        if field2 is None:
            labelwidth = 13
    output.append(string.ljust(label, labelwidth))
    if field1 is not None: output.append(string.rjust(str(field1), 5))
    output.append(' ')
    if field1 is not None or field2 is not None: output.append(string.ljust(str(field2), 2))
    for a in args:
        output.append(' ')
        output.append(str(a))
    output = string.join(output, '')
    screen.addstr(4, 1, (output+' '*78)[:78], curses.A_NORMAL)
    screen.refresh()
    
def main():
    proxy4_base.message = message
    proxy4_base.color = color
    import sys, StringIO
    sys.stdout = StringIO.StringIO()
    sys.stderr = StringIO.StringIO()
    
    global screen
    screen = stdscr.subwin(23, 79, 0, 0)
    screen.box()
    screen.hline(2, 1, curses.ACS_HLINE, 77)
    screen.refresh()
    
    import proxy4
    proxy4.mainloop()
    
if __name__=='__main__':
    try:
        # Initialize curses
        stdscr=curses.initscr()
        # Turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        curses.noecho()
        curses.cbreak()
        
        # In keypad mode, escape sequences for special keys
        # (like the cursor keys) will be interpreted and
        # a special value like curses.KEY_LEFT will be returned
        stdscr.keypad(1)
        main()                    # Enter the main loop
        # Set everything back to normal
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()                 # Terminate curses
    except (SystemExit, KeyboardInterrupt):
        # In event of exit, restore the terminal but don't print a traceback
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
    except:
        # In event of error, restore terminal to sane state.
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        traceback.print_exc()           # Print the exception
