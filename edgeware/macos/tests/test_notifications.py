#!/usr/bin/env python3
"""Quantitative notification test for macOS.

Measures whether Edgeware++ notifications are actually delivered to Notification
Center, using the same backend (UNUserNotificationCenter / desktop-notifier) that
features/misc.py send_notification() uses.

Metric: the number of delivered notifications in Notification Center before vs. after
sending. A successful send must increase the count by >= 1 and must not hang.

Modes:
  standalone (default):
      Send one notification via DesktopNotifierSync with the same app_name/icon
      parameters as the app, then measure the delivered-count delta.
  --app:
      Launch the bundled Edgeware++.app with notifications forced on
      (notificationChance=100) and poll Notification Center for a delivery within a
      timeout. This exercises the real in-app roll path.

A SIGALRM watchdog guards against the sync API deadlocking on the calling thread;
if it triggers, the result is reported as HANG.

Usage:
    cd edgeware && .venv/bin/python3 macos/test_notifications.py [--app] [--timeout 20]

Exit codes: 0 PASS (delivery observed), 1 FAIL (no delivery), 2 HANG / not testable.
"""

import argparse
import json
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

# rubicon is required for the low-level UNUserNotificationCenter query; it is a
# dependency of desktop-notifier, which the app already uses.
try:
    from rubicon.objc import Block, ObjCClass, py_from_ns
    from rubicon.objc.runtime import load_library, objc_id
    from Quartz import CFRunLoopRunInMode, kCFRunLoopDefaultMode

    load_library("UserNotifications")
    _UNUserNotificationCenter = ObjCClass("UNUserNotificationCenter")
except Exception as exc:  # pragma: no cover
    print(f"ERROR: cannot initialize UserNotifications bindings: {exc}")
    sys.exit(2)

APP_SUPPORT = Path.home() / "Library" / "Application Support" / "EdgewarePlusPlusMacosPython"
BUNDLE_EXE = Path(__file__).parent.parent.parent / "dist" / "Edgeware++.app" / "Contents" / "MacOS" / "Edgeware++"


def _delivered_count() -> int:
    """Return the number of delivered notifications for this process."""
    nc = _UNUserNotificationCenter.currentNotificationCenter()
    out = {"n": None}

    def handler(ns: objc_id) -> None:
        try:
            ns_list = py_from_ns(ns)
            out["n"] = len(ns_list) if ns_list is not None else 0
        except Exception as exc:  # pragma: no cover
            out["n"] = -1
            print(f"query error: {exc}")

    nc.getDeliveredNotificationsWithCompletionHandler(Block(handler))
    deadline = time.time() + 3.0
    while out["n"] is None and time.time() < deadline:
        CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.05, False)
    return out["n"] if out["n"] is not None else -1


def _authorization_status() -> str:
    """Return the authorization status string (authorized/denied/not determined)."""
    nc = _UNUserNotificationCenter.currentNotificationCenter()
    out = {"s": None}

    def handler(settings: objc_id) -> None:
        try:
            settings_obj = py_from_ns(settings)
            status = getattr(settings_obj, "authorizationStatus", None)
            names = {0: "not-determined", 1: "denied", 2: "authorized",
                     3: "provisional", 4: "ephemeral"}
            out["s"] = names.get(status, str(status))
        except Exception as exc:  # pragma: no cover
            out["s"] = f"error:{exc}"

    nc.getNotificationSettingsWithCompletionHandler(Block(handler))
    deadline = time.time() + 3.0
    while out["s"] is None and time.time() < deadline:
        CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.05, False)
    return out["s"] if out["s"] is not None else "unknown"


def _run_standalone(timeout: int) -> int:
    """Send one notification directly and measure delivered-count delta."""
    print(f"[notify] authorization status: {_authorization_status()}", flush=True)

    before = _delivered_count()
    print(f"[notify] delivered before send: {before}", flush=True)

    state = {"result": None}

    def alarm_handler(*_args):
        raise SystemExit("HANG")

    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)
    try:
        from desktop_notifier.sync import DesktopNotifierSync
        notifier = DesktopNotifierSync(app_name="Edgeware++")
        ident = notifier.send(
            title="Notification Test",
            message=f"quantitative check at {time.strftime('%H:%M:%S')}",
        )
        signal.alarm(0)
        state["result"] = ident
    except SystemExit:
        print("[notify] RESULT: HANG — send did not return in time", flush=True)
        return 2

    if state["result"] is None:
        print("[notify] send raised/failed without identifier", flush=True)
        return 1

    # Give Notification Center a moment to deliver.
    time.sleep(2.0)
    after = _delivered_count()
    print(f"[notify] delivered after send: {after}", flush=True)

    delta = (after - before) if isinstance(after, int) and isinstance(before, int) else -1
    auth = _authorization_status()
    ok = delta >= 1 and auth == "authorized"
    print(f"[notify] RESULT: delivery delta = {delta}, authorization = {auth} "
          f"({'PASS' if ok else 'FAIL'})", flush=True)
    if delta >= 1 and auth != "authorized":
        print("[notify] NOTE: scheduled but suppressed — macOS hides notifications "
              "when authorization is denied; grant permission for the app.", flush=True)
    return 0 if ok else 1


def _run_app(timeout: int) -> int:
    """Launch the bundled app with notifications forced and poll for delivery."""
    cfg_path = APP_SUPPORT / "data" / "config.json"
    backup = None
    if cfg_path.is_file():
        backup = cfg_path.with_suffix(".json.bak")
        shutil.copy2(cfg_path, backup)
    try:
        cfg = json.loads(cfg_path.read_text())
    except Exception:
        cfg = {}
    cfg.update({
        "notificationChance": 100, "promptMod": 0, "webMod": 0, "popupMod": 0,
        "audioMod": 0, "vidMod": 0, "subliminalsChance": 0,
        "corruptionMode": False, "mitosisMode": False, "singleMode": False,
        "timerMode": False, "hibernateMode": False, "fill": False,
        "replace": False, "rotateWallpaper": False, "desktopIcons": False,
        "showLoadingFlair": False, "delay": 1500,
    })
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(json.dumps(cfg))

    proc = subprocess.Popen([str(BUNDLE_EXE)],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        print(f"[app] launched bundle pid {proc.pid}", flush=True)
        time.sleep(8)  # startup + first roll
        before = _delivered_count()
        print(f"[app] delivered at start: {before}", flush=True)

        deadline = time.time() + timeout
        after = before
        while time.time() < deadline:
            if proc.poll() is not None:
                print(f"[app] app exited rc={proc.returncode}", flush=True)
                break
            current = _delivered_count()
            if current > before:
                after = current
                break
            time.sleep(1.0)

        delta = after - before
        auth = _authorization_status()
        ok = delta >= 1 and auth == "authorized"
        print(f"[app] RESULT: delivery delta = {delta}, authorization = {auth} "
              f"({'PASS' if ok else 'FAIL'})", flush=True)
        return 0 if ok else 1
    finally:
        if proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                pass
        if backup and backup.is_file():
            shutil.move(str(backup), str(cfg_path))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--app", action="store_true",
                    help="test the bundled app instead of a direct send")
    ap.add_argument("--timeout", type=int, default=20,
                    help="watchdog/roll timeout in seconds (default 20)")
    args = ap.parse_args()

    if args.app and not BUNDLE_EXE.is_file():
        print(f"[app] bundle not found: {BUNDLE_EXE}")
        print("      Rebuild with 'bash macos/build_app.sh' first.")
        return 2

    return _run_app(args.timeout) if args.app else _run_standalone(args.timeout)


if __name__ == "__main__":
    sys.exit(main())
