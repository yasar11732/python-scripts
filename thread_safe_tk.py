# Copy from effbot.org, for my own experiments

from tkinter import *

import threading # should use the threading module instead!
import queue

import os

class ThreadSafeConsole(Text):
    def __init__(self, master, **options):
        Text.__init__(self, master, **options)
        self.queue = queue.Queue()
        self.update_me()
    def write(self, line):
        self.queue.put(line)
    def clear(self):
        self.queue.put(None)
    def update_me(self):
        try:
            while 1:
                line = self.queue.get_nowait()
                if line is None:
                    self.delete(1.0, END)
                else:
                    self.insert(END, str(line))
                self.see(END)
                self.update_idletasks()
        except queue.Empty:
            pass
        self.after(100, self.update_me)

# this function pipes input to an widget
def pipeToWidget(input, widget):
    widget.clear()
    while 1:
        line = input.readline()
        if not line:
            break
        widget.write(line)

def funcThread(widget):
    input = os.popen('dir', 'r')
    pipeToWidget(input, widget)

# uber-main
root = Tk()
widget = ThreadSafeConsole(root)
widget.pack(side=TOP, expand=YES, fill=BOTH)
threading.Thread(target=funcThread, args=(widget,)).start()
threading.Thread(target=funcThread, args=(widget,)).start()
threading.Thread(target=funcThread, args=(widget,)).start()
threading.Thread(target=funcThread, args=(widget,)).start()
threading.Thread(target=funcThread, args=(widget,)).start()
root.mainloop()
