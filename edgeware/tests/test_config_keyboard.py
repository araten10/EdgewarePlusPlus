#!/usr/bin/env python3
"""Full round-trip test for the config app keyboard listener.

Tests that:
1. The CGEventTap keyboard listener captures key events (macOS)
   or the pynput subprocess starts and sends "focus" (other platforms)
2. A simulated key press is received
3. The key value can be written to and read from config JSON

Usage:
    cd edgeware && python tests/test_config_keyboard.py
"""

import json
import os
import sys
import tempfile
import threading
import time

EDGWARE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(EDGWARE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


def simulate_key_press(vk_code: int) -> None:
    """Simulate a key press+release using Quartz CGEvents."""
    import Quartz

    source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)
    key_down = Quartz.CGEventCreateKeyboardEvent(source, vk_code, True)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_down)
    time.sleep(0.1)
    key_up = Quartz.CGEventCreateKeyboardEvent(source, vk_code, False)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_up)


def test_cg_event_tap_listener():
    """Test that the CGEventTap keyboard listener captures key events."""
    print("=== Test: CGEventTap keyboard listener ===")

    import Quartz

    captured = {"key": None}
    tap_ref = [None]
    loop_ref = [None]

    def callback(proxy, event_type, event, refcon):
        if event_type == Quartz.kCGEventTapDisabledByTimeout:
            Quartz.CGEventTapEnable(tap_ref[0], True)
            return event
        if event_type == Quartz.kCGEventKeyDown:
            keycode = Quartz.CGEventGetIntegerValueField(
                event, Quartz.kCGKeyboardEventKeycode
            )
            from config.window.utils import _vk_to_key_name
            key_name = _vk_to_key_name(keycode)
            if key_name is not None:
                captured["key"] = key_name
        return event

    tap_obj = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,
        Quartz.kCGHeadInsertEventTap,
        Quartz.kCGEventTapOptionListenOnly,
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown),
        callback,
        None,
    )
    assert tap_obj is not None, "CGEventTap creation failed — Accessibility permission required"
    tap_ref[0] = tap_obj

    run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap_obj, 0)

    def run_loop():
        loop = Quartz.CFRunLoopGetCurrent()
        loop_ref[0] = loop
        Quartz.CFRunLoopAddSource(loop, run_loop_source, Quartz.kCFRunLoopCommonModes)
        Quartz.CGEventTapEnable(tap_obj, True)
        Quartz.CFRunLoopRun()

    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()
    time.sleep(0.3)

    VK_SPACE = 0x31
    print(f"  Simulating key press (VK 0x{VK_SPACE:02X})...")
    simulate_key_press(VK_SPACE)
    time.sleep(0.5)

    Quartz.CGEventTapEnable(tap_obj, False)
    if loop_ref[0] is not None:
        Quartz.CFRunLoopStop(loop_ref[0])

    key = captured["key"]
    assert key is not None, "No key captured by CGEventTap"
    print(f"  Captured key: {key!r}")
    print(f"  PASS — CGEventTap captured key: {key}")
    return key


def test_subprocess_keyboard_listener():
    """Test that the pynput keyboard listener subprocess starts and receives keys."""
    print("=== Test: pynput keyboard listener subprocess ===")

    import multiprocessing
    from config.window.utils import _config_keyboard_listener

    ctx = multiprocessing.get_context("spawn")
    parent_conn, child_conn = ctx.Pipe()
    process = ctx.Process(target=_config_keyboard_listener, args=(child_conn,), daemon=True)
    process.start()
    child_conn.close()

    print(f"  Subprocess started (PID {process.pid})")

    parent_conn.poll(timeout=5)
    msg = parent_conn.recv()
    assert msg == "focus", f"Expected 'focus', got {msg!r}"
    print("  Received 'focus' — subprocess is running")

    VK_SPACE = 0x31
    print(f"  Simulating key press (VK 0x{VK_SPACE:02X})...")
    simulate_key_press(VK_SPACE)

    parent_conn.poll(timeout=5)
    key = parent_conn.recv()
    print(f"  Received key: {key!r}")

    assert isinstance(key, str) and len(key) > 0

    process.terminate()
    process.join(timeout=2)
    if process.is_alive():
        process.kill()
        process.join(timeout=1)
    parent_conn.close()

    print(f"  PASS — subprocess started and received key: {key}")
    return key


def test_config_json_round_trip(key_name: str):
    """Test writing the key to config JSON and reading it back."""
    print("\n=== Test: Config JSON round-trip ===")

    config_path = os.path.join(tempfile.mkdtemp(), "test_config.json")
    try:
        config = {"globalPanicKey": key_name}
        with open(config_path, "w") as f:
            json.dump(config, f)
        print(f"  Wrote config: {config}")

        with open(config_path) as f:
            loaded = json.load(f)
        assert loaded["globalPanicKey"] == key_name, (
            f"Round-trip failed: wrote {key_name!r}, read {loaded['globalPanicKey']!r}"
        )
        print(f"  Read back: {loaded}")
        print(f"  PASS — round-trip succeeded")
    finally:
        os.unlink(config_path)


def test_key_to_vk_mapping():
    """Test that VK codes map to key names correctly."""
    print("\n=== Test: VK code to key name mapping ===")

    from config.window.utils import _vk_to_key_name

    cases = [
        (0x31, "Key.space"),
        (0x35, "Key.esc"),
        (0x00, "a"),
        (0x12, "1"),
    ]
    for vk, expected in cases:
        result = _vk_to_key_name(vk)
        assert result == expected, f"VK 0x{vk:02X}: expected {expected!r}, got {result!r}"
        print(f"  VK 0x{vk:02X} -> {result!r} ✓")

    print("  PASS — VK mapping works")


def main():
    print(f"Python: {sys.version}")
    print(f"Working dir: {os.getcwd()}")
    print(f"Source dir: {SRC_DIR}")
    print()

    results = []

    try:
        test_key_to_vk_mapping()
        results.append(("vk_mapping", True))
    except Exception as e:
        print(f"  FAIL — {e}")
        results.append(("vk_mapping", False))

    if sys.platform == "darwin":
        try:
            key = test_cg_event_tap_listener()
            results.append(("cg_event_tap", True))
        except Exception as e:
            print(f"  FAIL — {e}")
            import traceback
            traceback.print_exc()
            results.append(("cg_event_tap", False))
            key = None

        try:
            test_config_json_round_trip(key or "Key.space")
            results.append(("config_round_trip", True))
        except Exception as e:
            print(f"  FAIL — {e}")
            results.append(("config_round_trip", False))
    else:
        try:
            key = test_subprocess_keyboard_listener()
            results.append(("subprocess_listener", True))
        except Exception as e:
            print(f"  FAIL — {e}")
            import traceback
            traceback.print_exc()
            results.append(("subprocess_listener", False))
            key = None

        try:
            test_config_json_round_trip(key or "Key.space")
            results.append(("config_round_trip", True))
        except Exception as e:
            print(f"  FAIL — {e}")
            results.append(("config_round_trip", False))

    print("\n=== Summary ===")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'} — {name}")
    print(f"\n{passed}/{total} tests passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
