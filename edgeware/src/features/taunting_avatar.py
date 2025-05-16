import tkinter as tk
from tkinter import Label, Toplevel, GROOVE
import random
import time
from PIL import Image, ImageTk
from pack import Pack
from paths import CustomAssets
from settings import Settings
from state import State
from features.theme import get_theme

class TauntingAvatar:
    def __init__(self, master,settings: Settings, pack: Pack, state: State) -> None:
        self.master = master
        self.pack = pack
        self.settings = settings
        self.theme = get_theme(settings)
        # Create a separate always-on-top window for the avatar

        self.avatar_window = Toplevel(master)
        self.avatar_window.overrideredirect(True) # Remove window decorations
        self.avatar_window.attributes('-topmost', True) # Always on top
        self.avatar_window.wm_attributes("-transparentcolor", "white") # Optional for non-rectangular window
        
        # Position at bottom corner of screen
        screen_width = self.avatar_window.winfo_screenwidth()
        screen_height = self.avatar_window.winfo_screenheight()
        self.avatar_window.geometry(f"150x75+{screen_width-170}+{screen_height-170}")
        
        # Load avatar images (you would replace with your own images)
        # self.avatar_images = self.load_avatar_images()
        # For simplicity, we'll use a colored label for now
        self.image = ImageTk.PhotoImage(file=CustomAssets.theme_demo())
        self.avatar = Label(self.avatar_window,
            image=self.image)
        
        self.avatar.pack(padx=10, pady=10)
        
        # Speech bubble
        self.bubble_window = Toplevel(master)
        self.bubble_window.overrideredirect(True)
        self.bubble_window.attributes('-topmost', True)
        self.bubble_window.withdraw() # Initially hidden
        
        self.bubble_frame = tk.Frame(self.bubble_window, bg= self.theme.bg, bd=2, relief=tk.RAISED)
        self.bubble_frame.pack(padx=5, pady=5)
        
        self.bubble_text = Label(self.bubble_frame, text="", 
                                font=self.theme.font, bg=self.theme.bg, 
                                wraplength=200, padx=10, pady=10)
        self.bubble_text.pack()
        
        # List of taunts
        self.taunts = [
            "Having computer problems? What a coincidence!",
            "Oops, did you need that file? Too late now!",
            "Your antivirus can't save you from me!",
            "Try clicking faster, that always helps!",
            "Have you tried turning it off and... oh wait, I won't let you!",
            "Is your computer running slow? Let me help make it slower!",
            "Alt+F4 might work... just kidding, I disabled that!",
            "I'm just getting started, you ain't seen nothing yet!",
            "Thanks for running me! Your computer is now my playground!",
            "Looking for Task Manager? Good luck with that!"
        ]
        
        # Start taunting behavior
        self.start_taunting()
        
        # Make avatar react when clicked
        self.avatar.bind("<Button-1>", self.on_avatar_click)
        
        # Optional: Make avatar dodgeable
        self.avatar_window.bind("<Enter>", self.dodge_mouse)

    def load_avatar_images(self):
        # In a real implementation, you would load multiple avatar images here
        # For different expressions/states
        pass
    
    def show_taunt(self, text):
        # Position bubble near avatar
        avatar_x = self.avatar_window.winfo_x()
        avatar_y = self.avatar_window.winfo_y()
        self.bubble_window.geometry(f"+{avatar_x-220}+{avatar_y-50}")
        
        # Update and show the bubble
        self.bubble_text.config(text=text)
        self.bubble_window.deiconify()
        
        # Schedule bubble to disappear
        self.master.after(4000, self.bubble_window.withdraw)
    
    def start_taunting(self):
        # Show random taunt every 8-20 seconds
        taunt = random.choice(self.taunts)
        #taunt = self.Pack.random_caption()
        self.show_taunt(taunt)
        
        # Schedule next taunt
        next_taunt_time = random.randint(8000, 20000) # 8-20 seconds
        self.master.after(next_taunt_time, self.start_taunting)
    
    def on_avatar_click(self, event):
        # React when clicked
        self.show_taunt("Hey! Don't touch me! I'm busy destroying your computer!")
    
    def dodge_mouse(self, event):
        # Occasionally dodge the mouse when the user tries to hover over the avatar
        if random.random() < 0.7: # 70% chance to dodge
            screen_width = self.avatar_window.winfo_screenwidth() - 170
            screen_height = self.avatar_window.winfo_screenheight() - 170
            new_x = random.randint(0, screen_width)
            new_y = random.randint(0, screen_height)
            self.avatar_window.geometry(f"150x75+{new_x}+{new_y}")
            self.show_taunt(self.pack.random_caption())
