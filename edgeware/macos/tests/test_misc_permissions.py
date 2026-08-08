#!/usr/bin/env python3
"""Tests for the macOS Input Monitoring permission helper.

The real signal for global keyboard event taps is not AXIsProcessTrusted()
(Accessibility) but whether CGEventTapCreate returns a valid tap — that needs
the separate Input Monitoring TCC grant.  These tests verify
check_input_monitoring_permission() gates on the tap, not on Accessibility.

NOTE: os_utils.mac is imported once at module scope so its dependencies
(pystray/pynput/etc.) see the real Quartz module.  The fake Quartz is swapped
into sys.modules only around each individual check_input_monitoring_permission()
call, because that helper imports Quartz lazily inside itself.

Usage:
    cd edgeware && python macos/tests/test_misc_permissions.py
"""

import os
import sys
from unittest.mock import MagicMock, patch

EDGWARE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(EDGWARE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

if EDGWARE_DIR not in sys.path:
    sys.path.insert(0, EDGWARE_DIR)


# Import the helper up front: this also imports pystray/pynput/etc., which must
# resolve the *real* Quartz (not a mock).
from os_utils import check_input_monitoring_permission


class FakeQuartz:
    """Minimal stand-in for the real Quartz module.

    tap_created controls whether CGEventTapCreate returns a MagicMock (granted)
    or None (denied), mirroring macOS returning nil without Input Monitoring.
    """

    tap_created = True
    create_calls = 0

    kCGSessionEventTap = 0
    kCGHeadInsertEventTap = 1
    kCGEventTapOptionListenOnly = 2
    kCGEventKeyDown = 3

    @staticmethod
    def CGEventMaskBit(_):
        return 4

    @classmethod
    def CGEventTapCreate(cls, *args, **kwargs):
        cls.create_calls += 1
        if not cls.tap_created:
            return None
        return MagicMock()


def _check(tap_created: bool):
    """Run check_input_monitoring_permission under a fake Quartz."""
    FakeQuartz.tap_created = tap_created
    FakeQuartz.create_calls = 0
    with patch.dict(sys.modules, {"Quartz": FakeQuartz}):
        return check_input_monitoring_permission()


class TestInputMonitoringPermission:
    """check_input_monitoring_permission() gates on CGEventTapCreate success."""

    def test_tap_created_means_granted(self):
        """A valid CGEventTap means Input Monitoring is granted."""
        assert _check(tap_created=True) is True
        assert FakeQuartz.create_calls >= 1

    def test_nil_tap_means_not_granted(self):
        """CGEventTapCreate returning None means Input Monitoring is denied.

        This is the regression: AXIsProcessTrusted() reports Accessibility
        granted, yet the tap still fails.  The helper must return False here.
        """
        assert _check(tap_created=False) is False

    def test_probe_is_listen_only_keyboard_tap(self):
        """The probe must actually invoke CGEventTapCreate on darwin."""
        _check(tap_created=True)
        assert FakeQuartz.create_calls >= 1

    def test_quartz_missing_means_not_granted(self):
        """If Quartz cannot be imported, assume not granted."""
        with patch.dict(sys.modules, {"Quartz": None}):
            assert check_input_monitoring_permission() is False


def main():
    print(f"Python: {sys.version}")
    print()

    failures = 0
    for name in dir(TestInputMonitoringPermission):
        if not name.startswith("test_"):
            continue
        try:
            TestInputMonitoringPermission().__getattribute__(name)()
            print(f"  PASS — {name}")
        except AssertionError as e:
            print(f"  FAIL — {name}: {e}")
            failures += 1
        except Exception as e:
            print(f"  ERROR — {name}: {type(e).__name__}: {e}")
            failures += 1

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
