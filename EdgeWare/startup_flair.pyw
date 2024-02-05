import time
import os
import threading as thread
import pathlib
import sys
import tkinter as tk
from tkinter import Tk, Frame, Label, RAISED, messagebox
from PIL import Image, ImageTk, ImageFilter
from itertools import cycle
from pathlib import Path

PATH = Path(__file__).parent
os.chdir(PATH)
scalar = 0.6

SYS_ARGS = sys.argv.copy()
SYS_ARGS.pop(0)

#animated gif mode currently unused as I dont know how to bugfix this atm, but I want to work on other things
#keeping it in because it would be nice to fix at some point
class GifLabel(tk.Label):
    def load(self, resized_width:int, resized_height:int, delay:int=75):
        self.image = Image.open(os.path.join(PATH, 'resouce', 'loading_splash.gif'))
        self.configure(background='black')
        self.frames:list[ImageTk.PhotoImage] = []
        if 'duration' in self.image.info:
            self.delay = int(self.image.info['duration'])
        else:
            self.delay = delay

        if self.delay < delay:
            self.delay = delay

        try:
            for i in range(0, self.image.n_frames):
                hold_image = self.image.resize((resized_width, resized_height), Image.BOX)
                self.frames.append(ImageTk.PhotoImage(hold_image.copy()))
                self.image.seek(i)
        except Exception as e:
            print(f'{e}')
            print(f'Done register frames. ({len(self.frames)})')
        self.frames_ = cycle(self.frames)

    def next_frame(self):
        if self.frames_:
            self.config(image=next(self.frames_))
            self.after(self.delay, self.next_frame)

def doAnimation():
    root = Tk()
    root.configure(bg='black')
    root.frame = Frame(root, borderwidth=2, relief=RAISED)
    root.wm_attributes('-topmost', 1)
    root.overrideredirect(1)

    animated_gif = False
    if len(SYS_ARGS) >= 1 and SYS_ARGS[0] == '-custom':
        if os.path.exists(os.path.join(PATH, 'resouce', 'loading_splash.png')):
            img_ = Image.open(os.path.join(PATH, 'resource', 'loading_splash.png'))
        elif os.path.exists(os.path.join(PATH, 'resouce', 'loading_splash.gif')):
            img_ = Image.open(os.path.join(PATH, 'resource', 'loading_splash.gif'))
            #if img_.n_frames > 1:
                #animated_gif = True
        elif os.path.exists(os.path.join(PATH, 'resouce', 'loading_splash.jpg')):
            img_ = Image.open(os.path.join(PATH, 'resource', 'loading_splash.jpg'))
        elif os.path.exists(os.path.join(PATH, 'resouce', 'loading_splash.jpeg')):
            img_ = Image.open(os.path.join(PATH, 'resource', 'loading_splash.jpeg'))
        elif os.path.exists(os.path.join(PATH, 'resouce', 'loading_splash.bmp')):
            img_ = Image.open(os.path.join(PATH, 'resource', 'loading_splash.bmp'))
    else:
        img_ = Image.open(os.path.join(PATH, 'default_assets', 'loading_splash.png'))
    if len(SYS_ARGS) >= 2 and SYS_ARGS[1] == '-lanczos' or len(SYS_ARGS) == 1 and SYS_ARGS[0] == '-lanczos':
        img = ImageTk.PhotoImage(img_.resize((int(img_.width * scalar), int(img_.height * scalar)), resample=Image.LANCZOS))
    else:
        img = ImageTk.PhotoImage(img_.resize((int(img_.width * scalar), int(img_.height * scalar)), resample=Image.ANTIALIAS))

    root.geometry('{}x{}+{}+{}'.format(img.width(), img.height(), int((root.winfo_screenwidth() - img.width()) / 2), int((root.winfo_screenheight() - img.height()) / 2)))
    if animated_gif:
        try:
            lbl = GifLabel(root)
            lbl.load(resized_width = img.width, resized_height = img.height)
        except Exception as e:
            messagebox.showwarning('Animated gif couldn\'t play!', f'{e}')
    else:
        lbl = Label(root, image=img)
    lbl.pack()
    root.attributes('-alpha', 0)
    thread.Thread(target=lambda: anim(root)).start()
    root.mainloop()
    #if animated_gif:
        #lbl.next_frame()

def anim(root):
    alpha = 0.0
    step = 0.01
    for i in range(int(1 / step)):
        root.attributes('-alpha', alpha)
        alpha += step
        time.sleep(step)
    time.sleep(2)
    for i in range(int(1 / (2*step))):
        root.attributes('-alpha', alpha)
        alpha -= 2*step
        time.sleep(step/4)

    os.kill(os.getpid(), 9)

doAnimation()
