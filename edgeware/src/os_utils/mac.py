# Copyright (C) 2024 Araten & Marigold
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

import logging
import os
import subprocess
import sys
from pathlib import Path
from tkinter import Toplevel, Tk, Button, StringVar

import mpv
from os_utils.keyboard_listener_darwin import CGEventTapListener, vk_to_key_name
from paths import APP_BUNDLES, Process, find_app_bundle


def close_mpv(player: mpv.MPV) -> None:
    player.stop()


def set_borderless(window: Toplevel) -> None:
    # overrideredirect(True) removes a window from macOS's Cocoa focus chain,
    # so its Text widgets can never receive keyboard input. Prompt needs text
    # entry, so keep it a normal (topmost) window — the same special case Linux
    # KDE applies in os_utils/linux.py. Popups, splash and subliminals still
    # want borderless transparency.
    try:
        from features.prompt import Prompt

        if isinstance(window, Prompt):
            window.title("PROMPT")
            window.resizable(False, False)
            # Stay above everything but participate in the focus chain.
            window.attributes("-topmost", True)
            return
    except Exception:
        pass  # Prompt not importable yet (circular init); fall through to borderless

    window.tk.call('wm', 'overrideredirect', window._w, True)


def focus_window(window: Toplevel) -> None:
    """Force the given borderless window to become key and receive keyboard input.

    overrideredirect(True) windows on macOS are removed from the normal
    Cocoa focus chain, so calling focus_set()/focus_force() alone is not
    enough for a bundled .app.  We activate the app and make the window
    key through AppKit so typed characters reach the focused widget.
    """
    try:
        import AppKit
        app = AppKit.NSApplication.sharedApplication()
        app.activateIgnoringOtherApps_(True)
    except Exception as e:
        logging.warning(f"focus_window: could not activate app via AppKit: {e}")
    # makekeyandorderfront must run on the main thread; it is, since this is
    # called from a Tk callback.
    window.update_idletasks()
    window.lift()
    try:
        window.focus_force()
    except Exception as e:
        logging.warning(f"focus_window: focus_force failed: {e}")


def set_clickthrough(window: Toplevel) -> None:
    pass  # Disabled on macOS via settings.py and popup_tweaks.py


def get_wallpaper() -> Path | None:
    try:
        result = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to tell desktop 1 to get picture'],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()
        if output:
            return Path(output)
    except Exception as e:
        logging.warning(f"Failed to get wallpaper. Reason: {e}")
    return None


def set_wallpaper(wallpaper: Path) -> None:
    script = f'tell application "System Events" to tell every desktop to set picture to "{wallpaper}"'
    try:
        subprocess.run(["osascript", "-e", script], check=True)
    except Exception as e:
        logging.warning(f"Failed to set wallpaper. Reason: {e}")


def open_directory(url: str) -> None:
    subprocess.Popen(["open", url])


def make_shortcut(title: str, process: Path, icon: Path, location: Path | None = None) -> None:
    # FUTUREWORK: Could create Automator .app bundles instead of .command files
    # for a more native macOS experience (e.g. proper icons in Finder, Dock support).
    filename = f"{title}.command"

    if location:
        file = location / filename
    elif getattr(sys, "frozen", False):
        # Frozen builds: write to ~/Applications/Edgeware++/ to avoid macOS TCC
        # permission prompts for Desktop/Documents access.
        app_dir = Path.home() / "Applications" / "Edgeware++"
        app_dir.mkdir(parents=True, exist_ok=True)
        file = app_dir / filename
    else:
        file = Path(os.path.expanduser("~/Desktop")) / filename

    if getattr(sys, "frozen", False):
        bundle = find_app_bundle(APP_BUNDLES[title])
        if bundle:
            app_path = bundle
        else:
            # Fallback: assume siblings in the same directory
            app_path = Path(sys.executable).parent.parent.parent.parent / f"{APP_BUNDLES[title]}.app"
        content = [
            "#!/bin/bash",
            f'open "{app_path}"',
        ]
    else:
        content = [
            "#!/bin/bash",
            f'exec "{sys.executable}" "{process}"',
        ]

    file.write_text("\n".join(content))
    os.chmod(file, 0o755)


def toggle_run_at_startup(state: bool) -> None:
    if getattr(sys, "frozen", False):
        # In frozen mode, register the .app bundle as a login item
        bundle = find_app_bundle("Edgeware++")
        if bundle:
            script_path = str(bundle)
        else:
            script_path = str(Path(sys.executable).parent.parent.parent)
    else:
        script_path = str(Process.MAIN)

    if state:
        subprocess.run([
            "osascript", "-e",
            f'tell application "System Events" to make login item at end with properties '
            f'{{name:"Edgeware++", path:"{script_path}", hidden:false}}',
        ])
    else:
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to delete login item "Edgeware++"',
        ])


def set_schedule(vars) -> None:
    pass


def delete_schedule() -> None:
    pass


def send_panic_tray() -> None:
    """Send a panic signal via IPC (tray menu callback path).

    Imported lazily to avoid a circular import with panic.py (which imports
    from os_utils). The tray callback runs on pystray's Cocoa callback thread,
    so we send a message via IPC instead of calling panic() directly.
    """
    from multiprocessing.connection import Client
    from panic import ADDRESS, AUTHKEY

    with Client(address=ADDRESS, authkey=AUTHKEY) as connection:
        connection.send("panic_tray")


# ---------------------------------------------------------------------------
# TCC permissions (Accessibility + Input Monitoring)
# ---------------------------------------------------------------------------

def check_accessibility_permission() -> bool:
    """Check if the app has Accessibility permission on macOS.

    Uses AXIsProcessTrusted() via ctypes. Returns False if not granted or
    if the check fails.
    """
    try:
        import ctypes
        import ctypes.util

        framework_path = ctypes.util.find_library("ApplicationServices")
        if not framework_path:
            logging.warning("Could not find ApplicationServices framework")
            return False

        app_services = ctypes.cdll.LoadLibrary(framework_path)
        app_services.AXIsProcessTrusted.restype = ctypes.c_bool
        trusted = app_services.AXIsProcessTrusted()

        logging.info(
            f"Accessibility permission check: {'granted' if trusted else 'not granted'}"
        )
        return trusted
    except Exception as e:
        logging.warning(f"Could not check Accessibility permission: {e}")
        return False


def show_accessibility_dialog(root: Tk) -> None:
    """Show dialog explaining Accessibility permission requirement.

    If the user opts to open System Preferences, warn that a restart is required
    for the change to take effect, then quit the app so they can relaunch it.
    If they decline, keep running (the tray / IPC panic path still works).
    """
    from tkinter import messagebox

    message = (
        "Edgeware++ needs Accessibility permission to listen for the global panic hotkey while a prompt popup is open.\n\n"
        "To grant permission:\n"
        "1. Open System Preferences\n"
        "2. Go to Privacy & Security > Accessibility\n"
        "3. Click the lock icon and enter your password\n"
        "4. Check the box next to Edgeware++\n\n"
        "If you don't want to grant this permission, you can still use:\n"
        "• The Panic.app (separate application)\n"
        "• The tray icon menu\n"
        "• The Legacy Panic Key (requires focusing on a popup)\n\n"
        "Do you want to open System Preferences now?"
    )

    result = messagebox.askyesno("Accessibility Permission", message)
    if result:
        try:
            subprocess.Popen(
                [
                    "open",
                    "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
                ]
            )
        except Exception as e:
            logging.error(f"Failed to open System Preferences: {e}")

        messagebox.showinfo(
            "Restart Required",
            "Accessibility permission only takes effect after Edgeware++ is restarted.\n\n"
            "Edgeware++ will now close.  Please reopen it once you have granted permission.",
        )
        root.after(100, root.destroy)


def check_input_monitoring_permission() -> bool:
    """Check if the app has Input Monitoring permission on macOS.

    AXIsProcessTrusted() only proves Accessibility (which CGEventTap creation
    does NOT require).  The reliable signal for a global keyboard event tap is
    whether CGEventTapCreate itself returns a valid tap: if Input Monitoring
    has not been granted to this app, it returns None immediately.
    """
    try:
        import Quartz

        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionListenOnly,
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown),
            lambda proxy, event_type, event, refcon: event,
            None,
        )
        granted = tap is not None
        logging.info(
            f"Input Monitoring permission check: {'granted' if granted else 'not granted'}"
        )
        return granted
    except Exception as e:
        logging.warning(f"Could not check Input Monitoring permission: {e}")
        return False


def show_input_monitoring_dialog(root: Tk) -> None:
    """Show dialog explaining the Input Monitoring permission requirement.

    If the user opts to open System Settings, warn that a restart is required
    for the change to take effect, then quit the app so they can relaunch it.
    If they decline, keep running (the tray / IPC panic path still works).

    The correct macOS pane for global keyboard event taps is the Input
    Monitoring list under Privacy & Security, not Accessibility.
    """
    from tkinter import messagebox

    message = (
        "Edgeware++ needs Input Monitoring permission to listen for the global panic hotkey.\n\n"
        "To grant permission:\n"
        "1. Open System Settings\n"
        "2. Go to Privacy & Security > Input Monitoring\n"
        "3. Enable Edgeware++\n\n"
        "If you don't want to grant this permission, you can still use:\n"
        "• The Panic.app (separate application)\n"
        "• The tray icon menu\n\n"
        "Do you want to open System Settings now?"
    )

    result = messagebox.askyesno("Input Monitoring Permission", message)
    if result:
        try:
            subprocess.Popen(
                [
                    "open",
                    "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent",
                ]
            )
        except Exception as e:
            logging.error(f"Failed to open System Settings: {e}")

        messagebox.showinfo(
            "Restart Required",
            "Input Monitoring permission only takes effect after Edgeware++ is restarted.\n\n"
            "Edgeware++ will now close.  Please reopen it once you have granted permission.",
        )
        root.after(100, root.destroy)


# ---------------------------------------------------------------------------
# Notification Center authorization
# ---------------------------------------------------------------------------

def init_notifications(root: Tk, settings) -> None:
    """Request Notification Center authorization up front on macOS.

    macOS suppresses notifications when the app is not authorized.
    send_notification in features.misc requests permission lazily during a
    send, which can be rejected if the prompt never appeared while the app
    was foregrounded. Requesting it at startup (scheduled so it runs inside
    the Tk/CFRunLoop) makes macOS show the permission dialog early;
    desktop-notifier only prompts on first launch and returns the current
    status afterward.
    """
    if settings.notification_chance <= 0:
        return

    from config.settings import Settings  # type: ignore
    from desktop_notifier.sync import DesktopNotifierSync

    def request() -> None:
        try:
            DesktopNotifierSync(app_name="Edgeware++").request_authorisation()
        except Exception as e:
            logging.warning(f"Could not request notification authorization: {e}")

    # Run after the mainloop has started so CFRunLoop is pumping; otherwise the
    # first-ever permission callback can't be delivered and would deadlock startup.
    root.after(1500, request)


# ---------------------------------------------------------------------------
# Config window: global panic key capture via Quartz CGEventTap
# ---------------------------------------------------------------------------

class KeyListenerWindow(Toplevel):
    """Small topmost window used while capturing a global panic key."""

    def __init__(self) -> None:
        super().__init__()
        self.resizable(False, False)
        self.title("Key Listener")
        self.wm_attributes("-topmost", 1)
        self.geometry("250x250")
        self.focus_force()
        from tkinter import Label

        Label(self, text="Press any key or exit").pack(expand=1, fill="both")


def _vk_to_key_name(vk: int) -> str | None:
    """Convert a macOS virtual key code to a pynput-style key name."""
    return vk_to_key_name(vk)


def _request_global_panic_key_darwin(button: Button, var: StringVar, window: Toplevel) -> None:
    """macOS config-window implementation: capture a global panic key via CGEventTap."""
    try:
        import Quartz
    except ImportError:
        logging.error("PyObjC/Quartz not available — cannot use CGEventTap")
        from tkinter import messagebox
        messagebox.showerror(
            "Error",
            "PyObjC/Quartz not available. Please use the Legacy Panic Key in the Troubleshooting tab."
        )
        window.destroy()
        return

    if not check_accessibility_permission():
        logging.error("CGEventTap: Accessibility permission not granted")
        from tkinter import messagebox
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

    captured_key = [None]

    def on_capture(key_name: str) -> None:
        captured_key[0] = key_name

    listener = _CaptureTap(on_capture)
    if not listener.start():
        logging.error(
            "CGEventTap creation failed — Accessibility permission required. "
            "Go to System Settings → Privacy & Security → Accessibility and add this app."
        )
        from tkinter import messagebox
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

    def poll_key() -> None:
        """Poll the CGEventTap flag periodically."""
        if captured_key[0] is not None:
            key_name = captured_key[0]
            captured_key[0] = None
            button.configure(text=f"Set Global\nPanic Key\n<{key_name}>")
            var.set(key_name)
            try:
                listener.stop()
            except Exception:
                pass
            window.destroy()
            return
        window.after(50, poll_key)

    window.after(50, poll_key)

    def close() -> None:
        """Clean up when the window is closed."""
        try:
            listener.stop()
        except Exception:
            pass
        try:
            window.destroy()
        except Exception:
            pass

    def timeout_check() -> None:
        """Close the dialog if no key is pressed within 10 seconds."""
        logging.warning("No key pressed within 10 seconds")
        close()

    window.after(10000, timeout_check)
    window.protocol("WM_DELETE_WINDOW", close)


class _CaptureTap(CGEventTapListener):
    """CGEventTap for the config window that captures any single key press."""

    def __init__(self, on_capture) -> None:
        super().__init__()
        self._on_capture = on_capture

    def _build_mask(self) -> int:
        import Quartz
        return Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)

    def _on_key_event(self, keycode: int, is_down: bool) -> None:
        name = vk_to_key_name(keycode)
        if name is not None and self._on_capture:
            self._on_capture(name)


def request_global_panic_key(button: Button, var: StringVar) -> None:
    """macOS: capture a global panic key via Quartz CGEventTap (config window)."""
    window = KeyListenerWindow()
    _request_global_panic_key_darwin(button, var, window)
