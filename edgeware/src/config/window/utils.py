# Copyright (C) 2025 Araten & Marigold
#
# This file is part of Edgeware++.
#
# Edgeware++ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Edgeware++ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Edgeware++.  If not, see <https://www.gnu.org/licenses/>.

import json
import logging
import multiprocessing
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib
from multiprocessing.connection import Connection
from pathlib import Path
from threading import Thread
from tkinter import BooleanVar, Button, Event, IntVar, Label, Listbox, StringVar, TclError, Toplevel, Widget, messagebox, simpledialog

import os_utils
import utils
from paths import Data, launch_app

from config import load_config
from config.items import CONFIG_DANGER, DangerLevel
from config.vars import Vars

from os_utils import set_schedule, delete_schedule

# TODO: Don't load these here
config = load_config()
log_file = utils.init_logging("config")


class KeyListenerWindow(Toplevel):
    def __init__(self) -> None:
        super().__init__()
        self.resizable(False, False)
        self.title("Key Listener")
        self.wm_attributes("-topmost", 1)
        self.geometry("250x250")
        self.focus_force()
        Label(self, text="Press any key or exit").pack(expand=1, fill="both")


def request_legacy_panic_key(button: Button, var: StringVar) -> None:
    window = KeyListenerWindow()

    def assign_panic_key(event: Event) -> None:
        button.configure(text=f"Set Legacy\nPanic Key\n<{event.keysym}>")
        var.set(str(event.keysym))
        window.destroy()

    window.bind("<KeyPress>", assign_panic_key)


def _check_accessibility_darwin() -> bool:
    """Check and prompt for Accessibility permission on macOS."""
    try:
        import ctypes
        import ctypes.util

        framework_path = ctypes.util.find_library('ApplicationServices')
        if not framework_path:
            return True

        app_services = ctypes.cdll.LoadLibrary(framework_path)
        app_services.AXIsProcessTrusted.restype = ctypes.c_bool

        if app_services.AXIsProcessTrusted():
            return True

        logging.info("Accessibility not granted — prompting user via AXIsProcessTrustedWithOptions")
        # Trigger the macOS Accessibility permission prompt
        app_services.AXIsProcessTrustedWithOptions.restype = ctypes.c_bool
        opts = {str("AXTrustedCheckOptionPrompt"): True}
        ctypes.cf = ctypes.CDLL(None)
        trusted = app_services.AXIsProcessTrustedWithOptions(opts)
        logging.info("Accessibility prompt shown, result: %s", trusted)
        return trusted
    except Exception as e:
        logging.warning("Could not check Accessibility permission: %s", e)
        return True  # Assume granted if check fails, let CGEventTapCreate decide


def _request_global_panic_key_darwin(button: Button, var: StringVar, window: Toplevel) -> None:
    """macOS implementation using CGEventTap directly."""
    try:
        import Quartz
    except ImportError:
        logging.error("PyObjC/Quartz not available — cannot use CGEventTap")
        messagebox.showerror(
            "Error",
            "PyObjC/Quartz not available. Please use the Legacy Panic Key in the Troubleshooting tab."
        )
        window.destroy()
        return

    if not _check_accessibility_darwin():
        logging.error("CGEventTap: Accessibility permission not granted")
        messagebox.showerror(
            "Accessibility Permission Required",
            "The keyboard listener requires Accessibility permission.\n\n"
            "To grant permission:\n"
            "1. Open System Settings → Privacy & Security → Accessibility\n"
            "2. Click the lock icon and enter your password\n"
            "3. Enable the toggle next to Edgeware++ Config\n\n"
            "You may need to restart the app after granting permission.\n\n"
            "Alternatively, you can use the Legacy Panic Key in the Troubleshooting tab."
        )
        window.destroy()
        return

    # Thread-safe flag: CGEventTap callback sets it, main thread polls it
    captured_key = [None]  # Use list to allow mutation in nested function
    tap = [None]  # Use list to allow mutation in nested function
    loop_ref = [None]
    running = [True]

    def callback(proxy, event_type, event, refcon):
        """CGEventTap callback."""
        try:
            # Handle CGEventTap disabled by timeout
            if event_type == Quartz.kCGEventTapDisabledByTimeout:
                logging.warning("CGEventTap disabled by timeout — re-enabling")
                if tap[0] is not None:
                    Quartz.CGEventTapEnable(tap[0], True)
                return event

            # Only process key down events
            if event_type == Quartz.kCGEventKeyDown:
                keycode = Quartz.CGEventGetIntegerValueField(
                    event, Quartz.kCGKeyboardEventKeycode
                )
                # Map keycode to key name
                key_name = _vk_to_key_name(keycode)
                if key_name is not None:
                    captured_key[0] = key_name
        except Exception as e:
            logging.error(f"CGEventTap callback error: {e}")

        return event

    # Create the CGEventTap
    tap_obj = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,
        Quartz.kCGHeadInsertEventTap,
        Quartz.kCGEventTapOptionListenOnly,
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown),
        callback,
        None,
    )

    if tap_obj is None:
        logging.error(
            "CGEventTap creation failed — Accessibility permission required. "
            "Go to System Settings → Privacy & Security → Accessibility and add this app."
        )
        messagebox.showerror(
            "Accessibility Permission Required",
            "The keyboard listener requires Accessibility permission.\n\n"
            "To grant permission:\n"
            "1. Open System Preferences\n"
            "2. Go to Privacy & Security > Accessibility\n"
            "3. Click the lock icon and enter your password\n"
            "4. Check the box next to Edgeware++ Config\n\n"
            "Alternatively, you can use the Legacy Panic Key in the Troubleshooting tab."
        )
        window.destroy()
        return

    tap[0] = tap_obj

    # Create run loop source from the tap
    run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap_obj, 0)

    def run_loop():
        """Run the CFRunLoop in a daemon thread."""
        try:
            loop = Quartz.CFRunLoopGetCurrent()
            loop_ref[0] = loop
            Quartz.CFRunLoopAddSource(loop, run_loop_source, Quartz.kCFRunLoopCommonModes)
            Quartz.CGEventTapEnable(tap_obj, True)
            logging.info("CGEventTap keyboard listener started for config")
            Quartz.CFRunLoopRun()
        except Exception as e:
            logging.error(f"CGEventTap run loop error: {e}")
        finally:
            running[0] = False

    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()

    def poll_key() -> None:
        """Poll the CGEventTap flag periodically."""
        if not running[0]:
            return
        if captured_key[0] is not None:
            key_name = captured_key[0]
            captured_key[0] = None
            # Assign the captured key
            button.configure(text=f"Set Global\nPanic Key\n<{key_name}>")
            var.set(key_name)
            # Stop the listener and close the window
            try:
                if tap[0] is not None:
                    Quartz.CGEventTapEnable(tap[0], False)
                if loop_ref[0] is not None:
                    Quartz.CFRunLoopStop(loop_ref[0])
            except Exception:
                pass
            window.destroy()
            return
        window.after(50, poll_key)

    # Start polling
    window.after(50, poll_key)

    def close() -> None:
        """Clean up when the window is closed."""
        running[0] = False
        try:
            if tap[0] is not None:
                Quartz.CGEventTapEnable(tap[0], False)
            if loop_ref[0] is not None:
                Quartz.CFRunLoopStop(loop_ref[0])
        except Exception:
            pass
        try:
            window.destroy()
        except Exception:
            pass

    def timeout_check() -> None:
        """Close the dialog if no key is pressed within 10 seconds."""
        if running[0] and captured_key[0] is None:
            logging.warning("No key pressed within 10 seconds")
            close()

    # 10-second timeout
    window.after(10000, timeout_check)

    window.protocol("WM_DELETE_WINDOW", close)


def _vk_to_key_name(vk: int) -> str | None:
    """Convert a macOS virtual key code to a key name string."""
    # Map virtual key codes to key names
    VK_TO_KEY_NAME = {
        0x35: "Key.esc",
        0x24: "Key.enter",
        0x4C: "Key.enter",
        0x30: "Key.tab",
        0x33: "Key.backspace",
        0x75: "Key.delete",
        0x7E: "Key.up",
        0x7D: "Key.down",
        0x7B: "Key.left",
        0x7C: "Key.right",
        0x73: "Key.home",
        0x77: "Key.end",
        0x74: "Key.pageup",
        0x79: "Key.pagedown",
        0x7A: "Key.f1",
        0x78: "Key.f2",
        0x63: "Key.f3",
        0x76: "Key.f4",
        0x60: "Key.f5",
        0x61: "Key.f6",
        0x62: "Key.f7",
        0x64: "Key.f8",
        0x65: "Key.f9",
        0x6D: "Key.f10",
        0x67: "Key.f11",
        0x6F: "Key.f12",
        0x37: "Key.cmd",
        0x36: "Key.cmd_r",
        0x38: "Key.shift",
        0x3C: "Key.shift_r",
        0x3B: "Key.ctrl",
        0x3E: "Key.ctrl_r",
        0x3A: "Key.alt",
        0x3D: "Key.alt_r",
        0x31: "Key.space",
        # Letter keys
        0x00: "a", 0x01: "s", 0x02: "d", 0x03: "f", 0x04: "h",
        0x05: "g", 0x06: "z", 0x07: "x", 0x08: "c", 0x09: "v",
        0x0B: "b", 0x0C: "q", 0x0D: "w", 0x0E: "e", 0x0F: "r",
        0x10: "y", 0x11: "t", 0x1F: "o", 0x20: "u",
        0x21: "[", 0x1E: "]", 0x22: "i", 0x23: "p",
        0x25: "l", 0x26: "j", 0x27: "'", 0x28: "k",
        0x29: ";", 0x2A: "\\", 0x2B: ",", 0x2C: "/",
        0x2D: "n", 0x2E: "m", 0x2F: ".",
        # Number keys
        0x12: "1", 0x13: "2", 0x14: "3", 0x15: "4", 0x17: "5",
        0x16: "6", 0x1A: "7", 0x1C: "8", 0x19: "9", 0x1D: "0",
    }
    return VK_TO_KEY_NAME.get(vk)


def _config_keyboard_listener(connection: Connection) -> None:
    """Pynput keyboard listener subprocess target.

    Must be a top-level function so multiprocessing.spawn can pickle it.
    Runs pynput in its own main thread via subprocess, which is required
    because macOS TSM APIs (called by pynput) assert they run on the
    main thread.
    """
    try:
        from utils import init_logging
        init_logging("keyboard_listener")
        logging.info("Config keyboard listener subprocess started (PID %d)", __import__("os").getpid())
    except Exception as e:
        print(f"Failed to initialize config keyboard listener logging: {e}")

    from pynput import keyboard

    def on_release(key):
        try:
            logging.info("Key released: %s — sending via pipe", key)
            connection.send(str(key))
        except Exception as e:
            logging.error("Failed to send key event: %s", e)
            raise

    try:
        logging.info("Creating pynput keyboard Listener")
        listener = keyboard.Listener(on_release=on_release)
        logging.info("Starting pynput keyboard Listener")
        listener.start()
        logging.info("Pynput listener thread alive: %s", listener.is_alive())
        logging.info("Sending 'focus' to parent")
        connection.send("focus")
        logging.info("'focus' sent — joining listener thread")
        listener.join()
        logging.info("Listener thread joined (exit code: %s)", listener.daemon)
    except Exception as exc:
        logging.error("Config keyboard listener subprocess crashed: %s", exc, exc_info=True)
    finally:
        logging.info("Config keyboard listener subprocess exiting")
        try:
            connection.close()
        except Exception:
            pass


def request_global_panic_key(button: Button, var: StringVar) -> None:
    if sys.platform == "darwin":
        window = KeyListenerWindow()
        _request_global_panic_key_darwin(button, var, window)
        return

    window = KeyListenerWindow()

    def close() -> None:
        try:
            window.destroy()
        except Exception:
            pass
        try:
            if process.is_alive():
                process.terminate()
        except Exception:
            pass

    def assign_panic_key(key: str) -> None:
        button.configure(text=f"Set Global\nPanic Key\n<{key}>")
        var.set(key)
        close()

    def receive_panic_key() -> None:
        try:
            logging.info("receive_panic_key: waiting for 'focus' from subprocess")
            assert parent_connection.recv() == "focus"
            logging.info("receive_panic_key: got 'focus', focusing window")
            window.after(0, window.focus_force)

            logging.info("receive_panic_key: waiting for key event")
            key = parent_connection.recv()
            logging.info("receive_panic_key: got key %s", key)
            window.after(0, lambda: assign_panic_key(key))
        except EOFError:
            logging.error("receive_panic_key: subprocess pipe closed (EOFError)")
            window.after(0, lambda: messagebox.showerror(
                "Keyboard Listener Error",
                "The keyboard listener failed to start. This may be due to missing Accessibility permission.\n\n"
                "To grant permission:\n"
                "1. Open System Preferences\n"
                "2. Go to Privacy & Security > Accessibility\n"
                "3. Click the lock icon and enter your password\n"
                "4. Check the box next to Edgeware++ Config\n\n"
                "Alternatively, you can use the Legacy Panic Key in the Troubleshooting tab,\n"
                "which doesn't require Accessibility permission but requires focusing on a popup."
            ))
            window.after(0, window.destroy)
        except AssertionError:
            logging.error("Did not receive focus message from keyboard listener process")

    def timeout_check() -> None:
        """Close the dialog if no key is pressed within 10 seconds."""
        try:
            if process.is_alive():
                process.terminate()
                window.after(0, lambda: messagebox.showwarning(
                    "Timeout",
                    "No key pressed within 10 seconds. Dialog closing.\n\n"
                    "Please try again or use the Legacy Panic Key in the Troubleshooting tab."
                ))
                window.after(0, window.destroy)
        except Exception:
            pass

    try:
        ctx = multiprocessing.get_context("spawn")
        parent_connection, child_connection = ctx.Pipe()
        process = ctx.Process(target=_config_keyboard_listener, args=(child_connection,), daemon=True)
        process.start()
        child_connection.close()
    except Exception as e:
        logging.error(f"Failed to start keyboard listener process: {e}")
        messagebox.showerror(
            "Error",
            f"Failed to start keyboard listener: {e}\n\n"
            "Please use the Legacy Panic Key in the Troubleshooting tab."
        )
        window.destroy()
        return

    Thread(target=receive_panic_key).start()

    # 10-second timeout
    window.after(10000, timeout_check)

    window.protocol("WM_DELETE_WINDOW", close)


# TODO: Review these functions
def all_children(widget: Widget) -> list[Widget]:
    return [widget] + [subchild for child in widget.winfo_children() for subchild in all_children(child)]


def confirm_overwrite(path: Path) -> bool:
    if not path.exists():
        return True

    type = "directory" if path.is_dir() else "file"
    delete = shutil.rmtree if path.is_dir() else os.remove

    confirm = messagebox.askyesno("Confirm", f'Path "{path}" already exists. This {type} will be deleted and overwritten. Is this okay?')
    if confirm:
        delete(path)

    return confirm


def get_live_version() -> str:
    url = "http://raw.githubusercontent.com/araten10/EdgewarePlusPlus/main/edgeware/assets/default_config.json"

    test = config["toggleInternet"]
    if test != 0:
        logging.info("GitHub connection is disabled, version will not be checked.")
        return "Version check disabled!"

    try:
        with open(urllib.request.urlretrieve(url)[0], "r") as live_config:
            return json.loads(live_config.read())["versionplusplus"]
    except Exception as e:
        logging.warning(f"Failed to fetch version on GitHub.\n\tReason: {e}")
        return "Could not check version."


def write_save(vars: Vars, exit_at_end: bool = False) -> None:
    if vars.safe_mode.get() and exit_at_end and not safe_check(vars):
        return

    logging.info("starting config save write...")
    temp = config.copy()
    temp["wallpaperDat"] = str(config["wallpaperDat"])

    os_utils.toggle_run_at_startup(vars.run_at_startup.get())

    for key, var in vars.entries.items():
        value = var.get()
        if key == "packPath":
            value = value if value != "default" else None
        temp[key] = (1 if value else 0) if type(value) is bool else value

    if temp["schedule"]:
        set_schedule(vars)
    else:
        delete_schedule()

    with open(Data.CONFIG, "w") as file:
        file.write(json.dumps(temp))
        logging.info(f"wrote config file: {json.dumps(temp)}")

    if not (len(sys.argv) > 1 and sys.argv[1] == "--first-launch-configure") and vars.run_on_save_quit.get() and exit_at_end:
        launch_app("Edgeware++")

    if exit_at_end:
        logging.info("exiting config")
        sys.exit()
    else:
        messagebox.showinfo("Success!", "Settings saved successfully!")


def assign(obj: StringVar | IntVar | BooleanVar, var: str | int | bool) -> None:
    try:
        obj.set(var)
    except Exception as e:
        logging.warning(f"Failed to assign variable. Reason: {e}")


def safe_check(vars: Vars) -> bool:
    danger_levels = {
        DangerLevel.EXTREME: [],
        DangerLevel.MAJOR: [],
        DangerLevel.MEDIUM: [],
        DangerLevel.MINOR: [],
    }

    for key, var in vars.entries.items():
        danger = CONFIG_DANGER.get(key)
        if danger and danger.check(var.get()):
            danger_levels[danger.level].append(f"\n•{danger.warning or key}")

    danger_num = 0
    warnings = ""
    for level, dangers in danger_levels.items():
        danger_num += len(dangers)
        if dangers:
            warnings += f"\n\n{level.value.capitalize()}{''.join(dangers)}"

    return (
        messagebox.askyesno(
            "Dangerous Settings Detected!",
            f"{danger_num} potentially dangerous setting(s) detected! Do you want to save anyway? {warnings}",
            icon="warning",
        )
        if danger_num
        else True
    )


def clear_launches(confirmation: bool) -> None:
    try:
        if os.path.exists(Data.CORRUPTION_LAUNCHES):
            os.remove(Data.CORRUPTION_LAUNCHES)
            if confirmation:
                messagebox.showinfo(
                    "Cleaning Completed",
                    "The file that manages corruption launches has been deleted, and will be remade next time you start Edgeware with corruption on!",
                )
        else:
            if confirmation:
                messagebox.showinfo(
                    "No launches file!",
                    "There is no launches file to delete!\n\nThe launches file is used"
                    " for the launch transition mode, and is automatically deleted when you load a new pack. To generate a new"
                    " one, simply start Edgeware with the corruption setting on!",
                )
    except Exception as e:
        print(f"failed to clear launches. {e}")
        logging.warning(f"could not delete the corruption launches file. {e}")


def add_list(tk_list_obj: Listbox, key: str, title: str, text: str) -> None:
    name = simpledialog.askstring(title, text)
    if name != "" and name is not None:
        config[key] = f"{config[key]}>{name}"
        tk_list_obj.insert(2, name)


def remove_list(tk_list_obj: Listbox, key: str, title: str, text: str) -> None:
    index = int(tk_list_obj.curselection()[0])
    item_name = tk_list_obj.get(index)
    if index > 0:
        config[key] = config[key].replace(f">{item_name}", "")
        tk_list_obj.delete(tk_list_obj.curselection())
    else:
        messagebox.showwarning(title, text)


def remove_list_(tk_list_obj: Listbox, key: str, title: str, text: str) -> None:
    index = int(tk_list_obj.curselection()[0])
    item_name = tk_list_obj.get(index)
    print(config[key])
    print(item_name)
    print(len(config[key].split(">")))
    if len(config[key].split(">")) > 1:
        if index > 0:
            config[key] = config[key].replace(f">{item_name}", "")
        else:
            config[key] = config[key].replace(f"{item_name}>", "")
        tk_list_obj.delete(tk_list_obj.curselection())
    else:
        messagebox.showwarning(title, text)


def reset_list(tk_list_obj: Listbox, key: str, default: str) -> None:
    try:
        tk_list_obj.delete(0, 999)
    except Exception as e:
        print(e)
    config[key] = default
    for setting in config[key].split(">"):
        tk_list_obj.insert(1, setting)


def set_widget_states(state: bool, widgets: list[Widget], demo: bool = False) -> None:
    theme = config["themeType"].strip()

    # TODO: Use the same Theme objects as the main program
    if theme == "Original" or (config["themeNoConfig"] and not demo):
        set_widget_states_with_colors(state, widgets, "#f0f0f0", "gray35")
    else:
        if theme == "Dark":
            set_widget_states_with_colors(state, widgets, "#282c34", "gray65")
        if theme == "The One":
            set_widget_states_with_colors(state, widgets, "#282c34", "#37573d")
        if theme == "Ransom":
            set_widget_states_with_colors(state, widgets, "#841212", "#573737")
        if theme == "Goth":
            set_widget_states_with_colors(state, widgets, "#282c34", "#4b3757")
        if theme == "Bimbo":
            set_widget_states_with_colors(state, widgets, "#ffc5cd", "#bc7abf")


def set_widget_states_with_colors(state: bool, widgets: list[Widget], color_on: str, color_off: str) -> None:
    for widget in widgets:
        for child in [widget, *all_children(widget)]:
            # TODO: Better way to check if state and bg exist as options
            try:
                child.configure(state=("normal" if state else "disabled"))
            except TclError:
                pass

            try:
                child.configure(bg=(color_on if state else color_off))
            except TclError:
                pass


def refresh() -> None:
    launch_app("Edgeware++ Config")
    sys.exit()
