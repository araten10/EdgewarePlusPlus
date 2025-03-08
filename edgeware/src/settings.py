import ast
import json
import logging
import shutil
import subprocess
import sys

from paths import DEFAULT_PACK_PATH, Assets, Data, Process


def first_launch_configure() -> None:
    if not Data.CONFIG.is_file():
        subprocess.run([sys.executable, Process.CONFIG, "--first-launch-configure"])


def load_config() -> dict:
    if not Data.CONFIG.is_file():
        Data.ROOT.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Assets.DEFAULT_CONFIG, Data.CONFIG)

    default_config = load_default_config()
    with open(Data.CONFIG, "r+") as f:
        config = json.loads(f.read())

        new_keys = False
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
                new_keys = True

        if new_keys:
            f.seek(0)
            f.write(json.dumps(config))
            f.truncate()

    return config


def load_default_config() -> dict:
    with open(Assets.DEFAULT_CONFIG) as f:
        default_config = json.loads(f.read())

    return default_config


class Settings:
    def __init__(self):
        self.config = load_config()
        self.load_settings()
        logging.info(f"Config loaded: {self.config}")

    def load_settings(self) -> None:
        # Impacts other settings
        lowkey_mode = bool(self.config["lkToggle"])

        # General
        self.theme = self.config["themeType"]
        self.startup_splash = bool(self.config["showLoadingFlair"])
        self.desktop_icons = bool(self.config["desktopIcons"])
        self.global_panic_key = self.config["globalPanicButton"]
        self.panic_key = self.config["panicButton"]
        self.pack_path = Data.PACKS / self.config["packPath"] if self.config["packPath"] else DEFAULT_PACK_PATH

        # Booru downloader
        self.booru_download = bool(self.config["downloadEnabled"])
        self.booru_name = self.config["booruName"]
        # self.min_score = int(self.config["booruMinScore"])  # TODO: Can this be used with gallery-dl?
        self.booru_tags = self.config["tagList"].replace(">", "+")  # TODO: Store in a better way
        self.download_path = Data.DOWNLOAD / f"{self.booru_name}-{self.booru_tags}"

        # Popups
        self.delay = int(self.config["delay"])  # Milliseconds
        self.image_chance = int(self.config["popupMod"])  # 0 to 100
        self.opacity = int(self.config["lkScaling"]) / 100  # Float between 0 and 1
        self.timeout_enabled = bool(self.config["timeoutPopups"]) or lowkey_mode
        self.timeout = int(self.config["popupTimeout"]) * 1000 if not lowkey_mode else self.delay  # Milliseconds
        self.buttonless = bool(self.config["buttonless"])
        self.single_mode = bool(self.config["singleMode"])

        # Overlays
        self.denial_chance = int(self.config["denialChance"]) if bool(self.config["denialMode"]) else 0  # 0 to 100
        self.subliminal_chance = int(self.config["subliminalsChance"]) if bool(self.config["popupSubliminals"]) else 0  # 0 to 100
        self.max_subliminals = int(self.config["maxSubliminals"])
        self.subliminal_opacity = int(self.config["subliminalsAlpha"]) / 100  # Float between 0 and 1

        # Web
        self.web_chance = int(self.config["webMod"])  # 0 to 100
        self.web_on_popup_close = bool(self.config["webPopup"]) and not lowkey_mode

        # Prompt
        self.prompt_chance = int(self.config["promptMod"])  # 0 to 1000
        self.prompt_max_mistakes = int(self.config["promptMistakes"])

        # Audio
        self.audio_chance = int(self.config["audioMod"])  # 0 to 100
        self.max_audio = int(self.config["maxAudio"])

        # Video
        self.video_chance = int(self.config["vidMod"])  # 0 to 100
        self.video_volume = int(self.config["videoVolume"])  # 0 to 100
        self.max_video = int(self.config["maxVideos"]) if bool(self.config["maxVideoBool"]) else float("inf")
        self.video_hardware_acceleration = bool(self.config["videoHardwareAcceleration"])

        # Captions
        self.captions_in_popups = bool(self.config["showCaptions"])
        self.filename_caption_moods = bool(self.config["captionFilename"])  # TODO: How to handle this?
        self.multi_click_popups = bool(self.config["multiClick"])
        self.subliminal_message_popup_chance = int(self.config["capPopChance"])  # 0 to 100
        self.subliminal_message_popup_opacity = int(self.config["capPopOpacity"]) / 100  # Float between 0 and 1
        self.subliminal_message_popup_timeout = int(self.config["capPopTimer"])  # Milliseconds
        self.notification_chance = int(self.config["notificationChance"])  # 0 to 100
        self.notification_image_chance = int(self.config["notificationImageChance"])  # 0 to 100

        # Wallpaper
        self.rotate_wallpaper = bool(self.config["rotateWallpaper"])
        self.wallpaper_timer = int(self.config["wallpaperTimer"]) * 1000  # Milliseconds
        self.wallpaper_variance = int(self.config["wallpaperVariance"]) * 1000  # Milliseconds
        self.wallpapers = list(ast.literal_eval(self.config["wallpaperDat"]).values())  # TODO: Can fail, store in a better way

        # Dangerous
        self.drive_avoid_list = self.config["avoidList"].split(">")  # TODO: Store in a better way
        self.fill_drive = bool(self.config["fill"])
        self.drive_path = self.config["drivePath"]
        self.fill_delay = int(self.config["fill_delay"]) * 10  # Milliseconds
        self.replace_images = bool(self.config["replace"])
        self.replace_threshold = int(self.config["replaceThresh"])
        self.panic_disabled = bool(self.config["panicDisabled"])
        self.show_on_discord = bool(self.config["showDiscord"])

        # Basic modes
        self.lowkey_mode = lowkey_mode
        self.lowkey_corner = int(self.config["lkCorner"])
        self.moving_chance = int(self.config["movingChance"])  # 0 to 100
        self.moving_speed = int(self.config["movingSpeed"])
        self.moving_random = bool(self.config["movingRandom"])

        # Dangerous modes
        self.timer_mode = bool(self.config["timerMode"])
        self.timer_time = int(self.config["timerSetupTime"]) * 60 * 1000  # Milliseconds
        self.timer_password = self.config["safeword"]
        self.mitosis_mode = bool(self.config["mitosisMode"]) or lowkey_mode
        self.mitosis_strength = int(self.config["mitosisStrength"]) if not self.lowkey_mode else 1

        # Hibernate mode
        self.hibernate_mode = bool(self.config["hibernateMode"])
        self.hibernate_fix_wallpaper = bool(self.config["fixWallpaper"]) and self.hibernate_mode
        self.hibernate_type = self.config["hibernateType"]
        self.hibernate_delay_min = int(self.config["hibernateMin"]) * 1000  # Milliseconds
        self.hibernate_delay_max = int(self.config["hibernateMax"]) * 1000  # Milliseconds
        self.hibernate_activity = int(self.config["wakeupActivity"])
        self.hibernate_activity_length = int(self.config["hibernateLength"]) * 1000  # Milliseconds

        # Corruption mode
        self.corruption_mode = bool(self.config["corruptionMode"])
        self.corruption_full = bool(self.config["corruptionFullPerm"])
        self.corruption_fade = self.config["corruptionFadeType"]
        self.corruption_trigger = self.config["corruptionTrigger"]
        self.corruption_time = int(self.config["corruptionTime"]) * 1000  # Milliseconds
        self.corruption_popups = int(self.config["corruptionPopups"])
        self.corruption_launches = int(self.config["corruptionLaunches"])
        self.corruption_wallpaper = not bool(self.config["corruptionWallpaperCycle"])
        self.corruption_themes = not bool(self.config["corruptionThemeCycle"])
        self.corruption_purity = bool(self.config["corruptionPurityMode"])
        self.corruption_dev_mode = bool(self.config["corruptionDevMode"])
