import tkinter as tk
import json
import random
import pathlib
import sys
import os
import logging
import time
import random as rand
from utils import utils

SYS_ARGS = sys.argv.copy()
SYS_ARGS.pop(0)
PATH = str(pathlib.Path(__file__).parent.absolute())
os.chdir(PATH)

logging.basicConfig(filename=os.path.join(PATH, 'logs', time.asctime().replace(' ', '_').replace(':', '-') + '-sublabel.txt'), format='%(levelname)s:%(message)s', level=logging.DEBUG)
#This sublabel.pyw originally provided very generously by u/basicmo!

def check_setting(name:str, default:bool=False) -> bool:
    default = False if default is None else default
    try:
        return int(settings.get(name)) == 1
    except:
        return default

CAP_OPACITY = 100
CAP_TIMER = 300
SUBLIMINAL_MOOD = True
MOOD_OFF = True
THEME = 'Original'

MOOD_ID = '0'
if len(SYS_ARGS) >= 1 and SYS_ARGS[0] != '0':
    MOOD_ID = SYS_ARGS[0].strip('-')

if MOOD_ID != '0':
    if os.path.exists(os.path.join(PATH, 'moods', f'{MOOD_ID}.json')):
        with open(os.path.join(PATH, 'moods', f'{MOOD_ID}.json')) as f:
            moodData = json.loads(f.read())
    elif os.path.exists(os.path.join(PATH, 'moods', 'unnamed', f'{MOOD_ID}.json')):
        with open(os.path.join(PATH, 'moods', 'unnamed', f'{MOOD_ID}.json')) as f:
            moodData = json.loads(f.read())

with open(os.path.join(PATH, 'config.cfg')) as cfg:
    settings = json.loads(cfg.read())
    CAP_OPACITY = int(settings['capPopOpacity'])
    CAP_TIMER = int(settings['capPopTimer'])
    SUBLIMINAL_MOOD = check_setting('capPopMood')
    MOOD_OFF = check_setting('toggleMoodSet')
    THEME = settings['themeType']

#background is one hex value off here, because it looks pretty ugly if they're different colours, so we keep them close so there is no visual difference
try:
    if THEME == 'Original':
        fore = '#000000'
        back = '#000001' if utils.is_windows() else '#f0f0f0'
        mainfont = 'Segoe UI'
    if THEME == 'Dark':
        fore = '#f9faff'
        back = '#f9fafe' if utils.is_windows() else '#282c34'
        mainfont = 'Segoe UI'
    if THEME == 'The One':
        fore = '#00ff41'
        back = '#00ff42' if utils.is_windows() else '#282c34'
        mainfont = 'Consolas'
    if THEME == 'Ransom':
        fore = '#ffffff'
        back = '#fffffe' if utils.is_windows() else '#841212'
        mainfont = 'Arial Bold'
    if THEME == 'Goth':
        fore = '#ba9aff'
        back = '#ba9afe' if utils.is_windows() else '#282c34'
        mainfont = 'Constantia'
    if THEME == 'Bimbo':
        fore = '#ff3aa3'
        back = '#ff3aa4' if utils.is_windows() else '#ffc5cd'
        mainfont = 'Constantia'
except Exception as e:
    logging.fatal(f'failed to load theme. {e}')
    fore = '#000000'
    back = '#000001' if utils.is_windows() else '#f0f0f0'
    mainfont = 'Segoe UI'

def display_subliminal_message():
    # Load subliminal messages from captions.json
    def load_subliminal_messages():
        try:
            with open(os.path.join(PATH, 'resource', 'captions.json'), "r") as file:
                l = json.load(file)
                if l.get("subliminal", []) and SUBLIMINAL_MOOD:
                    return l.get("subliminal", [])
                else:
                    if 'prefix' in l: del l['prefix']
                    if 'subtext' in l: del l['subtext']
                    if 'prefix_settings' in l: del l['prefix_settings']
                    if MOOD_ID != '0':
                        allsub = []
                        for key in l:
                            if key in moodData['captions']:
                                allsub.append(l[key])
                    else:
                        allsub = list(l.values())
                    flatlist = [i for sublist in allsub for i in sublist]
                    #logging.info(flatlist)
                    return flatlist
        except Exception as e:
            logging.fatal(f'failed to get sublabel prefixes. {e}')
            return []

    # Get a random subliminal message
    def get_random_subliminal():
        subliminal_messages = load_subliminal_messages()
        if subliminal_messages:
            return random.choice(subliminal_messages)
        else:
            return "No subliminal messages found."

    # Create the label
    label = tk.Label(fg=fore, bg=back)

    # Choose a screen for the window
    monitor_data = utils.monitor_areas()
    area = rand.choice(monitor_data)

    # Calculate the font size based on screen resolution
    f_size = min(area.width, area.height) // 10  # Adjust the scaling factor as needed

    # Configure the font
    font = (mainfont, f_size)

    # Configure the label with the calculated font size and wrap the text
    label.config(font=font, wraplength=area.width // 1.5)

    # Set the text to a random subliminal message
    label.config(text=get_random_subliminal())

    # Calculate the position to center the window
    x = area.x + (area.width - label.winfo_reqwidth()) // 2
    y = area.y + (area.height - label.winfo_reqheight()) // 2

    # Configure the window
    label.master.overrideredirect(True)
    label.master.geometry(f'+{x}+{y}')
    label.master.lift()
    label.master.wm_attributes('-topmost', True)
    if utils.is_windows():
        label.master.wm_attributes('-disabled', True)
        label.master.wm_attributes('-transparentcolor', back)
    label.winfo_toplevel().attributes('-alpha',CAP_OPACITY/100)
    label.pack()

    # Update the label's size
    label.update_idletasks()

    # Schedule the destruction of the window after 0.3 seconds
    label.master.after(CAP_TIMER, label.master.destroy)

    # Start the Tkinter event loop

    label.mainloop()

# Call the function to display the subliminal message
display_subliminal_message()
