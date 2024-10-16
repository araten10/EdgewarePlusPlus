""" tk_ToolTip_class101.py
gives a Tkinter widget a tooltip as the mouse is above the widget
tested with Python27 and Python34  by  vegaseat  09sep2014
www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter

Modified to include a delay time by Victor Zaccardo, 25mar16
"""

import tkinter as tk

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    instances = []
    def __init__(self, widget, text="widget info", bg = None, fg = None, bc = None):
        self.waittime = 1000     #miliseconds
        self.wraplength = 500   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
        if bg:
            self.background = bg
        else:
            self.background = "#ffffff"
        if fg:
            self.foreground = fg
        else:
            self.foreground = "#000000"
        if bc:
            self.bordercolor = bc
        else:
            self.bordercolor = "#000000"
        self.__class__.instances.append(self)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 30
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        self.borderframe = tk.Frame(self.tw, background = self.bordercolor)
        label = tk.Label(self.borderframe, text=self.text, justify="left",
                       background= self.background, wraplength = self.wraplength,
                       foreground= self.foreground)
        self.borderframe.pack()
        label.pack(padx=1, pady=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()
