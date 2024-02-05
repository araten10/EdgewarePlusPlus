import os
import sys
import pathlib
import json
import random as rand
import tkinter as tk
from tkinter import messagebox, font
from tkinter import *
from utils import utils

SYS_ARGS = sys.argv.copy()
SYS_ARGS.pop(0)


hasData = False
textData = {}
maxMistakes = 3
submission_text = 'I Submit <3'
command_text    = 'Type for me, slut~'
moodData = {}
THEME = 'Original'
PATH = str(pathlib.Path(__file__).parent.absolute())
os.chdir(PATH)


with open(os.path.join(PATH, 'config.cfg')) as settings:
    jsondata = json.loads(settings.read())
    maxMistakes = int(jsondata['promptMistakes'])
    THEME = jsondata['themeType']

MOOD_ID = '0'
if len(SYS_ARGS) >= 1 and SYS_ARGS[0] != '0':
    MOOD_ID = SYS_ARGS[0].strip('-')

if MOOD_ID != '0':
    if os.path.exists(os.path.join(PATH, 'moods', f'{MOOD_ID}.json')):
        with open(os.path.join(PATH, 'moods', f'{MOOD_ID}.json'), 'r') as f:
            moodData = json.loads(f.read())
    elif os.path.exists(os.path.join(PATH, 'moods', 'unnamed', f'{MOOD_ID}.json')):
        with open(os.path.join(PATH, 'moods', 'unnamed', f'{MOOD_ID}.json'), 'r') as f:
            moodData = json.loads(f.read())

if os.path.exists(os.path.join(PATH, 'resource', 'prompt.json')):
    hasData = True
    with open(os.path.join(PATH, 'resource', 'prompt.json'), 'r') as f:
        textData = json.loads(f.read())
        try:
            submission_text = textData['subtext']
        except:
            print('no subtext')
        try:
            command_text = textData['commandtext']
        except:
            print('no commandtext')

if not hasData:
    messagebox.showerror('Prompt Error', 'Resource folder contains no "prompt.json". Either set prompt freq to 0 or add "prompt.json" to resource folder.')

def unborderedWindow():
    if not hasData:
        exit()
    root = Tk()

    fore = '#000000'
    back = '#f0f0f0'
    textb = '#ffffff'
    textf = '#000000'
    mainfont = font.nametofont('TkDefaultFont')

    if THEME == 'Dark':
        fore = '#f9faff'
        back = '#282c34'
        textb = '#1b1d23'
        textf = '#f9faff'
    if THEME == 'The One':
        fore = '#00ff41'
        back = '#282c34'
        textb = '#1b1d23'
        textf = '#00ff41'
        mainfont.configure(family='Consolas', size=8)
    if THEME == 'Ransom':
        fore = '#ffffff'
        back = '#841212'
        textb = '#ffffff'
        textf = '#000000'
        mainfont.configure(family='Arial Bold')
    if THEME == 'Goth':
        fore = '#ba9aff'
        back = '#282c34'
        textb = '#db7cf2'
        textf = '#6a309d'
        mainfont.configure(family='Constantia')
    if THEME == 'Bimbo':
        fore = '#ff3aa3'
        back = '#ffc5cd'
        textb = '#ffc5cd'
        textf = '#f43df2'
        mainfont.configure(family='Constantia')

    root.configure(background=back)
    label = tk.Label(root, text='\n' + command_text + '\n', bg=back, fg=fore)
    label.pack()

    txt = buildText()

    monitor_data = utils.monitor_areas()
    area = rand.choice(monitor_data) # TODO: Only on primary monitor?
    wid = area.width / 4
    hgt = area.height / 2

    textLabel = Label(root, text=txt, wraplength=wid, bg=back, fg=fore)
    textLabel.pack()

    root.geometry('%dx%d+%d+%d' % (wid, hgt, area.x + 2*wid - wid / 2, area.y + hgt - hgt / 2))

    root.frame = Frame(root, borderwidth=2, relief=RAISED, bg=back)
    root.frame.pack_propagate(True)
    root.wm_attributes('-topmost', 1)
    utils.set_borderless(root)

    inputBox = Text(root, bg=textb, fg=textf)
    inputBox.pack()

    subButton = Button(root, text=submission_text, command=lambda: checkTotal(root, txt, inputBox.get(1.0, "end-1c")), bg=back, fg=fore,
                        activebackground=back, activeforeground=fore)
    subButton.place(x=wid - 5 - subButton.winfo_reqwidth(), y=hgt - 5 - subButton.winfo_reqheight())
    root.mainloop()

def buildText():
    moodList = textData['moods']
    freqList = textData['freqList']
    if MOOD_ID != '0':
        for i, mood in enumerate(moodList):
            if mood not in moodData['prompts']:
                del moodList[i-1]
                del freqList[i-1]
    outputPhraseCount = rand.randint(int(textData['minLen']), int(textData['maxLen']))
    strVar = ''
    selection = rand.choices(moodList, freqList, k=1)
    for i in range(outputPhraseCount):
        strVar += textData[selection[0]][rand.randrange(0, len(textData[selection[0]]))] + ' '
    #strVar += MOOD_ID
    return strVar.strip()

def checkTotal(root, a, b):
    if checkText(a, b):
        root.destroy()

def checkText(a, b):
    mistakes = 0
    if len(a) != len(b):
        mistakes += abs(len(a)-len(b))
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            mistakes += 1
    return mistakes <= maxMistakes

try:
    unborderedWindow()
except Exception as e:
    messagebox.showerror('Prompt Error', 'Could not create prompt window.\n[' + str(e) + ']')
