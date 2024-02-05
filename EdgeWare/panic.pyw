import ctypes
import os
import pathlib
from pathlib import Path
from utils import utils

PATH = Path(__file__).parent

timeObjPath = os.path.join(PATH, 'hid_time.dat')

#checking timer
try:
    utils.show_file(timeObjPath)
except:
    ''
if os.path.exists(os.path.join(PATH, 'hid_time.dat')):
    utils.hide_file(timeObjPath)
    #sudoku if timer after hiding file again
    os.kill(os.getpid(), 9)
else:
    #continue if no timer
    utils.set_wallpaper(os.path.join(PATH, 'default_assets', 'default_win10.jpg'))

utils.panic_script()
