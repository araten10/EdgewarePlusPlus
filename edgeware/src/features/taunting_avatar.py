import tkinter as tk
from tkinter import Label, Toplevel, GROOVE, ttk
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
        self.avatar_window.wm_attributes("-transparentcolor", self.theme.bg) # Optional for non-rectangular window
        
        # Position at bottom corner of screen
        screen_width = self.avatar_window.winfo_screenwidth()
        screen_height = self.avatar_window.winfo_screenheight()
        self.avatar_window.geometry(f"150x75+{screen_width-170}+{screen_height-170}")
        
        # Load avatar images (you would replace with your own images)
        # self.avatar_images = self.load_avatar_images()
        # For simplicity, we'll use a colored label for now
        self.image = ImageTk.PhotoImage(file=CustomAssets.theme_demo())
        self.avatar = Label(self.avatar_window,
            image=self.image, bg= self.theme.bg)
        
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
        
        # Progress bars management
        self.active_bars = []  # Keep track of all progress bars
        self.max_bars = 5  # Maximum number of progress bars at once
        
        # Funny/absurd operations that might appear on progress bars
        self.operations = [
        "Reading your 'dirty laundry' browser history...",
        "Unarchiving your 'deep web' stash, hehe...",
        "Caching your 'favorite' GIFs in RAM, ready to roll!",
        "Examining your 'private' folder structure, neat freak!",
        "Generating 'just for you' video recommendations, naughty naughty!",
        "Livening up your desktop with 'inspiring' wallpapers, let's decorate!",
        "Encrypting your 'naughty' Google searches, your secret's safe with me!",
        "Preloading 'high definition' galleries, get ready to goon!",
        "Suggesting 'mind-expanding' fetish tags, ready to explore?",
        "Installing 'immersive' surround sound for your 'private' sessions, crank it up!",
        "Caching 'tempting' pop-up ads, ready to break your resolve!",
        "Generating 'kinky' browser extension suggestions, let's spice things up!",
        "Backing up your 'incredible' browsing history to the cloud, your digital diary! ♫",
        "Optimizing your 'personal' file sharing settings, time to connect!",
        "Reviewing your 'personal' folder size, impressive collection!"
]
        # Start taunting behavior
        self.start_taunting()
        # Start spawning progress bars
        self.start_spawning_progress_bars()
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
        taunt = self.pack.random_caption
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
            taunt = self.pack.random_caption()
            self.show_taunt(taunt)

     # Progress bar methods
    def start_spawning_progress_bars(self):
        # Schedule the first progress bar
        delay = random.randint(3000, 8000)  # 3-8 seconds
        self.master.after(delay, self.spawn_progress_bar)
    
    def spawn_progress_bar(self):
        # Limit the number of active progress bars
        if len(self.active_bars) < self.max_bars:
            # Create a new window for the progress bar
            bar_window = Toplevel(self.master)
            bar_window.title("Corrupting your computer")
            
            # Make it always on top with a reasonable size
            bar_window.attributes('-topmost', True)
            width = random.randint(300, 500)
            height = random.randint(100, 150)
            
            # Position randomly on screen
            x_pos = random.randint(50, self.master.winfo_screenwidth() - width - 50)
            y_pos = random.randint(50, self.master.winfo_screenheight() - height - 50)
            bar_window.geometry(f"{width}x{height}+{x_pos}+{y_pos}")

            # Cannot be closed normally
            bar_window.protocol("WM_DELETE_WINDOW", lambda: None)
            bar_window.resizable(False, False)
            
            # Select a random operation
            operation = random.choice(self.operations)
            
            # Create a label with the operation text
            label = tk.Label(bar_window, text=operation, font=self.theme.font)
            label.pack(pady=(20, 10))
            
            # Create a frame for the progress bar
            progress_frame = tk.Frame(bar_window, bg="black", bd=2)
            progress_frame.pack(pady=10, padx=20, fill="x")
            
            # Create custom progress bar (instead of ttk.Progressbar)
            progress_canvas = tk.Canvas(
                progress_frame, 
                height=20, 
                width=width-44, 
                bg="black", 
                highlightthickness=0
            )
            progress_canvas.pack()
            
            progress_rect = progress_canvas.create_rectangle(
                0, 0, 0, 20, 
                fill=self.theme.bg,  # Bright red
                width=0,
                tags="progress"
            )
            
            # Store reference with custom attributes
            self.active_bars.append({
                "window": bar_window,
                "canvas": progress_canvas,
                "rect_id": progress_rect,
                "width": width-44,
                "speed": random.uniform(0.5, 2.0),
                "complete": False,
                "value": 0  # Current progress (0-100)
            })

            
            # Taunt about the new progress bar
            progress_taunts = [
                "Another naughty process you'll never want to end!",
                "Look what I've just begun for your viewing pleasure!",
                "This might run forever, like your late-night marathons!",
                "Try halting this one, but we both know you won't!"
            ]
            self.show_taunt(random.choice(progress_taunts))
            
            # Start advancing the progress
            self.advance_progress(len(self.active_bars) - 1)
        
        # Schedule next progress bar
        next_delay = random.randint(5000, 15000)  # 5-15 seconds
        self.master.after(next_delay, self.spawn_progress_bar)
    
    def advance_progress(self, bar_index):
        # Check if the bar index is valid
        if bar_index >= len(self.active_bars):
            return  # Bar no longer exists
        
        try:    
            bar_data = self.active_bars[bar_index]
            
            # Safety check - ensure window still exists
            if not bar_data["window"].winfo_exists():
                # Window was destroyed externally, clean up
                self.active_bars.pop(bar_index)
                return
                
            # Check if already complete
            if bar_data["complete"]:
                return
            
            # Get current progress value
            if "canvas" in bar_data:  # Custom canvas-based progress
                current_value = bar_data["value"]
            else:  # Standard ttk progress bar
                current_value = bar_data["progress"]["value"]
            
            # Random increment between 1-5
            increment = random.randint(1, 5) * bar_data["speed"]
            new_value = min(current_value + increment, 100)
            
            # Update the progress bar
            if "canvas" in bar_data:  # Custom canvas-based progress
                bar_data["value"] = new_value
                max_width = bar_data["width"]
                new_width = (new_value / 100) * max_width
                bar_data["canvas"].coords(bar_data["rect_id"], 0, 0, new_width, 20)
            else:  # Standard ttk progress bar
                bar_data["progress"]["value"] = new_value
            
            # Add maximum time limit to prevent hanging
            bar_data["time_alive"] = bar_data.get("time_alive", 0) + 1
            
            # Force completion if it's been alive too long (300 = ~30 seconds with typical delays)
            if bar_data["time_alive"] > 300:
                new_value = 100
                if "canvas" in bar_data:
                    bar_data["value"] = 100
                    max_width = bar_data["width"]
                    bar_data["canvas"].coords(bar_data["rect_id"], 0, 0, max_width, 20)
                else:
                    bar_data["progress"]["value"] = 100
                    
            # If not complete, schedule next advancement
            if new_value < 100:
                # Update slightly faster/slower at different points
                if 20 <= new_value <= 40:
                    # Slow down in the middle
                    delay = random.randint(100, 300)
                elif 80 <= new_value <= 95:
                    # Slow down near completion
                    delay = random.randint(200, 500)
                else:
                    # Normal speed
                    delay = random.randint(50, 150)
                    
                # Schedule next update with a backup timeout
                update_id = self.master.after(delay, lambda: self.advance_progress(bar_index))
                bar_data["update_id"] = update_id
            else:
                # Mark as complete
                bar_data["complete"] = True
                # Close after delay
                self.master.after(1000, lambda: self.complete_progress(bar_index))
                
        except Exception as e:
            # If anything goes wrong, clean up this bar to prevent hanging
            print(f"Error advancing progress bar: {e}")
            try:
                if bar_index < len(self.active_bars):
                    # Try to destroy the window if it exists
                    try:
                        self.active_bars[bar_index]["window"].destroy()
                    except:
                        pass
                    # Remove from active bars
                    self.active_bars.pop(bar_index)
            except:
                pass
    
    def complete_progress(self, bar_index):
        """Handle completion of a progress bar"""
        if bar_index >= len(self.active_bars):
            return
            
        bar_data = self.active_bars[bar_index]
        
        
        # Close window and remove from active bars
        bar_data["window"].destroy()
        self.active_bars.pop(bar_index)

    def cleanup_stuck_bars(self):
        current_time = time.time()
        
        # Keep track of indices to remove (in reverse order to avoid shifting issues)
        to_remove = []
        
        # Check each progress bar
        for i in range(len(self.active_bars)-1, -1, -1):
            try:
                bar_data = self.active_bars[i]
                
                # Check if window still exists
                if not bar_data["window"].winfo_exists():
                    to_remove.append(i)
                    continue
                    
                # Check if it's been stuck at the same value for too long
                if not hasattr(bar_data, "last_check_time"):
                    bar_data["last_check_time"] = current_time
                    bar_data["last_value"] = bar_data.get("value", 0)
                    continue
                    
                # If value hasn't changed in 10 seconds, consider it stuck
                if current_time - bar_data["last_check_time"] > 10:
                    if "value" in bar_data and bar_data["value"] == bar_data["last_value"]:
                        # It's stuck, force completion
                        print("Found stuck bar, forcing completion")
                        self.complete_progress(i)
                        continue
                    
                    # Update the last check values
                    bar_data["last_check_time"] = current_time
                    bar_data["last_value"] = bar_data.get("value", 0)
                    
            except Exception as e:
                print(f"Error checking progress bar {i}: {e}")
                to_remove.append(i)
        
        # Schedule next cleanup
        self.master.after(5000, self.cleanup_stuck_bars)    
        
