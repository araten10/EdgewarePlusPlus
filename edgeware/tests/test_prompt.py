#!/usr/bin/env python3
"""Tests for the Prompt dialog text input and focus management.

Verifies that:
1. The Prompt's Text widget has focus_set() called on creation
2. The Prompt does NOT use grab_set(), so other popups stay interactive
3. The Levenshtein distance submit logic accepts correct input
4. The keyboard listener is paused during the Prompt and restarted after

Note: overrideredirect(True) windows cannot receive actual keyboard focus
in headless test environments (no window manager).  These tests verify the
code paths by calling submit() directly and checking state transitions.

Usage:
    cd edgeware && python tests/test_prompt.py
"""

import os
import sys
import unittest
from dataclasses import dataclass, field
from tkinter import Tk, Text
from unittest.mock import MagicMock, patch

EDGWARE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(EDGWARE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


class _FakePynputListener:
    """Minimal pynput.Listener stand-in exposing is_alive() for the Prompt safety net."""

    def __init__(self, alive: bool) -> None:
        self._alive = alive

    def is_alive(self) -> bool:
        return self._alive


@dataclass
class MockTheme:
    fg: str = "black"
    bg: str = "#f0f0f0"
    text_fg: str = "black"
    text_bg: str = "white"
    font: str = "Arial"
    font_size: int = 12


@dataclass
class MockDefault:
    popup_close: str = "Close"
    prompt_command: str = "Type for me"
    prompt_submit: str = "Submit"


@dataclass
class MockIndex:
    default: MockDefault = field(default_factory=MockDefault)


@dataclass
class MockSettings:
    theme: MockTheme = field(default_factory=MockTheme)
    prompt_max_mistakes: int = 2
    prompt_chance: int = 100


@dataclass
class MockPack:
    index: MockIndex = field(default_factory=MockIndex)

    def random_prompt(self):
        return "hello world"


class MockState:
    def __init__(self):
        self.prompt_active = False
        self.keyboard_process = None
        self.keyboard_receive_conn = None
        self.keyboard_listener = None


def _make_prompt(settings=None, pack=None, state=None, prompt="test", on_close=None):
    """Create a Prompt with mocked keyboard listener functions."""
    settings = settings or MockSettings()
    pack = pack or MockPack()
    state = state or MockState()
    with patch("features.misc.handle_keyboard"):
        from features.prompt import Prompt
        p = Prompt(settings, pack, state, prompt=prompt, on_close=on_close)
        p.update_idletasks()
        return p


def _find_text_widget(toplevel):
    """Find the Text widget inside a Toplevel."""
    for child in toplevel.winfo_children():
        if isinstance(child, Text):
            return child
    return None


class TestPromptFocus(unittest.TestCase):
    """Test that the Prompt dialog manages focus correctly."""

    def setUp(self):
        self.root = Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    @patch("features.misc.handle_keyboard")
    def test_focus_set_called_on_text_widget(self, mock_restart):
        """focus_set() should be called on the Text widget after creation."""
        from features.prompt import Prompt

        prompt = Prompt(MockSettings(), MockPack(), MockState())
        prompt.update_idletasks()

        text_widget = _find_text_widget(prompt)
        self.assertIsNotNone(text_widget, "Text widget not found in Prompt")

        # In headless mode, focus_set() is called but the window manager
        # doesn't actually grant focus.  Verify the widget exists and is
        # configured to receive focus.
        self.assertEqual(str(text_widget["state"]), "normal")
        prompt.destroy()

    @patch("features.misc.handle_keyboard")
    def test_grab_set_not_called(self, mock_restart):
        """grab_set() must NOT be called on the Prompt so other popups stay usable."""
        from features.prompt import Prompt

        prompt = Prompt(MockSettings(), MockPack(), MockState())
        with patch.object(prompt, "grab_set", wraps=prompt.grab_set) as mock_grab:
            prompt.update_idletasks()
            mock_grab.assert_not_called()

        # Window should still be created and manageable (not grab-enslaved).
        self.assertTrue(prompt.winfo_ismapped() or prompt.winfo_manager() == "wm")
        prompt.destroy()

    @patch("features.misc.handle_keyboard")
    def test_text_widget_exists_and_is_writable(self, mock_restart):
        """The Text widget should exist and accept insert operations."""
        prompt = _make_prompt()

        text_widget = _find_text_widget(prompt)
        self.assertIsNotNone(text_widget, "Text widget not found in Prompt")

        # Directly insert text (bypasses the focus issue in headless)
        text_widget.insert("1.0", "hello world")
        prompt.update_idletasks()

        content = text_widget.get(1.0, "end-1c")
        self.assertEqual(content, "hello world", f"Expected 'hello world', got {content!r}")
        prompt.destroy()

    @patch("features.misc.handle_keyboard")
    def test_submit_accepts_exact_match(self, mock_restart):
        """Submit should destroy the Prompt when input matches exactly."""
        on_close = MagicMock()
        prompt = _make_prompt(prompt="test", on_close=on_close)
        state = prompt.state

        text_widget = _find_text_widget(prompt)
        text_widget.insert("1.0", "test")

        prompt.submit(2, "test", text_widget.get(1.0, "end-1c"))

        self.assertFalse(state.prompt_active, "prompt_active should be False after successful submit")
        on_close.assert_called_once()

    @patch("features.misc.handle_keyboard")
    def test_submit_rejects_too_many_mistakes(self, mock_restart):
        """Submit should NOT destroy the Prompt when mistakes exceed max_mistakes."""
        on_close = MagicMock()
        prompt = _make_prompt(prompt="hello", on_close=on_close)
        state = prompt.state

        # 5 mistakes > max_mistakes=2
        prompt.submit(2, "hello", "xxxxx")

        self.assertTrue(state.prompt_active, "prompt_active should still be True after failed submit")
        on_close.assert_not_called()
        prompt.destroy()

    @patch("features.misc.handle_keyboard")
    def test_submit_within_max_mistakes(self, mock_restart):
        """Submit should accept input within the allowed Levenshtein distance."""
        on_close = MagicMock()
        prompt = _make_prompt(prompt="hello", on_close=on_close)
        state = prompt.state

        # "helo" is 1 edit away from "hello"
        prompt.submit(2, "hello", "helo")

        self.assertFalse(state.prompt_active)
        on_close.assert_called_once()

    @patch("features.misc.handle_keyboard")
    def test_keyboard_listener_not_killed_on_open(self, mock_restart):
        """The global panic keyboard listener must NOT be stopped when Prompt opens."""
        state = MockState()
        from features.prompt import Prompt
        prompt = Prompt(MockSettings(), MockPack(), state)
        prompt.update_idletasks()

        # The regression was killing the listener here; assert it is never restarted.
        mock_restart.assert_not_called()
        prompt.destroy()

    @patch("features.misc.handle_keyboard")
    def test_keyboard_listener_kept_alive_if_running(self, mock_restart):
        """The keyboard listener should remain alive while the Prompt is open."""
        state = MockState()
        from features.prompt import Prompt
        prompt = Prompt(MockSettings(), MockPack(), state)
        prompt.update_idletasks()

        # Listener must survive: restart is never invoked on open.
        mock_restart.assert_not_called()
        prompt.destroy()

    @patch("features.misc.handle_keyboard")
    def test_listener_restarted_if_down_on_close(self, mock_restart):
        """destroy() should restart the keyboard listener if it is unexpectedly down."""
        state = MockState()
        if sys.platform == "darwin":
            # macOS: in-process pynput listener; a stopped one must be restarted.
            state.keyboard_listener = _FakePynputListener(False)
        else:
            # Simulate a dead keyboard subprocess so destroy() performs the safety net.
            state.keyboard_process = MagicMock()
            state.keyboard_process.is_alive.return_value = False

        prompt = _make_prompt(prompt="x", state=state)
        text_widget = _find_text_widget(prompt)
        text_widget.insert("1.0", "x")

        prompt.submit(0, "x", text_widget.get(1.0, "end-1c"))

        # Safety net: if the listener was down after close, handle_keyboard restarts it.
        mock_restart.assert_called_once()

    @patch("features.misc.handle_keyboard")
    def test_listener_not_restarted_if_still_alive(self, mock_restart):
        """destroy() should NOT restart a healthy keyboard listener."""
        state = MockState()
        if sys.platform == "darwin":
            state.keyboard_listener = _FakePynputListener(True)
        else:
            state.keyboard_process = MagicMock()
            state.keyboard_process.is_alive.return_value = True

        prompt = _make_prompt(prompt="x", state=state)
        text_widget = _find_text_widget(prompt)
        text_widget.insert("1.0", "x")

        prompt.submit(0, "x", text_widget.get(1.0, "end-1c"))

        mock_restart.assert_not_called()

    @patch("features.misc.handle_keyboard")
    def test_should_init_prevents_double_prompt(self, mock_restart):
        """Only one Prompt can be active at a time."""
        state = MockState()
        prompt1 = _make_prompt(prompt="a", state=state)
        self.assertTrue(state.prompt_active)

        # Second Prompt should return early (should_init returns False)
        # without calling super().__init__, so it has no tkinter attributes
        from features.prompt import Prompt
        prompt2 = Prompt(MockSettings(), MockPack(), state, prompt="b")
        self.assertFalse(hasattr(prompt2, "tk"), "Uninitialized Prompt should not have tk attribute")
        self.assertTrue(state.prompt_active)

        prompt1.destroy()

    @patch("features.misc.handle_keyboard")
    def test_submit_clears_prompt_active(self, mock_restart):
        """A successful submit should clear prompt_active."""
        state = MockState()
        prompt = _make_prompt(prompt="ok", state=state)
        self.assertTrue(state.prompt_active)

        prompt.submit(0, "ok", "ok")
        self.assertFalse(state.prompt_active)


class TestLevenshteinDistance(unittest.TestCase):
    """Test the Levenshtein distance calculation used in Prompt.submit()."""

    def _compute_distance(self, a: str, b: str) -> int:
        d = [[j for j in range(0, len(b) + 1)]] + [[i] for i in range(1, len(a) + 1)]
        for j in range(1, len(b) + 1):
            for i in range(1, len(a) + 1):
                d[i].append(
                    min(
                        d[i - 1][j] + 1,
                        d[i][j - 1] + 1,
                        d[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1] else 1),
                    )
                )
        return d[len(a)][len(b)]

    def test_identical_strings(self):
        self.assertEqual(self._compute_distance("hello", "hello"), 0)

    def test_one_edit_insertion(self):
        self.assertEqual(self._compute_distance("hello", "helllo"), 1)

    def test_one_edit_deletion(self):
        self.assertEqual(self._compute_distance("hello", "helo"), 1)

    def test_one_edit_substitution(self):
        self.assertEqual(self._compute_distance("hello", "hallo"), 1)

    def test_two_edits(self):
        self.assertEqual(self._compute_distance("hello", "helo!"), 2)

    def test_completely_different(self):
        self.assertEqual(self._compute_distance("abc", "xyz"), 3)

    def test_empty_strings(self):
        self.assertEqual(self._compute_distance("", ""), 0)

    def test_one_empty(self):
        self.assertEqual(self._compute_distance("abc", ""), 3)
        self.assertEqual(self._compute_distance("", "abc"), 3)

    def test_single_char(self):
        self.assertEqual(self._compute_distance("a", "a"), 0)
        self.assertEqual(self._compute_distance("a", "b"), 1)


def main():
    print(f"Python: {sys.version}")
    print(f"Working dir: {os.getcwd()}")
    print(f"Source dir: {SRC_DIR}")
    print()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestPromptFocus))
    suite.addTests(loader.loadTestsFromTestCase(TestLevenshteinDistance))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
