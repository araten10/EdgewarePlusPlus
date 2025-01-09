from tkinter import BooleanVar, IntVar, StringVar

ConfigVar = IntVar | BooleanVar | StringVar


class Vars:
    entries: dict[str, ConfigVar] = {}

    def __init__(self, config: dict):
        self.config = config

        self.delay = self.make(IntVar, "delay")
        self.image_chance = self.make(IntVar, "popupMod")
        self.web_chance = self.make(IntVar, "webMod")
        self.audio_chance = self.make(IntVar, "audioMod")
        self.prompt_chance = self.make(IntVar, "promptMod")
        self.fill_drive = self.make(BooleanVar, "fill")
        self.random_fill =  self.make(BooleanVar, "random_fill")


        self.fill_delay = self.make(IntVar, "fill_delay")
        self.replace_images = self.make(BooleanVar, "replace")
        self.replace_threshold = self.make(IntVar, "replaceThresh")
        self.run_at_startup = self.make(BooleanVar, "start_on_logon")

        self.hibernate_mode = self.make(BooleanVar, "hibernateMode")
        self.hibernate_delay_min = self.make(IntVar, "hibernateMin")
        self.hibernate_delay_max = self.make(IntVar, "hibernateMax")
        self.hibernate_type = self.make(StringVar, "hibernateType")
        self.hibernate_activity = self.make(IntVar, "wakeupActivity")
        self.hibernate_activity_length = self.make(IntVar, "hibernateLength")
        self.hibernate_fix_wallpaper = self.make(BooleanVar, "fixWallpaper")

        self.show_on_discord = self.make(BooleanVar, "showDiscord")
        self.startup_splash = self.make(BooleanVar, "showLoadingFlair")
        self.captions_in_popups = self.make(BooleanVar, "showCaptions")
        self.panic_key = self.make(StringVar, "panicButton")
        self.panic_disabled = self.make(BooleanVar, "panicDisabled")

        self.prompt_max_mistakes = self.make(IntVar, "promptMistakes")
        self.mitosis_mode = self.make(BooleanVar, "mitosisMode")
        self.web_on_popup_close = self.make(BooleanVar, "webPopup")

        self.rotate_wallpaper = self.make(BooleanVar, "rotateWallpaper")
        self.wallpaper_timer = self.make(IntVar, "wallpaperTimer")
        self.wallpaper_variance = self.make(IntVar, "wallpaperVariance")

        self.timeout_enabled = self.make(BooleanVar, "timeoutPopups")
        self.timeout = self.make(IntVar, "popupTimeout")
        self.mitosis_strength = self.make(IntVar, "mitosisStrength")
        self.booru_name = self.make(StringVar, "booruName")

        self.booru_download = self.make(BooleanVar, "downloadEnabled")
        self.drive_path = self.make(StringVar, "drivePath")
        self.run_on_save_quit = self.make(BooleanVar, "runOnSaveQuit")

        self.timer_mode = self.make(BooleanVar, "timerMode")
        self.timer_time = self.make(IntVar, "timerSetupTime")
        self.lowkey_corner = self.make(IntVar, "lkCorner")
        self.opacity = self.make(IntVar, "lkScaling")
        self.lowkey_mode = self.make(BooleanVar, "lkToggle")

        self.timer_password = self.make(StringVar, "safeword")

        self.video_volume = self.make(IntVar, "videoVolume")
        self.video_chance = self.make(IntVar, "vidMod")
        self.denial_mode = self.make(BooleanVar, "denialMode")
        self.denial_chance = self.make(IntVar, "denialChance")
        self.popup_subliminals = self.make(IntVar, "popupSubliminals")

        self.min_score = self.make(IntVar, "booruMinScore")

        self.desktop_icons = self.make(BooleanVar, "desktopIcons")

        self.max_audio = self.make(IntVar, "maxAudio")
        self.max_video_enabled = self.make(BooleanVar, "maxVideoBool")
        self.max_video = self.make(IntVar, "maxVideos")

        self.subliminal_chance = self.make(IntVar, "subliminalsChance")
        self.max_subliminals = self.make(IntVar, "maxSubliminals")

        self.safe_mode = self.make(BooleanVar, "safeMode")

        self.toggle_internet = self.make(BooleanVar, "toggleInternet")
        self.toggle_hibernate_skip = self.make(BooleanVar, "toggleHibSkip")
        self.toggle_mood_set = self.make(BooleanVar, "toggleMoodSet")

        self.buttonless = self.make(BooleanVar, "buttonless")
        self.filename_caption_moods = self.make(BooleanVar, "captionFilename")
        self.single_mode = self.make(BooleanVar, "singleMode")

        self.corruption_mode = self.make(BooleanVar, "corruptionMode")
        self.corruption_dev_mode = self.make(BooleanVar, "corruptionDevMode")
        self.corruption_full = self.make(BooleanVar, "corruptionFullPerm")
        self.corruption_time = self.make(IntVar, "corruptionTime")
        self.corruption_popups = self.make(IntVar, "corruptionPopups")
        self.corruption_launches = self.make(IntVar, "corruptionLaunches")
        self.corruption_fade = self.make(StringVar, "corruptionFadeType")
        self.corruption_trigger = self.make(StringVar, "corruptionTrigger")
        self.corruption_wallpaper = self.make(BooleanVar, "corruptionWallpaperCycle")
        self.corruption_themes = self.make(BooleanVar, "corruptionThemeCycle")
        self.corruption_purity = self.make(BooleanVar, "corruptionPurityMode")

        self.pump_scare_offset = self.make(IntVar, "pumpScareOffset")

        self.vlc_mode = self.make(BooleanVar, "vlcMode")
        self.multi_click_popups = self.make(BooleanVar, "multiClick")

        self.theme = self.make(StringVar, "themeType")
        self.theme_ignore_config = self.make(BooleanVar, "themeNoConfig")

        self.preset_danger = self.make(BooleanVar, "presetsDanger")

        self.moving_chance = self.make(IntVar, "movingChance")
        self.moving_speed = self.make(IntVar, "movingSpeed")
        self.moving_random = self.make(BooleanVar, "movingRandom")

        self.subliminal_message_popup_chance = self.make(IntVar, "capPopChance")
        self.subliminal_message_popup_opacity = self.make(IntVar, "capPopOpacity")
        self.subliminal_message_popup_timeout = self.make(IntVar, "capPopTimer")
        self.subliminal_caption_mood = self.make(BooleanVar, "capPopMood")
        self.notification_mood = self.make(BooleanVar, "notificationMood")
        self.notification_chance = self.make(IntVar, "notificationChance")
        self.notification_image_chance = self.make(IntVar, "notificationImageChance")

        self.config["packPath"] = self.config["packPath"] or "default"
        self.pack_path = self.make(StringVar, "packPath")

        self.subliminal_opacity = self.make(IntVar, "subliminalsAlpha")

        self.message_off = self.make(BooleanVar, "messageOff")

    def make(self, var_init: type[ConfigVar], key: str) -> ConfigVar:
        value = self.config[key]
        var = var_init()
        match var:
            case IntVar():
                var.set(int(value))
            case BooleanVar():
                var.set(bool(value))
            case StringVar():
                var.set(value.strip())

        self.entries[key] = var
        return var
