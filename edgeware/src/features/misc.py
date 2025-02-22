import json
import logging
import random
import subprocess
import time
import webbrowser
from collections.abc import Callable
from threading import Thread
from tkinter import Tk

import pystray
import utils
from desktop_notifier.common import Attachment, Icon
from desktop_notifier.sync import DesktopNotifierSync
from pack import Pack
from panic import panic
from paths import CustomAssets, Data, Process
from PIL import Image
from pygame import mixer
from pypresence import Presence
from roll import roll
from settings import Settings
from state import State


def play_audio(pack: Pack) -> None:
    # Pygame will not stop additional sounds from being played when the max is
    # reached, so we need to check if there are empty channels
    audio = pack.random_audio()
    if audio and mixer.find_channel():
        sound = mixer.Sound(str(audio))
        # TODO POTENTIAL SETTINGS: Volume, fadein, fadeout, separating music from sounds
        # https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound
        sound.play()


def open_web(pack: Pack) -> None:
    web = pack.random_web()
    if web:
        webbrowser.open(web)


def display_notification(settings: Settings, pack: Pack) -> None:
    notification = pack.random_notification()
    if not notification:
        return

    image = pack.random_image()
    notifier = DesktopNotifierSync(app_name="Edgeware++", app_icon=Icon(pack.icon))
    notifier.send(
        title=pack.info.name,
        message=notification,
        attachment=Attachment(image) if roll(settings.notification_image_chance) and image else None,
    )


def make_tray_icon(root: Tk, settings: Settings, pack: Pack, state: State, hibernate_activity: Callable[[], None]) -> None:
    menu = [pystray.MenuItem("Panic", lambda: panic(root, settings, state))]
    if settings.hibernate_mode:

        def skip_hibernate() -> None:
            if state.hibernate_active:
                return

            root.after_cancel(state.hibernate_id)
            hibernate_activity()

        menu.append(pystray.MenuItem("Skip to Hibernate", skip_hibernate))

    icon = pystray.Icon("Edgeware++", Image.open(pack.icon), "Edgeware++", menu)
    Thread(target=icon.run, daemon=True).start()


def make_desktop_icons(settings: Settings) -> None:
    if settings.desktop_icons:
        utils.make_shortcut("Edgeware++", Process.MAIN, CustomAssets.icon())
        utils.make_shortcut("Edgeware++ Config", Process.CONFIG, CustomAssets.config_icon())
        utils.make_shortcut("Edgeware++ Panic", Process.PANIC, CustomAssets.panic_icon())


def handle_booru_download(settings: Settings, state: State) -> None:
    if not settings.booru_download:
        return

    root = f"https://{settings.booru_name}.booru.org"
    url = f"{root}/index.php?page=post&s=list&tags={settings.booru_tags}"

    with open(Data.GALLERY_DL_CONFIG, "w") as f:
        json.dump({"extractor": {"gelbooru_v01": {settings.booru_name: {"root": root}}}}, f)

    args = f'gallery-dl -D "{settings.download_path}" -c "{Data.GALLERY_DL_CONFIG}" "{url}"'
    state.gallery_dl_process = subprocess.Popen(args, shell=True)


def handle_wallpaper(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    def rotate(previous: str = None) -> None:
        if settings.hibernate_fix_wallpaper and not state.hibernate_active and state.popup_number == 0:
            return

        wallpapers = settings.wallpapers.copy()
        if previous:
            wallpapers.remove(previous)

        wallpaper = random.choice(wallpapers)
        utils.set_wallpaper(pack.paths.root / wallpaper)

        t = settings.wallpaper_timer
        v = settings.wallpaper_variance
        root.after(t + random.randint(-v, v), lambda: rotate(wallpaper))

    if settings.corruption_mode and settings.corruption_wallpaper:
        return

    if settings.rotate_wallpaper and len(settings.wallpapers) > 1:
        rotate()
    else:
        utils.set_wallpaper(pack.wallpaper)


def handle_discord(root: Tk, settings: Settings, pack: Pack) -> None:
    if not settings.show_on_discord:
        return

    try:
        presence = Presence("820204081410736148")
        presence.connect()
        presence.update(state=pack.discord.text, large_image=pack.discord.image, start=int(time.time()))
    except Exception as e:
        logging.warning(f"Setting Discord presence failed. Reason: {e}")


def handle_timer_mode(root: Tk, settings: Settings, state: State) -> None:
    def timer_over() -> None:
        state.timer_active = False

    if settings.timer_mode:
        state.timer_active = True
        root.after(settings.timer_time, timer_over)


def mitosis_popup(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    # Imports done here to avoid circular imports
    from features.image_popup import ImagePopup
    from features.video_popup import VideoPopup

    try:
        popup = random.choices([ImagePopup, VideoPopup], [settings.image_chance, settings.video_chance], k=1)[0]
    except ValueError:
        popup = ImagePopup  # Exception thrown when both chances are 0
    popup(root, settings, pack, state)


def handle_mitosis_mode(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    if settings.mitosis_mode:
        # Import done here to avoid circular imports

        def observer() -> None:
            if state.popup_number == 0:
                mitosis_popup(root, settings, pack, state)

        state._popup_number.attach(observer)
        mitosis_popup(root, settings, pack, state)
