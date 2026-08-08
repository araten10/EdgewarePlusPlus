#!/usr/bin/env python3
"""SPIKE test: does in-process pynput reintroduce the Prompt TSM typing hang?

Confirms whether running pynput directly in the Edgeware process (Option 1) breaks
typing into the Prompt Text widget on macOS, compared to the CGEventTap default.

How it works
------------
1. Backs up and rewrites the user config so a Prompt is guaranteed to open
   (promptMod=100, all other chance-mods 0).
2. Launches Edgeware++ (in-process pynput keyboard listener is the default on
   macOS) and types into it.
3. Waits for the Prompt to appear, then posts synthetic keystrokes via Quartz
   (posting requires no permission).
4. Determines whether the text landed in the Text widget:
     - If THIS test process is Accessibility-trusted: read the widget value via AX ->
       definitive PASS/FAIL.
     - Otherwise: fall back to a responsiveness probe + prints manual steps.
5. Restores the config and terminates the app.

The TSM hang is independent of bundle-vs-source, so `--target source` gives the
same result as a rebuilt bundle without the multi-minute PyInstaller rebuild.

Usage:
    cd edgeware && .venv/bin/python3 macos/test_prompt_typing.py \
        [--target bundle|source]

Exit codes:
    0  PASS - typed text reached the Prompt widget
    1  FAIL - typed text did NOT reach the Prompt widget (hang reproduced)
    2  MANUAL - automation couldn't read the widget; follow printed instructions
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

EDGWARE_DIR = Path(__file__).parent.parent.parent   # edgeware/
SRC_DIR = EDGWARE_DIR / "src"

APP_SUPPORT = Path.home() / "Library" / "Application Support" / "EdgewarePlusPlusMacosPython"
BUNDLE_APP = EDGWARE_DIR / "dist" / "Edgeware++.app"
BUNDLE_EXE = BUNDLE_APP / "Contents" / "MacOS" / "Edgeware++"

CONFIG_PATHS = {
    "bundle": APP_SUPPORT / "data" / "config.json",
    "source": EDGWARE_DIR / "data" / "config.json",
}

PROMPT_TEXT = "hello"
VK_LETTERS = {
    "a": 0x00, "s": 0x01, "d": 0x02, "f": 0x03, "h": 0x04, "g": 0x05,
    "z": 0x06, "x": 0x07, "c": 0x08, "v": 0x09, "b": 0x0B, "q": 0x0C,
    "w": 0x0D, "e": 0x0E, "r": 0x0F, "y": 0x10, "t": 0x11, "o": 0x1F,
    "u": 0x20, "i": 0x22, "p": 0x23, "l": 0x25, "j": 0x26, "k": 0x28,
    "n": 0x2D, "m": 0x2E,
}


def forcing_config() -> dict:
    """Minimal config that guarantees exactly one Prompt at the first roll."""
    cfg = {
        # Ensure a prompt opens immediately and is accepted on any submit.
        "promptMod": 100,
        "promptMistakes": 9999,
        # Silence every other random event so only the Prompt appears.
        "webMod": 0, "popupMod": 0, "audioMod": 0, "vidMod": 0,
        "subliminalsChance": 0, "notificationChance": 0, "denialChance": 0,
        "corruptionMode": False, "mitosisMode": False, "singleMode": False,
        "timerMode": False, "hibernateMode": False, "startupSplash": False,
        # Non-destructive safety: never touch the drive/desktop.
        "fill": False, "replace": False, "rotateWallpaper": False,
        "desktopIcons": False, "showLoadingFlair": False,
        # Faster first roll so the test doesn't wait forever.
        "delay": 1000,
    }
    return cfg


def write_forcing_config(target: str) -> Path:
    """Back up any existing config and replace it with the forcing config."""
    path = CONFIG_PATHS[target]
    backup = None
    if path.is_file():
        backup = path.with_suffix(".json.bak")
        shutil.copy2(path, backup)

    cfg = {}
    if path.is_file():
        try:
            cfg = json.loads(path.read_text())
        except Exception:
            cfg = {}
    cfg.update(forcing_config())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg))
    print(f"[cfg] wrote forcing config -> {path}", flush=True)
    return backup


def restore_config(backup: Path | None, target_path: Path) -> None:
    if backup is None or not backup.is_file():
        return
    try:
        shutil.move(str(backup), str(target_path))
        print("[cfg] restored original config", flush=True)
    except Exception as e:
        print(f"[cfg] restore failed (non-fatal): {e}", flush=True)


def launch_app(target: str) -> subprocess.Popen:
    if target == "bundle":
        print(f"[launch] starting bundle {BUNDLE_EXE}", flush=True)
        return subprocess.Popen([str(BUNDLE_EXE)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[launch] starting source app", flush=True)
    return subprocess.Popen(
        [sys.executable, "main_edgeware.py"],
        cwd=str(SRC_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def post_text(text: str) -> None:
    """Post each character via Quartz CGEventPost (no permission needed to post)."""
    import Quartz

    source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)
    for ch in text:
        vk = VK_LETTERS.get(ch.lower())
        if vk is None:
            continue
        down = Quartz.CGEventCreateKeyboardEvent(source, vk, True)
        up = Quartz.CGEventCreateKeyboardEvent(source, vk, False)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, down)
        time.sleep(0.05)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, up)
        time.sleep(0.08)
    print(f"[type] posted {len([c for c in text if VK_LETTERS.get(c.lower())])} chars", flush=True)


def ax_read_prompt_text() -> str | None:
    """Read the frontmost Prompt's Text widget via AX; None if not permitted."""
    try:
        import ApplicationServices as AS
        import Quartz
    except (ImportError, AttributeError):
        return None
    try:
        if not AS.AXIsProcessTrusted():
            print("[ax] this test process is NOT Accessibility-trusted — skipping widget read", flush=True)
            return None

        # Find the first text field across all windows of the frontmost app.
        apps = Quartz.NSWorkspace.sharedWorkspace().runningApplications()
        target = None
        for app in apps:
            if "Edgeware" in str(app.localizedName() or ""):
                target = app
                break
        if target is None:
            return None

        ax_app = AS.AXUIElementCreateApplication(target.processIdentifier())
        err, children = AS.AXUIElementCopyAttributeValue(ax_app, AS.kAXWindowsAttribute, None)
        if err != AS.kAXErrorSuccess:
            return None
        try:
            windows = list(children)
        except TypeError:
            return None

        text = ""
        for win in windows:
            found = _ax_search_text(win)
            if found is not None:
                text = found
                break
        print(f"[ax] read prompt text: {text!r}", flush=True)
        return text
    except Exception as e:
        print(f"[ax] AX read failed ({type(e).__name__}: {e}) — skipping widget read", flush=True)
        return None


def _ax_search_text(element: object) -> str | None:
    import ApplicationServices as AS

    try:
        err, role = AS.AXUIElementCopyAttributeValue(element, AS.kAXRoleAttribute, None)
        if err != AS.kAXErrorSuccess:
            return None
        role_name = str(role)
        if role_name == "AXTextArea":
            value_err, value = AS.AXUIElementCopyAttributeValue(element, AS.kAXValueAttribute, None)
            if value_err == AS.kAXErrorSuccess and value is not None:
                return str(value)
        err, children = AS.AXUIElementCopyAttributeValue(element, AS.kAXChildrenAttribute, None)
        if err != AS.kAXErrorSuccess:
            return None
        try:
            kids = list(children)
        except TypeError:
            return None
        for child in kids:
            r = _ax_search_text(child)
            if r is not None:
                return r
    except Exception:
        pass
    return None


def wait_and_type(proc: subprocess.Popen) -> str | None:
    """Wait for the app to reach steady state, post keys, then read widget (or None)."""
    print("[wait] waiting ~8s for app startup + first Prompt roll...", flush=True)
    time.sleep(8)

    if proc.poll() is not None:
        print(f"[app] exited early with code {proc.returncode}", flush=True)
        return "exited"

    post_text(PROMPT_TEXT)
    # Give the (possibly hung) TSM path time to process before reading.
    time.sleep(2)
    # A SIGTRAP/SIGABRT crash may fire only when key events arrive, so check
    # whether the app died while typing.
    if proc.poll() is not None:
        print(f"[app] exited during typing with code {proc.returncode}", flush=True)
        return f"exited:{proc.returncode}"
    text = ax_read_prompt_text()
    return text


def is_responsive(proc: subprocess.Popen) -> bool:
    """SIGTERM then check it exits; if it ignores SIGTERM, the main loop is stuck."""
    print("[resp] probing responsiveness via SIGTERM...", flush=True)
    try:
        proc.terminate()
    except Exception:
        return False
    try:
        proc.wait(timeout=5)
        print("[resp] app exited cleanly on SIGTERM -> responsive", flush=True)
        return True
    except subprocess.TimeoutExpired:
        print("[resp] app did NOT exit on SIGTERM within 5s -> main loop hung", flush=True)
        try:
            proc.kill()
        except Exception:
            pass
        return False


def manual_instructions() -> None:
    print("\n" + "=" * 62)
    print("MANUAL VERIFICATION REQUIRED")
    print("=" * 62)
    print("Automated widget read needs Accessibility permission, which this test lacks.")
    print("The app is running with the in-process pynput keyboard listener.")
    print("A Prompt window should be open and 'hello' has been typed into it.")
    print()
    print("1. Look at the Prompt's text box.")
    print("   - If 'hello' appears (typing works)  -> PASS  (no hang)")
    print("   - If nothing appears or typing hangs    -> FAIL  (TSM hang reproduced)")
    print("2. Press ESC (panic key).")
    print("   - Panic should trigger and the app exits.")
    print()
    print("When done, press Enter here to clean up.")
    print("=" * 62)
    try:
        input()
    except EOFError:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["bundle", "source"], default="source")
    args = parser.parse_args()

    if args.target == "bundle" and not BUNDLE_EXE.is_file():
        print(f"[error] bundle not found: {BUNDLE_APP}")
        print("  Rebuild with 'bash macos/build_app.sh' after editing misc.py,")
        print("  or use --target source (identical in-process behavior).")
        return 2

    backup = write_forcing_config(args.target)

    proc = launch_app(args.target)
    code = 2  # default: needs manual
    try:
        time.sleep(1)  # let the subprocess fully spawn
        result = wait_and_type(proc)

        if result == "exited":
            code = 1
        elif isinstance(result, str) and result.startswith("exited:"):
            rc = int(result.split(":", 1)[1])
            crashed = rc < 0  # negative returncode -> killed by a signal (SIGTRAP/SIGABRT)
            print(f"\n[result] {'FAIL' if crashed else 'PASS'} - app exited during typing with code {rc} ({'signal crash' if crashed else ''})")
            code = 1 if crashed else 0
        elif result is not None and isinstance(result, str):
            # AX gave a definitive read.
            landed = PROMPT_TEXT in result
            print(f"\n[result] {'PASS' if landed else 'FAIL'} - typed text {'landed' if landed else 'DID NOT land'}")
            code = 0 if landed else 1
        else:
            manual_instructions()

        # Final responsiveness probe as a secondary hang signal.
        responsive = is_responsive(proc)
        print(f"[result] responsiveness: {'responsive' if responsive else 'HUNG'}")
        if code != 2 and not responsive:
            print("NOTE: app did not exit on SIGTERM - main loop may be stuck.")
    finally:
        if proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass
        restore_config(backup, CONFIG_PATHS[args.target])

    return code


if __name__ == "__main__":
    sys.exit(main())
