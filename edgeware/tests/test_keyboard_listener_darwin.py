#!/usr/bin/env python3
"""End-to-end test for the macOS CGEventTap keyboard listener.

Verifies that DarwinKeyboardListener:
1. Starts a Quartz CGEventTap (requires Accessibility permission)
2. Captures a simulated key press for the configured panic key
3. Polls pending state from the main thread
4. Tracks alt-key hold/release state (used by popup blacklist)

This mirrors the real bundled-app path: a raw in-process Quartz CGEventTap,
polled via Tk's after(). This is what actually fixes panic exit + prompt input
in the .app, unlike pynput-in-a-subprocess.

Usage:
    cd edgeware && python tests/test_keyboard_listener_darwin.py

Exit code 0 on success (or if CGEventTap cannot be created due to missing
Accessibility permission, which is reported and skipped).
"""

import os
import sys
import time

EDGWARE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(EDGWARE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


def simulate_key(vk_code: int, hold_ms: float = 60) -> None:
    """Simulate a key press+release using Quartz CGEvents."""
    import Quartz

    source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)
    key_down = Quartz.CGEventCreateKeyboardEvent(source, vk_code, True)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_down)
    time.sleep(hold_ms / 1000.0)
    key_up = Quartz.CGEventCreateKeyboardEvent(source, vk_code, False)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_up)


def test_panic_key_capture() -> None:
    """The configured panic key (esc) must be captured and pollable."""
    print("=== Test: DarwinKeyboardListener captures panic key ===")

    from features.keyboard_listener_darwin import DarwinKeyboardListener

    fired = []
    listener = DarwinKeyboardListener(target_key="Key.esc", on_panic=lambda: fired.append(True))

    assert listener.start(), "CGEventTap creation failed — Accessibility permission required"
    try:
        time.sleep(0.6)  # let the CFRunLoop spin up

        VK_ESCAPE = 0x35
        print("  Simulating ESC press (VK 0x35)...")
        simulate_key(VK_ESCAPE)

        # Poll repeatedly like the Tk after() loop does.
        deadline = time.time() + 4.0
        while time.time() < deadline:
            if listener.poll():
                break
            time.sleep(0.05)

        assert fired, "Panic key was not captured by CGEventTap"
        print("  PASS — panic key captured and polled")
    finally:
        listener.stop()


def test_alt_key_tracking() -> None:
    """Alt press/release must be reflected by poll_alt().

    macOS does not reliably dispatch a *bare* posted modifier key (Option) to
    session event taps, so we exercise the callback directly with synthetic Quartz
    events instead of relying on CGEventPost.
    """
    print("\n=== Test: DarwinKeyboardListener tracks alt key ===")

    import Quartz
    from features.keyboard_listener_darwin import DarwinKeyboardListener

    changes = []
    listener = DarwinKeyboardListener(
        target_key="Key.esc",
        on_panic=lambda: None,
        alt_keys=["Key.alt", "Key.alt_l", "Key.alt_r"],
        on_alt_change=lambda held: changes.append(held),
    )

    def synth_event(is_down: bool):
        """Build a synthetic CGEventKeyDown/Up for VK_OPTION."""
        source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)
        return Quartz.CGEventCreateKeyboardEvent(source, 0x3A, is_down)

    assert listener.start(), "CGEventTap creation failed — Accessibility permission required"
    try:
        time.sleep(0.4)

        # Press alt (key down) -> callback should set held True.
        ev = synth_event(True)
        listener._callback(None, Quartz.kCGEventKeyDown, ev, None)
        assert listener.poll_alt() is True or True in changes, (
            "Alt press was not tracked (changes=%r)" % changes
        )
        print("  PASS — alt press sets held=True")

        # Release alt (key up) -> callback should clear it.
        ev = synth_event(False)
        listener._callback(None, Quartz.kCGEventKeyUp, ev, None)
        time.sleep(0.2)
        assert not changes or changes[-1] is False, (
            "Alt release did not clear held state (changes=%r)" % changes
        )
        print("  PASS — alt release clears held state")
    finally:
        listener.stop()


def test_vk_mapping() -> None:
    """The panic key name resolves to the expected VK code."""
    print("\n=== Test: Key.esc -> VK mapping ===")
    from features.keyboard_listener_darwin import KEY_NAME_TO_VK

    assert KEY_NAME_TO_VK["Key.esc"] == 0x35, "Key.esc should map to 0x35"
    assert KEY_NAME_TO_VK["a"] == 0x00, "'a' should map to 0x00"
    print("  PASS — Key.esc -> 0x35, 'a' -> 0x00")


def main():
    print(f"Python: {sys.version}")
    print()

    results = []
    test_vk_mapping()
    results.append(("vk_mapping", True))

    # CGEventTap tests require a real display + Accessibility permission. If the
    # tap cannot be created (e.g. headless CI), report as SKIP rather than fail.
    for name, fn in [
        ("panic_key_capture", test_panic_key_capture),
        ("alt_key_tracking", test_alt_key_tracking),
    ]:
        try:
            fn()
            results.append((name, True))
        except AssertionError as e:
            print(f"  FAIL — {e}")
            results.append((name, False))
        except Exception as e:
            # Likely missing Accessibility/display; treat as environment-skip.
            print(f"  SKIP — {type(e).__name__}: {e}")
            results.append((name, "skip"))

    print("\n=== Summary ===")
    all_ok = True
    for name, ok in results:
        status = {"True": "PASS", "False": "FAIL", "skip": "SKIP"}[str(ok)]
        if ok is not True:
            all_ok = False
        print(f"  {status} — {name}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
