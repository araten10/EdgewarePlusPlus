from dataclasses import dataclass


@dataclass
class CorruptionConfig:
    # TODO/TO CONSIDER FOR BLACKLIST:
    # would rotate_wallpaper even work at all if the user didn't have any set? can packs set the rotating wallpapers somehow? (other than via corruption levels)
    # you could maybe set wallpaperdat but not sure how many people would bother with this
    BLACKLIST = [
        "version",  # version, etc, things that make no sense to change
        "versionplusplus",
        "panicButton",  # while disabling panic could be used for danger-chasing fetishists, changing the hotkey serves little purpose
        "safeword",  # imo, the safeword is a safeword for a reason (timer mode)
        "drivePath",  # We can't know what paths exist and they look different on Linux and Windows
        "safeMode",  # optional warning in config to warn of dangerous settings. being able to disable remotely doesn't affect anything horny, just allows you to be a dick
        "toggleInternet",  # troubleshooting settings
        "toggleHibSkip",
        "toggleMoodSet",
        "corruptionMode",  # if you're turning off corruption mode with corruption just make it the final level lmao
        "presetsDanger",  # see safeMode
        "corruptionDevMode",
        "corruptionFullPerm",
        "messageOff",
        "runOnSaveQuit",
        "themeNoConfig",
        # Changing these settings would most likely not do anything with their current implementation
        "desktopIcons",
        "showLoadingFlair",
        "rotateWallpaper",
        "replace",  # replace images
        "replaceThresh",
        "avoidList",  # avoid list for replace images. also works on fill drive but due to filepath the only thing you can do with this is make it blank
        "start_on_logon",
        "showDiscord",  # show discord status, technically not PC dangerous but socially dangerous
        "timerMode",  # locks out panic until certain time has passed
        "timerSetupTime",
        "hibernateMode",
        "start_on_logon",
        # TODO: Test changing these, they will probably work but may have strange interactions
        # "lkToggle",
        "mitosisMode",
    ]

    # Settings I found that are maybe dead currently since I can't find use (feel free to delete this once it's taken care of):
    # pumpScareOffset (used to be for offsetting the pumpscare audio, might be irrelevant once we force vlc)

    # TO CONSIDER FOR DANGEROUS:
    # mitosismode/mitosis_strength can potentially cause a dangerous payload of popups if set incorrectly
    # capPopTimer could potentially cause seizures if low enough... however, considering not bothering with this as so many settings have to be set right
    # remember: a lot of obvious dangerous settings are not listed here as they are on the blacklist
    DANGEROUS = [
        "fill",  # fill drive
        "fill_delay",
        "maxFillThreads",
        "panicDisabled",  # disables panic in hotkey/system tray, can still be run via panic.pyw
        "webPopup",  # opens up web popup on popup close, this one could be cut from this list as it's not listed as dangerous in config but could lead to bad performance
    ]

    # When the setting has a value outside the given range, it is considered dangerous
    # (min, max)
    SAFE_RANGE = {
        "delay": (2000, None),
        "wakeupActivity": (0, 35),
        "hibernateMax": (10, None),
    }
