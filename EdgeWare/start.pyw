import json
import logging
import multiprocessing
import os
import random as rand
import shutil
import subprocess
import sys
import threading as thread
import time
import traceback
import webbrowser
import zipfile
from pathlib import Path
from tkinter import messagebox

import playsound as ps
from utils import utils
from utils.booru import BooruDownloader, download_web_resources
from utils.fill import LIVE_FILL_THREADS, fill_drive, replace_images
from utils.paths import Data, Defaults, Process, Resource
from utils.settings import Settings
from utils.tray import TrayHandler

PATH = Path(__file__).parent
os.chdir(PATH)

utils.init_logging("ew_start", "start")

SYS_ARGS = sys.argv.copy()
SYS_ARGS.pop(0)
logging.info(f"args: {SYS_ARGS}")

# load settings, if first run open options, then reload options from file
settings = Settings()
if not settings["is_configed"] == 1:
    logging.info("running config for first setup, is_configed flag is false.")
    subprocess.run([sys.executable, Process.CONFIG])
    logging.info("reloading settings")
    settings = Settings()

PLAYING_AUDIO = False  # audio thread flag
REPLACING_LIVE = False  # replace thread flag
HAS_PROMPTS = False  # can use prompts flag
MITOSIS_LIVE = False  # flag for if the mitosis mode popup has been spawned

# default data for generating working default asset resource folder
DEFAULT_WEB = '{"urls":["https://duckduckgo.com/"], "args":["?q=why+are+you+gay"]}'
DEFAULT_PROMPT = '{"moods":["no moods"], "freqList":[100], "minLen":1, "maxLen":1, "no moods":["no prompts"]}'
DEFAULT_DISCORD = "Playing with myself~"

AUDIO_NUMBER = 0
VIDEO_NUMBER = 0

MOOD_ID = "0"
if not settings.MOOD_OFF:
    try:
        if os.path.isfile(Resource.INFO):
            info_dict = ""
            with open(Resource.INFO) as r:
                info_dict = json.loads(r.read())
                if "id" in info_dict:
                    MOOD_ID = info_dict["id"] if info_dict["id"] else "0"
        if MOOD_ID == "0":
            im = str(len(os.listdir(Resource.IMAGE))) if os.path.exists(Resource.IMAGE) else "0"
            au = str(len(os.listdir(Resource.AUDIO))) if os.path.exists(Resource.AUDIO) else "0"
            vi = str(len(os.listdir(Resource.VIDEO))) if os.path.exists(Resource.VIDEO) else "0"
            wa = "w" if os.path.isfile(Resource.WALLPAPER) else "x"
            sp = "s" if Resource.SPLASH else "x"
            di = "d" if os.path.isfile(Resource.DISCORD) else "x"
            ic = "i" if os.path.isfile(Resource.ICON) else "x"
            co = "c" if os.path.isfile(Resource.CORRUPTION) else "x"
            MOOD_ID = im + au + vi + wa + sp + di + ic + co
    except Exception as e:
        messagebox.showerror("Launch Error", "Could not launch Edgeware due to setting mood ID issues.\n[" + str(e) + "]")
        logging.fatal(f"failed to set mood id.\n\tReason:{e}")
        os.kill(os.getpid(), 9)
    logging.info(f"mood id: {MOOD_ID}")

hiber_wait = thread.Event()
wallpaper_wait = thread.Event()
running_hibernate = thread.Event()
pump_scare_audio = thread.Event()
corruption_wait = thread.Event()

# start init portion, check resources, config, etc.
try:
    if not os.path.exists(Resource.ROOT):
        logging.warning("no resource folder found")
        pth = "pth-default_ignore"
        # selecting first zip found in script folder
        for obj in os.listdir(PATH):
            try:
                if obj.split(".")[-1].lower() == "zip":
                    logging.info(f"found zip file {obj}")
                    pth = os.path.join(PATH, obj)
                    break
            except Exception:
                print(f"{obj} is not a zip file.")
        # if found zip unpack
        if not pth == "pth-default_ignore":
            with zipfile.ZipFile(pth, "r") as obj:
                logging.info("extracting resources from zip")
                obj.extractall(Resource.ROOT)
        else:
            # if no zip found, use default resources
            logging.warning("no zip file found, generating resource folder from default assets.")
            for obj in [Resource.ROOT, Resource.AUDIO, Resource.IMAGE, Resource.VIDEO]:
                os.mkdir(obj)
            shutil.copyfile(Defaults.WALLPAPER, Resource.WALLPAPER)
            shutil.copyfile(Defaults.IMAGE, Resource.IMAGE / "img0.png", follow_symlinks=True)
            if not os.path.exists(Resource.DISCORD):
                with open(Resource.DISCORD, "w") as f:
                    f.write(DEFAULT_DISCORD)
            if not os.path.exists(Resource.PROMPT):
                with open(Resource.PROMPT, "w") as f:
                    f.write(DEFAULT_PROMPT)
            if not os.path.exists(Resource.WEB):
                with open(Resource.WEB, "w") as f:
                    f.write(DEFAULT_WEB)
except Exception as e:
    messagebox.showerror("Launch Error", "Could not launch Edgeware due to resource zip unpacking issues.\n[" + str(e) + "]")
    logging.fatal(f"failed to unpack resource zip or read default resources.\n\tReason:{e}")
    os.kill(os.getpid(), 9)

corruption_data = {}
if settings.CORRUPTION_MODE:
    try:
        # read and save corruption data
        with open(Resource.CORRUPTION, "r") as f:
            corruption_data = json.loads(f.read())
            # print(corruption_data["moods"]["1"]["add"])
        # writing corruption file if it doesn't exist/wiping it if the mode isn't on launch
        if not os.path.exists(Data.ROOT):
            os.mkdir(Data.ROOT)
        # the launches will reset when the user specifies in the config, or a new pack is loaded
        if not os.path.exists(Data.CORRUPTION_LAUNCHES):
            with open(Data.CORRUPTION_LAUNCHES, "w") as f:
                f.write("1")
        elif settings.CORRUPTION_TRIGGER == "Launch":
            with open(Data.CORRUPTION_LAUNCHES, "r+") as f:
                i = int(f.readline())
                f.seek(0)
                f.write(str(i + 1))
                f.truncate()
        with open(Data.CORRUPTION_POPUPS, "w") as f:
            f.write("0")
        with open(Data.CORRUPTION_LEVEL, "w") as f:
            if not settings.CORRUPTION_PURITY:
                # starts at 1 and not 0 for simplicity's sake
                f.write("1")
            else:
                # purity mode starts at max value and works backwards
                f.write(str(len(corruption_data["moods"].keys())))

    except Exception as e:
        messagebox.showerror("Launch Error", "Could not launch Edgeware due to corruption initialization failing.\n[" + str(e) + "]")
        logging.fatal(f"failed to initialize corruption properly.\n\tReason: {e}")
        os.kill(os.getpid(), 9)

HAS_PROMPTS = False
WEB_JSON_FOUND = False
if os.path.exists(Resource.PROMPT):
    logging.info("found prompt.json")
    HAS_PROMPTS = True
if os.path.exists(Resource.WEB):
    logging.info("found web.json")
    WEB_JSON_FOUND = True

WEB_DICT = {}
if os.path.exists(Resource.WEB):
    with open(Resource.WEB, "r") as web_f:
        WEB_DICT = json.loads(web_f.read())

# checking presence of resources
try:
    HAS_IMAGES = len(os.listdir(Resource.IMAGE)) > 0
    logging.info("image resources found")
except Exception as e:
    logging.warning(f"no image resource folder found\n\tReason: {e}")
    print("no image folder found")
    HAS_IMAGES = False

VIDEOS = []
try:
    for vid in os.listdir(Resource.VIDEO):
        VIDEOS.append(Resource.VIDEO / vid)
    logging.info("video resources found")
except Exception as e:
    logging.warning(f"no video resource folder found\n\tReason: {e}")
    print("no video folder found")

AUDIO = []
MOOD_AUDIO = []
try:
    HAS_AUDIO = os.path.exists(Resource.AUDIO)
    for aud in os.listdir(Resource.AUDIO):
        AUDIO.append(Resource.AUDIO / aud)
    logging.info("audio resources found")
except Exception as e:
    logging.warning(f"no audio resource folder found\n\tReason: {e}")
    print("no audio folder found")

CAPTIONS = os.path.exists(Resource.CAPTIONS)

HAS_WEB = WEB_JSON_FOUND and len(WEB_DICT["urls"]) > 0
# end of checking resource presence

# set discord status if enabled
if settings.SHOW_ON_DISCORD:
    try:
        subprocess.Popen([sys.executable, Process.DISCORD])
    except Exception as e:
        logging.warning(f"failed to start discord status background task\n\tReason: {e}")
        print("failed to start discord status")

# making missing desktop shortcuts
if settings.DESKTOP_ICONS:
    if not utils.does_desktop_shortcut_exist("Edgeware"):
        utils.make_shortcut("Edgeware", Process.START, Defaults.ICON)
    if not utils.does_desktop_shortcut_exist("Config"):
        utils.make_shortcut("Config", Process.CONFIG, Defaults.CONFIG_ICON)
    if not utils.does_desktop_shortcut_exist("Panic"):
        utils.make_shortcut("Panic", Process.PANIC, Defaults.PANIC_ICON)

if settings.LOADING_FLAIR and (__name__ == "__main__"):
    logging.info("started loading flair")
    if Resource.SPLASH:
        if settings.LANCZOS_MODE:
            logging.info("using lanczos for loading flair")
            subprocess.run([sys.executable, Process.STARTUP, "-custom", "-lanczos"])
        else:
            subprocess.run([sys.executable, Process.STARTUP, "-custom"])
    else:
        if settings.LANCZOS_MODE:
            logging.info("using lanczos for loading flair")
            subprocess.run([sys.executable, Process.STARTUP, "-lanczos"])
        else:
            subprocess.run([sys.executable, Process.STARTUP])


# checks if user is in corruption mode, then sets wallpaper accordingly
def wallpaper_check(else_path: Path | str):
    try:
        if settings.CORRUPTION_MODE:
            if not settings.CORRUPTION_WALLCYCLE:
                with open(Data.CORRUPTION_LEVEL, "r") as f:
                    corruption_level = f.read()
                try:
                    wp_path = Resource.ROOT / str(corruption_data["wallpapers"][corruption_level])
                except Exception:
                    print("wallpaper does not exist for this corruption level")
                    return
            else:
                wp_path = Resource.ROOT / str(corruption_data["wallpapers"]["default"])
        else:
            wp_path = else_path

        print(f"current wallpaper path: {wp_path}")
        utils.set_wallpaper(wp_path)
    except Exception as e:
        print(f"Error changing wallpaper. {e}")
        logging.warning(f"failed to change wallpaper.\n\tReason: {e}")


# set wallpaper if not specific modes that set it later
if not settings.HIBERNATE_MODE and not settings.CORRUPTION_MODE:
    logging.info("set user wallpaper to default wallpaper.png")
    wallpaper_check(Resource.WALLPAPER)


# selects url to be opened in new tab by web browser
def url_select(arg: int):
    logging.info(f"selected url {arg}")
    return WEB_DICT["urls"][arg] + WEB_DICT["args"][arg].split(",")[rand.randrange(len(WEB_DICT["args"][arg].split(",")))]

START_TIME = time.monotonic()

# main function, probably can do more with this but oh well i'm an idiot so
def main():
    logging.info("entered main function")
    # set up tray icon
    tray = TrayHandler(hiber_wait)

    # if tray icon breaks again this is why
    # idk why it works 50% of the time when it works and sometimes just stops working
    thread.Thread(target=tray.move_to_tray, daemon=True).start()

    # timer handling, start if there's a time left file
    if os.path.exists(Data.HID_TIME):
        thread.Thread(target=do_timer).start()

    # max value handling creation/cleaning
    if not os.path.exists(Data.ROOT):
        os.mkdir(Data.ROOT)
    try:
        with open(Data.MAX_VIDEOS, "w") as f:
            f.write("0")
        with open(Data.MAX_SUBLIMINALS, "w") as f:
            f.write("0")
        with open(Data.HIBERNATE, "w") as f:
            f.write("0")
        if not settings.MOOD_OFF:
            with open(Data.MEDIA_IMAGES, "w") as f:
                f.write("0")
            with open(Data.MEDIA_VIDEO, "w") as f:
                f.write("0")
    except Exception as e:
        logging.warning(f"failed to clean or create data files\n\tReason: {e}")
        print("failed to clean or create data files")

    # initial corruption setup and mood calibration
    corrupted_list = []
    if settings.CORRUPTION_MODE:
        thread.Thread(target=lambda: corruption_timer(len(corruption_data["moods"].keys()))).start()
        time.sleep(0.1)
        corrupted_list = update_corruption()
        wallpaper_check(Resource.WALLPAPER)
    update_media(corrupted_list)

    # do downloading for booru stuff
    if settings.get("downloadEnabled") == 1:
        booru_downloader: BooruDownloader = BooruDownloader(settings.get("booruName"), settings.get("tagList").split(">"))

        logging.info("start booru_method thread")
        if settings.get("downloadMode") == "First Page":
            thread.Thread(target=lambda: booru_downloader.download(min_score=int(settings.get("booruMinScore"))), daemon=True).start()
        elif settings.get("downloadMode") == "Random Page":
            thread.Thread(target=lambda: booru_downloader.download_random(min_score=int(settings.get("booruMinScore"))), daemon=True).start()
        else:
            thread.Thread(target=lambda: booru_downloader.download_all(min_score=int(settings.get("booruMinScore"))), daemon=True).start()

    # do downloading from web resource folder
    if settings.USE_WEB_RESOURCE:
        logging.info("start download_web_resources thread")
        thread.Thread(target=download_web_resources).start()

    # start thread for wallpaper timer
    if settings.ROTATE_WALLPAPER:
        logging.info("start rotate_wallpapers thread")
        thread.Thread(target=rotate_wallpapers).start()

    # run annoyance thread or do hibernate mode
    if settings.HIBERNATE_MODE:
        logging.info("starting in hibernate mode")
        with open(Data.CORRUPTION_LEVEL, "r") as f:
            tracked_level = int(f.read())
        trigger_thread = thread.Thread(target=check_wallpaper_status)
        if settings.FIX_WALLPAPER:
            trigger_thread.start()
        while True:
            hiber_wait.clear()
            wait_time = rand.randint(settings.HIBERNATE_MIN, settings.HIBERNATE_MAX)
            if settings.CORRUPTION_MODE:
                with open(Data.CORRUPTION_LEVEL, "r") as f:
                    current_level = int(f.read())
                if tracked_level != current_level:
                    corrupted_list = []
                    corrupted_list = update_corruption()
                    update_media(corrupted_list)
                    tracked_level = current_level
            if settings.HIBERNATE_TRUTH == "Chaos":
                try:
                    global HIBERNATE_TYPE
                    HIBERNATE_TYPE = rand.choice(["Original", "Spaced", "Glitch", "Ramp", "Pump-Scare"])
                    with open(Data.CHAOS_TYPE, "w") as f:
                        f.write(HIBERNATE_TYPE)
                    print(f"hibernate type is chaos, and has switched to {HIBERNATE_TYPE}")
                except Exception as e:
                    logging.warning(f"failed to successfully run chaos hibernate.\n\tReason: {e}")
            hiber_wait.wait(float(wait_time))
            running_hibernate.clear()
            if settings.HIBERNATE_TYPE != "Pump-Scare":
                wallpaper_check(Resource.WALLPAPER)
                wallpaper_wait.clear()
            if settings.HIBERNATE_TYPE == "Original":
                try:
                    print(f"running original hibernate. number of popups estimated between {int(settings.WAKEUP_ACTIVITY / 2)} and {settings.WAKEUP_ACTIVITY}.")
                    for i in range(0, rand.randint(int(settings.WAKEUP_ACTIVITY / 2), settings.WAKEUP_ACTIVITY)):
                        roll_for_initiative()
                except Exception as e:
                    logging.warning(f"failed to successfully run {settings.HIBERNATE_TYPE} hibernate.\n\tReason: {e}")
            if settings.HIBERNATE_TYPE == "Spaced":
                try:
                    end_time = time.monotonic() + float(settings.HIBERNATE_LENGTH)
                    print(f"running spaced hibernate. current time is {time.monotonic()}, end time is {end_time}")
                    while time.monotonic() < end_time:
                        roll_for_initiative()
                        time.sleep(float(settings.DELAY) / 1000.0)
                except Exception as e:
                    logging.warning(f"failed to successfully run {settings.HIBERNATE_TYPE} hibernate.\n\tReason: {e}")
            if settings.HIBERNATE_TYPE == "Glitch":
                try:
                    glitch_sleep = settings.HIBERNATE_LENGTH / settings.WAKEUP_ACTIVITY
                    total_time = time.monotonic()
                    end_time = time.monotonic() + float(settings.HIBERNATE_LENGTH)
                    print(
                        f"running glitch hibernate. the end time is {end_time} with {settings.WAKEUP_ACTIVITY} popups, total time is {settings.HIBERNATE_LENGTH} and glitch_sleep median is {glitch_sleep}"
                    )
                    for i in range(0, settings.WAKEUP_ACTIVITY):
                        if end_time <= time.monotonic():
                            break
                        rgl = rand.randint(1, 4)
                        rt = rand.randint(2, 4)
                        if rgl == 1 and (end_time - total_time) > glitch_sleep:
                            time.sleep(float(glitch_sleep))
                            total_time = total_time + glitch_sleep
                        if rgl == 2 and (end_time - total_time) > (glitch_sleep / rt):
                            time.sleep(float(glitch_sleep / rt))
                            total_time = total_time + (glitch_sleep / rt)
                        if rgl == 3 and (end_time - total_time) > (glitch_sleep * rt):
                            time.sleep(float(glitch_sleep * rt))
                            total_time = total_time + (glitch_sleep * rt)
                        logging.info(f"time {end_time - total_time}, rgl {rgl}, rt {rt}")
                        roll_for_initiative()
                    if end_time > time.monotonic():
                        time.sleep(float(end_time - time.monotonic()))
                    roll_for_initiative()
                except Exception as e:
                    logging.warning(f"failed to successfully run {settings.HIBERNATE_TYPE} hibernate.\n\tReason: {e}")
            if settings.HIBERNATE_TYPE == "Ramp":
                try:
                    print(
                        f"hibernate type is ramp. ramping up speed for {settings.HIBERNATE_LENGTH}, max speed is {settings.DELAY*0.9}, and popups at max speed is {settings.WAKEUP_ACTIVITY}"
                    )
                    end_time = time.monotonic() + float(settings.HIBERNATE_LENGTH)
                    x = settings.HIBERNATE_LENGTH / 4
                    accelerate = 1
                    while True:
                        if (time.monotonic() > end_time) and ((settings.DELAY / 1000) + 0.1 > ramp_sleep):
                            break
                        if ((end_time - time.monotonic()) / settings.HIBERNATE_LENGTH) > 0.5:
                            accelerate = accelerate * 1.10
                        else:
                            accelerate = accelerate * 1.05
                        x = x / accelerate
                        ramp_sleep = (settings.DELAY / 1000) + x
                        # logging.info(f'rampsleep {ramp_sleep} accelerate {accelerate}, {((end_time - time.monotonic()) / settings.HIBERNATE_LENGTH)} time left {end_time - time.monotonic()}')
                        roll_for_initiative()
                        time.sleep(float(ramp_sleep))
                    for i in range(0, settings.WAKEUP_ACTIVITY):
                        roll_for_initiative()
                        time.sleep(float(settings.DELAY * 0.9) / 1000.0)
                except Exception as e:
                    logging.warning(f"failed to successfully run {settings.HIBERNATE_TYPE} hibernate.\n\tReason: {e}")
            if settings.HIBERNATE_TYPE == "Pump-Scare":
                try:
                    print("hibernate type is pump-scare.")
                    roll_for_initiative()
                except Exception as e:
                    logging.warning(f"failed to successfully run {settings.HIBERNATE_TYPE} hibernate.\n\tReason: {e}")
            time.sleep(0.5)
            running_hibernate.set()

    else:
        logging.info("starting annoyance loop")
        annoyance()


def check_wallpaper_status():
    with open(Data.HIBERNATE, "r") as f:
        while True:
            running_hibernate.wait()
            print("hibernate processing is over, waiting for popups to close")
            while True:
                if not running_hibernate.is_set():
                    break
                if not wallpaper_wait.is_set():
                    f.seek(0)
                    i = int(f.readline())
                    if i < 1:
                        wallpaper_wait.set()
                        print("hibernate popups are all dead")
                        utils.set_wallpaper(Defaults.PANIC_WALLPAPER)
                        break


# just checking %chance of doing annoyance options
def do_roll(mod: float) -> bool:
    if mod >= 100:
        return True

    if mod <= 0:
        return False

    return mod > (rand.random() * 100)


# does annoyance things; while running, does a check of randint against the frequency of each option
#   if pass, do thing, if fail, don't do thing. pretty simple stuff right here.
#   only exception is for fill drive and replace images:
#       fill: will only happen if fill is on AND until there are 8 threads running simultaneously
#             as threads become available they will be restarted.
#       replace: will only happen one single time in the run of the application, but checks ALL folders
def annoyance():
    global MITOSIS_LIVE
    corr_chance = 0
    if settings.CORRUPTION_MODE:
        with open(Data.CORRUPTION_LEVEL, "r") as f:
            tracked_level = int(f.read())
        if settings.CORRUPTION_TRIGGER == "Launch":
            corr_chance = corruption_percent()
            if corr_chance > 1.0:
                #remove leading digit if corruption level isn't maxxed
                #this only happens for launches because launches don't reset to 0 when corruption levels up
                if settings.CORRUPTION_PURITY and tracked_level != 1:
                    corr_chance = corr_chance % 1
                elif not settings.CORRUPTION_PURITY and tracked_level != len(corruption_data["moods"].keys()):
                    corr_chance = corr_chance % 1
                else:
                    #if it's maxxed, just keep it at 1
                    corr_chance = 1
    while True:
        if settings.CORRUPTION_MODE:
            with open(Data.CORRUPTION_LEVEL, "r") as f:
                current_level = int(f.read())
            if tracked_level != current_level:
                corrupted_list = []
                corrupted_list = update_corruption()
                update_media(corrupted_list)
                wallpaper_check(Resource.WALLPAPER)
                tracked_level = current_level
        roll_for_initiative(corr_chance)
        if not MITOSIS_LIVE and (settings.MITOSIS_MODE or settings.LOWKEY_MODE) and HAS_IMAGES:
            subprocess.Popen([sys.executable, Process.POPUP]) if settings.MOOD_OFF else subprocess.Popen([sys.executable, Process.POPUP, f"-{MOOD_ID}"])
            MITOSIS_LIVE = True
        if settings.FILL_MODE and LIVE_FILL_THREADS < settings.MAX_FILL_THREADS:
            thread.Thread(target=fill_drive).start()
        if settings.REPLACE_MODE and not REPLACING_LIVE:
            thread.Thread(target=replace_images).start()
        time.sleep(float(settings.DELAY) / 1000.0)


# independently attempt to do all active settings with probability equal to their freq value
def roll_for_initiative(corr_chance: float = 0.0): #TODO: Remove default value when corruption gets implemented
    if settings.CORRUPTION_MODE and settings.CORRUPTION_TRIGGER != "Launch":
        corr_chance = corruption_percent()
        if corr_chance > 1.0:
            corr_chance = 1
    #print(f"corruption chance: {corr_chance}")
    if settings.HIBERNATE_TYPE == "Pump-Scare" and settings.HIBERNATE_MODE:
        if HAS_IMAGES:
            if HAS_AUDIO:
                if settings.AUDIO_CAP:
                    if AUDIO_NUMBER < settings.AUDIO_MAX:
                        try:
                            thread.Thread(target=play_audio).start()
                            pump_scare_audio.wait()
                        except Exception as e:
                            messagebox.showerror("Audio Error", "Failed to play audio.\n[" + str(e) + "]")
                            logging.critical(f"failed to play audio\n\tReason: {e}")
                else:
                    try:
                        thread.Thread(target=play_audio).start()
                        pump_scare_audio.wait()
                    except Exception as e:
                        messagebox.showerror("Audio Error", "Failed to play audio.\n[" + str(e) + "]")
                        logging.critical(f"failed to play audio\n\tReason: {e}")
            try:
                wallpaper_check(Resource.WALLPAPER)
                wallpaper_wait.clear()
                subprocess.Popen([sys.executable, Process.POPUP]) if settings.MOOD_OFF else subprocess.Popen([sys.executable, Process.POPUP, f"-{MOOD_ID}"])
            except Exception as e:
                messagebox.showerror("Popup Error", "Failed to start popup.\n[" + str(e) + "]")
                logging.critical(f"failed to start popup.pyw\n\tReason: {e}")
    else:
        # these variables make the experience "more consistent" by stopping further popup spawns if enough spawns are reached
        curr_pop_num = 0
        max_pop_num = 1 if settings.SINGLE_MODE else 999
        if do_roll(settings.WEB_CHANCE) and HAS_WEB and curr_pop_num < max_pop_num:
            try:
                url = url_select(rand.randrange(len(WEB_DICT["urls"]))) if HAS_WEB else None
                webbrowser.open_new(url)
                curr_pop_num += 1
            except Exception as e:
                messagebox.showerror("Web Error", "Failed to open website.\n[" + str(e) + "]")
                logging.critical(f"failed to open website {url}\n\tReason: {e}")
        if do_roll(settings.VIDEO_CHANCE) and VIDEOS and curr_pop_num < max_pop_num:
            global VIDEO_NUMBER
            if settings.VIDEO_CAP:
                with open(Data.MAX_VIDEOS, "r") as f:
                    VIDEO_NUMBER = int(f.readline())
                if VIDEO_NUMBER < settings.VIDEO_MAX:
                    try:
                        if settings.VLC_MODE:
                            thread.Thread(
                                target=lambda: subprocess.call([sys.executable, Process.POPUP, "-video", "-vlc"], shell=False)
                            ).start() if settings.MOOD_OFF else thread.Thread(
                                target=lambda: subprocess.call([sys.executable, Process.POPUP, f"-{MOOD_ID}", "-video", "-vlc"], shell=False)
                            ).start()
                        else:
                            thread.Thread(
                                target=lambda: subprocess.call([sys.executable, Process.POPUP, "-video"], shell=False)
                            ).start() if settings.MOOD_OFF else thread.Thread(
                                target=lambda: subprocess.call([sys.executable, Process.POPUP, f"-{MOOD_ID}", "-video"], shell=False)
                            ).start()
                        with open(Data.MAX_VIDEOS, "w") as f:
                            f.write(str(VIDEO_NUMBER + 1))
                        curr_pop_num += 1
                    except Exception as e:
                        messagebox.showerror("Popup Error", "Failed to start popup.\n[" + str(e) + "]")
                        logging.critical(f"failed to start video popup.pyw\n\tReason: {e}")
            else:
                try:
                    if settings.VLC_MODE:
                        thread.Thread(
                            target=lambda: subprocess.call([sys.executable, Process.POPUP, "-video", "-vlc"], shell=False)
                        ).start() if settings.MOOD_OFF else thread.Thread(
                            target=lambda: subprocess.call([sys.executable, Process.POPUP, f"-{MOOD_ID}", "-video", "-vlc"], shell=False)
                        ).start()
                    else:
                        thread.Thread(
                            target=lambda: subprocess.call([sys.executable, Process.POPUP, "-video"], shell=False)
                        ).start() if settings.MOOD_OFF else thread.Thread(
                            target=lambda: subprocess.call([sys.executable, Process.POPUP, f"-{MOOD_ID}", "-video"], shell=False)
                        ).start()
                    curr_pop_num += 1
                except Exception as e:
                    messagebox.showerror("Popup Error", "Failed to start popup.\n[" + str(e) + "]")
                    logging.critical(f"failed to start video popup.pyw\n\tReason: {e}")
        if do_roll(settings.AUDIO_CHANCE) and AUDIO and curr_pop_num < max_pop_num:
            if settings.AUDIO_CAP:
                if AUDIO_NUMBER < settings.AUDIO_MAX:
                    try:
                        thread.Thread(target=play_audio).start()
                        curr_pop_num += 1
                    except Exception as e:
                        messagebox.showerror("Audio Error", "Failed to play audio.\n[" + str(e) + "]")
                        logging.critical(f"failed to play audio\n\tReason: {e}")
            else:
                try:
                    thread.Thread(target=play_audio).start()
                    curr_pop_num += 1
                except Exception as e:
                    messagebox.showerror("Audio Error", "Failed to play audio.\n[" + str(e) + "]")
                    logging.critical(f"failed to play audio\n\tReason: {e}")
        if do_roll(settings.CAP_POP_CHANCE) and CAPTIONS and curr_pop_num < max_pop_num:
            try:
                subprocess.call([sys.executable, Process.SUBLABEL, f"-{MOOD_ID}"]) if not settings.MOOD_OFF else subprocess.call(
                    [sys.executable, Process.SUBLABEL]
                )
                curr_pop_num += 1
            except Exception as e:
                messagebox.showerror("Caption Popup Error", "Could not start caption popup.\n[" + str(e) + "]")
                logging.critical(f"failed to start sublabel.pyw\n\tReason: {e}")

        if do_roll(settings.PROMPT_CHANCE) and HAS_PROMPTS and curr_pop_num < max_pop_num:
            try:
                subprocess.call([sys.executable, Process.PROMPT, f"-{MOOD_ID}"]) if not settings.MOOD_OFF else subprocess.call([sys.executable, Process.PROMPT])
                curr_pop_num += 1
            except Exception as e:
                messagebox.showerror("Prompt Error", "Could not start prompt.\n[" + str(e) + "]")
                logging.critical(f"failed to start prompt.pyw\n\tReason: {e}")
        if (not (settings.MITOSIS_MODE or settings.LOWKEY_MODE)) and do_roll(settings.POPUP_CHANCE) and HAS_IMAGES and curr_pop_num < max_pop_num:
            try:
                subprocess.Popen([sys.executable, Process.POPUP]) if settings.MOOD_OFF else subprocess.Popen([sys.executable, Process.POPUP, f"-{MOOD_ID}"])
                curr_pop_num += 1
            except Exception as e:
                messagebox.showerror("Popup Error", "Failed to start popup.\n[" + str(e) + "]")
                logging.critical(f"failed to start popup.pyw\n\tReason: {e}")


def rotate_wallpapers():
    prv = "default"
    base = int(settings["wallpaperTimer"])
    vari = int(settings["wallpaperVariance"])
    while len(settings["wallpaperDat"].keys()) > 1:
        time.sleep(base + rand.randint(-vari, vari))
        selected_wallpaper = list(settings["wallpaperDat"].keys())[rand.randrange(0, len(settings["wallpaperDat"].keys()))]
        while selected_wallpaper == prv:
            selected_wallpaper = list(settings["wallpaperDat"].keys())[rand.randrange(0, len(settings["wallpaperDat"].keys()))]
        utils.set_wallpaper(Resource.ROOT / settings["wallpaperDat"][selected_wallpaper])
        prv = selected_wallpaper


def do_timer():
    utils.show_file(Data.HID_TIME)
    with open(Data.HID_TIME, "r") as file:
        time_remaining = int(file.readline())

    while time_remaining > 0:
        print("time left: ", str(time_remaining), "secs", sep="")
        time.sleep(1)
        time_remaining -= 1
        utils.show_file(Data.HID_TIME)
        with open(Data.HID_TIME, "w") as file:
            file.write(str(time_remaining))
        utils.hide_file(Data.HID_TIME)

    try:
        utils.show_file(Data.PASS_HASH)
        utils.show_file(Data.HID_TIME)
        os.remove(Data.PASS_HASH)
        os.remove(Data.HID_TIME)
        subprocess.Popen([sys.executable, Process.PANIC])
    except Exception:
        subprocess.Popen([sys.executable, Process.PANIC])


def audio_helper(mood_audio: list):
    try:
        if settings.MOOD_OFF:
            ps.playsound(str(AUDIO[rand.randrange(len(AUDIO))]))
        else:
            ps.playsound(str(mood_audio[rand.randrange(len(mood_audio))]))
    except Exception as e:
        print(f"error managing audio. {e}")


# if audio is not playing, selects and plays random audio file from /aud/ folder
def play_audio():
    global PLAYING_AUDIO
    global AUDIO_NUMBER
    if not AUDIO:
        return
    logging.info("starting audio playback")
    PLAYING_AUDIO = True
    AUDIO_NUMBER += 1
    try:
        if settings.HIBERNATE_TYPE == "Pump-Scare" and settings.HIBERNATE_MODE:
            p = multiprocessing.Process(target=audio_helper, args=(MOOD_AUDIO,))
            p.start()
            if settings.PUMP_SCARE_OFFSET != 0:
                time.sleep(settings.PUMP_SCARE_OFFSET)
            pump_scare_audio.set()
            time.sleep(2.6)
            pump_scare_audio.clear()
            p.terminate()
        else:
            if not settings.MOOD_OFF and os.path.exists(Resource.MEDIA):
                ps.playsound(str(MOOD_AUDIO[rand.randrange(len(MOOD_AUDIO))]))
            else:
                ps.playsound(str(AUDIO[rand.randrange(len(AUDIO))]))
    except Exception as e:
        logging.warning(f"Could not play sound. {e}")
    # winsound.PlaySound(AUDIO[rand.randrange(len(AUDIO))], winsound.SND_)
    PLAYING_AUDIO = False
    AUDIO_NUMBER -= 1
    logging.info("finished audio playback")


def update_corruption():
    try:
        corrupt_list = []
        with open(Resource.CORRUPTION, "r") as f:
            corruption_data = json.loads(f.read())
        with open(Data.CORRUPTION_LEVEL, "r") as f:
            corruption_level = int(f.read())
        if not settings.CORRUPTION_PURITY:
            i = 1
            while i <= corruption_level:
                for mood in corruption_data["moods"][str(i)]["remove"]:
                    if mood in corrupt_list:
                        corrupt_list.remove(mood)
                for mood in corruption_data["moods"][str(i)]["add"]:
                    if mood not in corrupt_list:
                        corrupt_list.append(mood)
                i += 1
        else:
            # generate initial list, as if corruption has run through every level
            i = 1
            while i <= len(corruption_data["moods"].keys()):
                for mood in corruption_data["moods"][str(i)]["remove"]:
                    if mood in corrupt_list:
                        corrupt_list.remove(mood)
                for mood in corruption_data["moods"][str(i)]["add"]:
                    if mood not in corrupt_list:
                        corrupt_list.append(mood)
                i += 1
            # actually run purity mode normally
            i = len(corruption_data["moods"].keys())
            while i >= corruption_level:
                for mood in corruption_data["moods"][str(i)]["remove"]:
                    if mood in corrupt_list:
                        corrupt_list.remove(mood)
                for mood in corruption_data["moods"][str(i)]["add"]:
                    if mood not in corrupt_list:
                        corrupt_list.append(mood)
                if i < len(corruption_data["moods"].keys()):
                    for mood in corruption_data["moods"][str(i + 1)]["remove"]:
                        if mood not in corrupt_list:
                            corrupt_list.append(mood)
                    for mood in corruption_data["moods"][str(i + 1)]["add"]:
                        if mood in corrupt_list:
                            corrupt_list.remove(mood)
                i -= 1
        print(f"current corruption list: {corrupt_list}")
        return corrupt_list
    except Exception as e:
        logging.warning(f"failed to update corruption.\n\tReason: {e}")
        print(f"failed to update corruption. {e}")
        traceback.print_exc()


def update_media(corrlist: list):
    # handle media list, doing it here instead of popup to take the load off of popups
    if os.path.exists(Resource.MEDIA) and not settings.MOOD_OFF:
        if os.path.exists(Data.MOODS / f"{MOOD_ID}.json"):
            with open(Data.MOODS / f"{MOOD_ID}.json", "r") as f:
                mood_data = json.loads(f.read())
                # print(f'mood_data {mood_data}')
        elif os.path.exists(Data.UNNAMED_MOODS / f"{MOOD_ID}.json"):
            with open(Data.UNNAMED_MOODS / f"{MOOD_ID}.json", "r") as f:
                mood_data = json.loads(f.read())
                # print(f'mood_data {mood_data}')
        with open(Resource.MEDIA, "r") as f:
            media_data = json.loads(f.read())
            # print(f'media_data {media_data}')
        if settings.CORRUPTION_MODE and corrlist:
            try:
                corrupted_media = media_data
                for mood in list(media_data):
                    if mood not in corrlist:
                        corrupted_media.pop(mood)
                # print(f'corrupted_media {corrupted_media}')
            except Exception as e:
                logging.warning(f"failed to compare corruption list to mood list.\n\tReason:{e}")
                print(f"failed to compare corruption. {e}")
        try:
            global MOOD_AUDIO
            MOOD_AUDIO = []
            for mood in list(media_data):
                if mood not in mood_data["media"]:
                    media_data.pop(mood)

            raw_list = list(media_data.values())
            merged_list = []
            mood_video = []
            for sub in raw_list:
                for i in sub:
                    if i in os.listdir(Resource.AUDIO):
                        MOOD_AUDIO.append(Resource.AUDIO / i)
                        # print(f'{i}')
                    elif i in os.listdir(Resource.VIDEO):
                        mood_video.append(i)
                    else:
                        merged_list.append(i)
            print(merged_list)
            with open(Data.MEDIA_IMAGES, "w") as f:
                f.write(json.dumps(merged_list))
            with open(Data.MEDIA_VIDEO, "w") as f:
                f.write(json.dumps(mood_video))
        except Exception as e:
            logging.warning(f"failed to load media_data properly.\n\tReason: {e}")
            print(f"failed to load media_data. {e}")


def corruption_timer(total_levels: int):
    with open(Data.CORRUPTION_LEVEL, "r") as f:
        corruption_level = int(f.read())
    while True:
        if settings.CORRUPTION_TRIGGER == "Timed":
            corruption_wait.wait(timeout=settings.CORRUPTION_TIME)
        if settings.CORRUPTION_TRIGGER == "Popup":
            while True:
                with open(Data.CORRUPTION_POPUPS, "r+") as f:
                    if int(f.read()) >= settings.CORRUPTION_POPUPS:
                        f.seek(0)
                        f.write("0")
                        f.truncate()
                        break
        if settings.CORRUPTION_TRIGGER == "Launch":
            with open(Data.CORRUPTION_LAUNCHES, "r") as f:
                corruption_level = total_levels if settings.CORRUPTION_PURITY else 1
                curr_launches = int(f.read())
                for i in range(1, total_levels):
                    if curr_launches >= (settings.CORRUPTION_LAUNCHES * i):
                        corruption_level = corruption_level - 1 if settings.CORRUPTION_PURITY else corruption_level + 1
                        # print(f'corruption level change! It is now {corruption_level}. Current launches is {curr_launches}')
            with open(Data.CORRUPTION_LEVEL, "w") as f:
                f.write(str(corruption_level))
                # print(f'corruption written, now at level {corruption_level}')
            break
        if not settings.CORRUPTION_PURITY:
            with open(Data.CORRUPTION_LEVEL, "r+") as f:
                corruption_level = int(f.read())
                if corruption_level >= total_levels:
                    break
                f.seek(0)
                f.write(str(corruption_level + 1))
                f.truncate()
                print(f"corruption now at level {corruption_level+1}")
        else:
            with open(Data.CORRUPTION_LEVEL, "r+") as f:
                corruption_level = int(f.read())
                if corruption_level <= 1:
                    break
                f.seek(0)
                f.write(str(corruption_level - 1))
                f.truncate()
                print(f"corruption now at level {corruption_level-1}")

def corruption_percent():
    if settings.CORRUPTION_TRIGGER == "Timed":
        with open(Data.CORRUPTION_LEVEL, "r") as f:
            corruption_level = int(f.read())
        if settings.CORRUPTION_PURITY:
            corruption_completed_time = (len(corruption_data["moods"].keys()) - corruption_level) * settings.CORRUPTION_TIME
        else:
            corruption_completed_time = (corruption_level - 1) * settings.CORRUPTION_TIME
        #remove already elapsed time before dividing
        corruption_chance = (time.monotonic() - (START_TIME + corruption_completed_time)) / settings.CORRUPTION_TIME
    if settings.CORRUPTION_TRIGGER == "Popup":
        with open(Data.CORRUPTION_POPUPS, "r") as f:
            corruption_chance = int(f.read()) / settings.CORRUPTION_POPUPS
    if settings.CORRUPTION_TRIGGER == "Launch":
        with open(Data.CORRUPTION_LAUNCHES, "r") as f:
            curr_launches = int(f.read())
        corruption_chance = curr_launches / settings.CORRUPTION_LAUNCHES
    return corruption_chance

if __name__ == "__main__":
    main()
