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

"""macOS keyboard listener using CGEventTap directly.

This module provides a keyboard listener that uses Quartz CGEventTap directly
instead of pynput. This avoids issues with Input Monitoring permission in
packaged/bundled macOS apps, where a pynput subprocess does not reliably
receive key events.

The CGEventTap runs in a daemon thread with its own CFRunLoop.
A thread-safe flag is set by the callback, which is polled by the
main thread using Tk's after() method. This keeps the listener entirely
in-process (no subprocess) while still isolating the Quartz tap from the
Tk main loop.

The raw Quartz CGEventTap does NOT call pynput/macOS TSM APIs, so it
does not interfere with text input in Prompt Text widgets and does not crash on
non-main threads.
"""

import logging
import threading
from collections.abc import Callable

# macOS virtual key codes
# https://gist.github.com/eegrok/949034
VK_ESCAPE = 0x35
VK_A = 0x00
VK_S = 0x01
VK_D = 0x02
VK_F = 0x03
VK_H = 0x04
VK_G = 0x05
VK_Z = 0x06
VK_X = 0x07
VK_C = 0x08
VK_V = 0x09
VK_B = 0x0B
VK_Q = 0x0C
VK_W = 0x0D
VK_E = 0x0E
VK_R = 0x0F
VK_Y = 0x10
VK_T = 0x11
VK_1 = 0x12
VK_2 = 0x13
VK_3 = 0x14
VK_4 = 0x15
VK_6 = 0x16
VK_5 = 0x17
VK_EQUAL = 0x18
VK_9 = 0x19
VK_7 = 0x1A
VK_MINUS = 0x1B
VK_8 = 0x1C
VK_0 = 0x1D
VK_RBRACKET = 0x1E
VK_O = 0x1F
VK_U = 0x20
VK_LBRACKET = 0x21
VK_I = 0x22
VK_P = 0x23
VK_RETURN = 0x24
VK_L = 0x25
VK_J = 0x26
VK_QUOTE = 0x27
VK_K = 0x28
VK_SEMICOLON = 0x29
VK_BACKSLASH = 0x2A
VK_COMMA = 0x2B
VK_SLASH = 0x2C
VK_N = 0x2D
VK_M = 0x2E
VK_PERIOD = 0x2F
VK_TAB = 0x30
VK_SPACE = 0x31
VK_TILDE = 0x32
VK_DELETE = 0x33
VK_COMMAND = 0x37
VK_COMMAND_R = 0x36
VK_SHIFT = 0x38
VK_CAPSLOCK = 0x39
VK_OPTION = 0x3A
VK_CONTROL = 0x3B
VK_RSHIFT = 0x3C
VK_ROPTION = 0x3D
VK_RCONTROL = 0x3E
VK_FUNCTION = 0x3F
# Arrow / navigation keys
VK_UP = 0x7E
VK_DOWN = 0x7D
VK_LEFT = 0x7B
VK_RIGHT = 0x7C
VK_HOME = 0x73
VK_END = 0x77
VK_PAGEUP = 0x74
VK_PAGEDOWN = 0x79
# Function keys
VK_F1 = 0x7A
VK_F2 = 0x78
VK_F3 = 0x63
VK_F4 = 0x76
VK_F5 = 0x60
VK_F6 = 0x61
VK_F7 = 0x62
VK_F8 = 0x64
VK_F9 = 0x65
VK_F10 = 0x6D
VK_F11 = 0x67
VK_F12 = 0x6F

# Map key names to virtual key codes (pynput-style names).
KEY_NAME_TO_VK = {
    "Key.esc": VK_ESCAPE,
    "Key.escape": VK_ESCAPE,
    "Key.enter": VK_RETURN,
    "Key.return": VK_RETURN,
    "Key.space": VK_SPACE,
    "Key.tab": VK_TAB,
    "Key.backspace": VK_DELETE,
    "Key.delete": VK_DELETE,
    "Key.cmd": VK_COMMAND,
    "Key.cmd_l": VK_COMMAND,
    "Key.cmd_r": VK_COMMAND_R,
    "Key.shift": VK_SHIFT,
    "Key.shift_l": VK_SHIFT,
    "Key.shift_r": VK_RSHIFT,
    "Key.ctrl": VK_CONTROL,
    "Key.ctrl_l": VK_CONTROL,
    "Key.ctrl_r": VK_RCONTROL,
    "Key.alt": VK_OPTION,
    "Key.alt_l": VK_OPTION,
    "Key.alt_r": VK_ROPTION,
    # Arrow / navigation keys
    "Key.up": VK_UP,
    "Key.down": VK_DOWN,
    "Key.left": VK_LEFT,
    "Key.right": VK_RIGHT,
    "Key.home": VK_HOME,
    "Key.end": VK_END,
    "Key.pageup": VK_PAGEUP,
    "Key.pagedown": VK_PAGEDOWN,
    # Function keys
    "Key.f1": VK_F1,
    "Key.f2": VK_F2,
    "Key.f3": VK_F3,
    "Key.f4": VK_F4,
    "Key.f5": VK_F5,
    "Key.f6": VK_F6,
    "Key.f7": VK_F7,
    "Key.f8": VK_F8,
    "Key.f9": VK_F9,
    "Key.f10": VK_F10,
    "Key.f11": VK_F11,
    "Key.f12": VK_F12,
    # Letter keys
    "a": VK_A, "b": VK_B, "c": VK_C, "d": VK_D, "e": VK_E,
    "f": VK_F, "g": VK_G, "h": VK_H, "i": VK_I, "j": VK_J,
    "k": VK_K, "l": VK_L, "m": VK_M, "n": VK_N, "o": VK_O,
    "p": VK_P, "q": VK_Q, "r": VK_R, "s": VK_S, "t": VK_T,
    "u": VK_U, "v": VK_V, "w": VK_W, "x": VK_X, "y": VK_Y,
    "z": VK_Z,
    # Number keys
    "0": VK_0, "1": VK_1, "2": VK_2, "3": VK_3, "4": VK_4,
    "5": VK_5, "6": VK_6, "7": VK_7, "8": VK_8, "9": VK_9,
    # Punctuation
    "[": VK_LBRACKET, "]": VK_RBRACKET, "'": VK_QUOTE,
    ";": VK_SEMICOLON, "\\": VK_BACKSLASH, ",": VK_COMMA,
    "/": VK_SLASH, ".": VK_PERIOD, "-": VK_MINUS,
    "=": VK_EQUAL, "`": VK_TILDE,
}

# Reverse lookup (virtual key code -> name). Derived from KEY_NAME_TO_VK so the
# two maps can never drift apart. When several names share a keycode, the first one
# wins (e.g. 0x33 -> "Key.backspace", not "Key.delete").
VK_TO_KEY_NAME: dict[int, str] = {}
for _name, _vk in KEY_NAME_TO_VK.items():
    VK_TO_KEY_NAME.setdefault(_vk, _name)


def vk_to_key_name(vk: int) -> str | None:
    """Convert a macOS virtual key code to a pynput-style key name.

    Returns ``None`` for key codes that are not mapped.
    """
    return VK_TO_KEY_NAME.get(vk)


class CGEventTapListener:
    """Reusable Quartz CGEventTap running on its own CFRunLoop thread.

    Encapsulates the shared plumbing behind every global keyboard event tap on
    macOS: creating the tap, enabling it on a daemon-thread CFRunLoop,
    re-enabling it when macOS disables it after a timeout, and stopping it
    cleanly. Subclasses only need to:

    * optionally override :meth:`_build_mask` to choose which event types to
      listen for (default: key down + key up), and
    * implement :meth:`_on_key_event`.

    The callback runs on the tap thread; any UI work must be marshalled back to
    the Tk main thread by the caller.
    """

    def __init__(self) -> None:
        self._tap = None
        self._loop_ref = None
        self._thread = None
        self._running = False

    @property
    def is_running(self) -> bool:
        """True while the CFRunLoop thread is alive and the tap is enabled."""
        return self._running

    def is_alive(self) -> bool:
        """Duck-typed alias for :attr:`is_running` (used by Prompt's restart check)."""
        return self._running

    def _build_mask(self) -> int:
        """Return the CGEventMaskBit combination this listener subscribes to."""
        import Quartz

        return (
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)
            | Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp)
        )

    def start(self) -> bool:
        """Create the CGEventTap and start its CFRunLoop thread.

        Returns:
            True if the tap was created and enabled, False otherwise.
        """
        if self._running:
            return True

        try:
            import Quartz
        except ImportError:
            logging.error("PyObjC/Quartz not available — cannot start CGEventTap")
            return False

        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionListenOnly,
            self._build_mask(),
            self._callback,
            None,
        )
        if tap is None:
            logging.error(
                "CGEventTap creation failed — Accessibility permission required. "
                "Go to System Settings → Privacy & Security → Accessibility and add this app."
            )
            return False

        self._tap = tap
        run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)

        def run_loop():
            try:
                loop = Quartz.CFRunLoopGetCurrent()
                self._loop_ref = loop
                Quartz.CFRunLoopAddSource(loop, run_loop_source, Quartz.kCFRunLoopCommonModes)
                Quartz.CGEventTapEnable(tap, True)
                self._running = True
                logging.info("CGEventTap enabled on CFRunLoop")
                Quartz.CFRunLoopRun()
            except Exception as e:
                logging.error(f"CGEventTap run loop error: {e}")
            finally:
                self._running = False

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

        return True

    def stop(self) -> None:
        """Stop the CGEventTap and join its CFRunLoop thread."""
        if not self._running:
            return

        self._running = False

        if self._loop_ref is not None:
            try:
                import Quartz
                Quartz.CFRunLoopStop(self._loop_ref)
            except Exception as e:
                logging.error(f"Error stopping CGEventTap run loop: {e}")
            self._loop_ref = None

        if self._tap is not None:
            try:
                import Quartz
                Quartz.CGEventTapEnable(self._tap, False)
            except Exception:
                pass
            self._tap = None

        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

        logging.info("CGEventTap stopped")

    def _callback(self, proxy, event_type, event, refcon):
        """CGEventTap callback.

        Runs on the tap thread. Handles the disabled-by-timeout re-enable and
        dispatches key events to :meth:`_on_key_event`.
        """
        try:
            import Quartz

            if event_type == Quartz.kCGEventTapDisabledByTimeout:
                logging.warning("CGEventTap disabled by timeout — re-enabling")
                Quartz.CGEventTapEnable(self._tap, True)
                return event

            keycode = Quartz.CGEventGetIntegerValueField(
                event, Quartz.kCGKeyboardEventKeycode
            )
            is_down = event_type == Quartz.kCGEventKeyDown
            self._on_key_event(keycode, is_down)
        except Exception as e:
            logging.error(f"CGEventTap callback error: {e}")

        return event

    def _on_key_event(self, keycode: int, is_down: bool) -> None:
        """Handle a key down/up event. Runs on the tap thread."""
        raise NotImplementedError


class DarwinKeyboardListener(CGEventTapListener):
    """macOS keyboard listener using CGEventTap directly.

    This listener runs in the main process (not a subprocess) to avoid
    permission inheritance issues. The CGEventTap runs in a daemon thread
    with its own CFRunLoop, and thread-safe flags are polled by the main
    thread using Tk's after() method.

    Args:
        target_key: The key name to trigger a panic (e.g., "Key.esc").
        on_panic: Callback invoked when the panic key is pressed.
        alt_keys: Optional list of alt key names to track for press/release.
        on_alt_change: Optional callback called with (alt_held: bool) whenever
            an alt key state changes. Only meaningful if alt_keys is provided.
        poll_interval_ms: Interval in milliseconds to poll flags (default: 50).
    """

    def __init__(
        self,
        target_key: str,
        on_panic: Callable[[], None],
        alt_keys: list[str] | None = None,
        on_alt_change: Callable[[bool], None] | None = None,
        poll_interval_ms: int = 50,
    ) -> None:
        super().__init__()
        self._target_key = target_key
        self._on_panic = on_panic
        self._alt_keys = {KEY_NAME_TO_VK[k] for k in (alt_keys or []) if k in KEY_NAME_TO_VK}
        self._on_alt_change = on_alt_change
        self._poll_interval_ms = poll_interval_ms

        # Thread-safe flags: CGEventTap callback sets them, main thread polls them.
        self._panic_pending = False
        self._alt_held = False
        self._pressed_alts: set[int] = set()
        self._lock = threading.Lock()

        # Resolve target key code
        self._target_vk = KEY_NAME_TO_VK.get(target_key)
        if self._target_vk is None:
            raise ValueError(f"Unknown key name: {target_key}")

    def start(self) -> bool:
        """Start the keyboard listener.

        Returns:
            True if the listener started successfully, False otherwise.
        """
        ok = super().start()
        if ok:
            logging.info(
                "CGEventTap keyboard listener started: %s (keycode 0x%02X)",
                self._target_key,
                self._target_vk,
            )
        else:
            logging.error("Failed to start macOS CGEventTap keyboard listener")
        return ok

    def poll(self) -> bool:
        """Consume a pending panic-key press and fire the callback.

        Should be called periodically from the main thread (e.g., via Tk's
        after() method). Alt state is updated incrementally by the CGEventTap
        callback, so only panic needs polling here. When a press is consumed,
        on_panic is invoked (synchronously; it should dispatch to the main
        thread if needed).

        Returns:
            True if a panic key press was consumed and on_panic fired.
        """
        with self._lock:
            if not self._panic_pending:
                return False
            self._panic_pending = False
        cb = self._on_panic
        try:
            if cb is not None:
                cb()
        except Exception as e:
            logging.error(f"CGEventTap on_panic callback error: {e}")
        return True

    def poll_alt(self) -> bool:
        """Return the current alt-held state (snapshot)."""
        with self._lock:
            return self._alt_held

    def _on_key_event(self, keycode: int, is_down: bool) -> None:
        """CGEventTap key event handler.

        Runs in the CGEventTap thread. Sets thread-safe flags for the target
        key and any tracked alt keys.
        """
        # Panic key: trigger on press (key down).
        if is_down and keycode == self._target_vk:
            with self._lock:
                self._panic_pending = True

        # Alt tracking (used for popup blacklist-on-alt). Maintain a set of
        # currently-pressed alt keys so release events for one alt while another is
        # still held do not clear the state prematurely.
        if keycode in self._alt_keys:
            with self._lock:
                if is_down:
                    self._pressed_alts.add(keycode)
                else:
                    self._pressed_alts.discard(keycode)
                new_state = bool(self._pressed_alts)
                changed = new_state != self._alt_held
                self._alt_held = new_state
            if changed and self._on_alt_change:
                self._on_alt_change(new_state)


def get_available_keys() -> list[str]:
    """Return a list of available key names for this platform."""
    return sorted(KEY_NAME_TO_VK.keys())
