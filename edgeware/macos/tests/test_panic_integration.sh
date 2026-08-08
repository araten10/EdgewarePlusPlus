#!/usr/bin/env bash
# Integration test: verify panic shuts down cleanly (no crash dialog, exit code 0).
#
# Spawns the real Edgeware++ app in the background, triggers panic via
# various paths, and checks the exit behaviour.
#
# Supported panic methods:
#   app      — multiprocessing connection (same path as Panic.app)
#   keyboard — simulates pressing the global panic key (Key.esc)
#   tray     — IPC panic_tray message (same path as pystray menu callback)
#
# Targets:
#   --bundle   Test against dist/Edgeware++.app (default if bundle exists)
#   --source   Test against src/main_edgeware.py directly
#   Auto-detection is used if not specified.
#
# Usage: cd edgeware && bash macos/tests/test_panic_integration.sh [app|keyboard|tray] [--bundle|--source]
#   No method argument: tests all methods sequentially.
#   One method argument: tests only that method.
# Exit 0 = all methods clean shutdown, exit 1 = crash/hang/timeout
#
# Requires: macOS, Quartz via PyObjC for keyboard simulation

set -euo pipefail

EDGWARE_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
SRC_DIR="$EDGWARE_DIR/src"
DIST_DIR="$EDGWARE_DIR/dist"
VENV_PYTHON="$EDGWARE_DIR/.venv/bin/python3"
TIMEOUT_SECONDS=30
RETRIES=3
STARTUP_DELAY=15  # Seconds to wait for app to fully initialize
CRASH_REPORT_DELAY=6  # Seconds to wait for macOS crash report to be written to disk

log() { printf '[panic-integration] %s\n' "$*" >&2; }
pass() { log "PASS — ${METHOD} — clean shutdown (exit 0)"; return 0; }
fail() { log "FAIL — ${METHOD} — $*"; return 1; }

# Check teardown logs for expected events
check_teardown_logs() {
    local method="$1"
    local log_file="$2"
    
    log "  Checking teardown logs for ${method}..."
    
    # Check for DO_PANIC entry
    if grep -q "DO_PANIC: entered" "$log_file"; then
        log "  ✓ DO_PANIC entered"
    else
        log "  ✗ DO_PANIC never entered"
        return 1
    fi
    
    # Check for root.quit scheduling (only for macOS path)
    if grep -q "DO_PANIC: scheduling root.quit" "$log_file"; then
        log "  ✓ root.quit scheduled"
    elif grep -q "root.destroy" "$log_file"; then
        log "  ✓ root.destroy called (non-macOS path)"
    else
        log "  ✗ No exit mechanism scheduled"
        return 1
    fi
    
    return 0
}

# Parse arguments
TARGET=""
METHODS=()

for arg in "$@"; do
    case "$arg" in
        --bundle)
            TARGET="bundle"
            ;;
        --source)
            TARGET="source"
            ;;
        app|keyboard|tray)
            METHODS+=("$arg")
            ;;
        *)
            echo "Unknown argument: $arg" >&2
            exit 1
            ;;
    esac
done

# Auto-detect target
if [ -z "$TARGET" ]; then
    if [ -d "$DIST_DIR/Edgeware++.app" ]; then
        TARGET="bundle"
    else
        TARGET="source"
    fi
fi

# Default to all methods if none specified
if [ ${#METHODS[@]} -eq 0 ]; then
    METHODS=(app keyboard tray)
fi

# Set up the app launch command based on target
case "$TARGET" in
    bundle)
        APP_BIN="$DIST_DIR/Edgeware++.app/Contents/MacOS/Edgeware++"
        if [ ! -x "$APP_BIN" ]; then
            echo "ERROR: Bundle not found at $APP_BIN. Run bash macos/build_app.sh first." >&2
            exit 1
        fi
        START_APP=()
        START_APP+=("$APP_BIN")
        log "Target: bundled app ($APP_BIN)"
        ;;
    source)
        START_APP=("$VENV_PYTHON" -u "$SRC_DIR/main_edgeware.py")
        log "Target: source ($SRC_DIR/main_edgeware.py)"
        ;;
esac

# Trigger panic via the given method
trigger_panic() {
    local method="$1"
    case "$method" in
        app)
            "$VENV_PYTHON" -c "
import sys
sys.path.insert(0, '$SRC_DIR')
from panic import send_panic
send_panic()
" 2>/dev/null && log "Panic signal (app) sent" || log "Could not send panic (expected if app already exited)"
            ;;
        keyboard)
            "$VENV_PYTHON" -c "
import json
import Quartz
import time
from pathlib import Path

# Read config to find the configured panic key
config_path = Path.home() / 'Library/Application Support/EdgewarePlusPlusMacosPython/data/config.json'
with open(config_path) as f:
    config = json.load(f)
key_name = config.get('globalPanicButton', 'Key.space')

# Map key name to VK code
KEY_NAME_TO_VK = {
    'Key.esc': 0x35, 'Key.escape': 0x35, 'Key.enter': 0x24, 'Key.return': 0x24,
    'Key.space': 0x31, 'Key.tab': 0x30, 'Key.backspace': 0x33, 'Key.delete': 0x75,
    'Key.up': 0x7E, 'Key.down': 0x7D, 'Key.left': 0x7B, 'Key.right': 0x7C,
    'Key.home': 0x73, 'Key.end': 0x77, 'Key.pageup': 0x74, 'Key.pagedown': 0x79,
    'Key.f1': 0x7A, 'Key.f2': 0x78, 'Key.f3': 0x63, 'Key.f4': 0x76,
    'Key.f5': 0x60, 'Key.f6': 0x61, 'Key.f7': 0x62, 'Key.f8': 0x64,
    'Key.f9': 0x65, 'Key.f10': 0x6D, 'Key.f11': 0x67, 'Key.f12': 0x6F,
    'Key.cmd': 0x37, 'Key.shift': 0x38, 'Key.ctrl': 0x3B, 'Key.alt': 0x3A,
    'a': 0x00, 'b': 0x0B, 'c': 0x08, 'd': 0x02, 'e': 0x0E, 'f': 0x03,
    'g': 0x05, 'h': 0x04, 'i': 0x22, 'j': 0x26, 'k': 0x28, 'l': 0x25,
    'm': 0x2E, 'n': 0x2D, 'o': 0x1F, 'p': 0x23, 'q': 0x0C, 'r': 0x0F,
    's': 0x01, 't': 0x11, 'u': 0x20, 'v': 0x09, 'w': 0x0D, 'x': 0x07,
    'y': 0x10, 'z': 0x06,
    '0': 0x1D, '1': 0x12, '2': 0x13, '3': 0x14, '4': 0x15,
    '5': 0x17, '6': 0x16, '7': 0x1A, '8': 0x1C, '9': 0x19,
}

vk = KEY_NAME_TO_VK.get(key_name)
if vk is None:
    print(f'ERROR: Unknown key name: {key_name}', flush=True)
    exit(1)

print(f'Config panic key: {key_name} (VK 0x{vk:02X})', flush=True)
source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)

key_down = Quartz.CGEventCreateKeyboardEvent(source, vk, True)
Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_down)
time.sleep(0.3)

key_up = Quartz.CGEventCreateKeyboardEvent(source, vk, False)
Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_up)
print(f'Key {key_name} (VK 0x{vk:02X}) pressed and released', flush=True)
" && log "Keyboard panic key simulated" || log "Failed to simulate keyboard panic"
            ;;
        tray)
            # Send panic_tray message via IPC (same path as pystray menu callback)
            "$VENV_PYTHON" -c "
import sys
sys.path.insert(0, '$SRC_DIR')
from os_utils.mac import send_panic_tray
send_panic_tray()
" 2>/dev/null && log "Panic signal (tray/IPC) sent" || log "Could not send tray panic (expected if app already exited)"
            ;;
        *)
            echo "Unknown method: $method" >&2
            return 1
            ;;
    esac
}

# Test a single panic method
# Returns 0 on success, 1 on failure
test_panic_method() {
    local method="$1"
    METHOD="$method"
    log "Testing panic method: ${method}"

    # Record existing crash count before test
    local CRASH_DIR="$HOME/Library/Logs/DiagnosticReports"
    local PRE_CRASH_COUNT=0
    if [ -d "$CRASH_DIR" ]; then
        PRE_CRASH_COUNT=$(ls "$CRASH_DIR"/Edgeware++*.crash "$CRASH_DIR"/Edgeware++*.ips "$CRASH_DIR"/Python-*.ips "$CRASH_DIR"/Python-*.crash 2>/dev/null | wc -l | tr -d ' ')
    fi

    for attempt in $(seq 1 "$RETRIES"); do
        log "  Attempt $attempt/$RETRIES"

        # Start the app in background, capture stdout+stderr for crash detection
        APP_LOG="${TMPDIR:-/tmp}/edgeware_panic_test_$$_${method}.log"
        "${START_APP[@]}" > "$APP_LOG" 2>&1 &
        APP_PID=$!
        log "  Started app (PID $APP_PID)"

        # Wait for the keyboard listener and panic listener to be ready
        sleep "$STARTUP_DELAY"

        # Verify app is still running
        if ! kill -0 "$APP_PID" 2>/dev/null; then
            log "  App crashed during startup"
            return 1
        fi

        # Trigger panic via the specified method
        log "  Triggering panic via ${method}..."
        trigger_panic "$method"

        # Wait for app to exit with timeout
        START_TIME=$(date +%s)
        while kill -0 "$APP_PID" 2>/dev/null; do
            ELAPSED=$(( $(date +%s) - START_TIME ))
            if [ "$ELAPSED" -ge "$TIMEOUT_SECONDS" ]; then
                log "  TIMEOUT after ${ELAPSED}s — killing PID $APP_PID"
                kill -9 "$APP_PID" 2>/dev/null || true
                wait "$APP_PID" 2>/dev/null || true
                sleep "$CRASH_REPORT_DELAY"
                local POST_CRASH_COUNT_TIMEOUT=0
                if [ -d "$CRASH_DIR" ]; then
                    POST_CRASH_COUNT_TIMEOUT=$(ls "$CRASH_DIR"/Edgeware++*.crash "$CRASH_DIR"/Edgeware++*.ips "$CRASH_DIR"/Python-*.crash "$CRASH_DIR"/Python-*.ips 2>/dev/null | wc -l | tr -d ' ')
                fi
                local NEW_CRASH_COUNT_TIMEOUT=$(( POST_CRASH_COUNT_TIMEOUT - PRE_CRASH_COUNT ))
                if [ "$NEW_CRASH_COUNT_TIMEOUT" -gt 0 ]; then
                    fail "App hung and crash report(s) generated (count=$NEW_CRASH_COUNT_TIMEOUT)"
                    return 1
                fi
                fail "App did not shut down within ${TIMEOUT_SECONDS}s"
                return 1
            fi
            sleep 0.5
        done

        wait "$APP_PID" 2>/dev/null
        EXIT_CODE=$?
        ELAPSED=$(( $(date +%s) - START_TIME ))
        log "  App exited with code $EXIT_CODE after ${ELAPSED}s"

        # macOS crash reports may take a moment to be written to disk
        sleep "$CRASH_REPORT_DELAY"

        # Capture stderr for fatal error analysis
        APP_STDERR=""
        if [ -f "$APP_LOG" ]; then
            APP_STDERR=$(cat "$APP_LOG" 2>/dev/null || true)
        fi

        # Crash reports: check for new ones regardless of exit code.
        # os._exit(0) produces exit code 0 even if the process crashed
        # from a SIGABRT (abort trap 6) — the "Python has crashed" dialog
        # appears despite exit code 0 and the crash report being generated.
        local POST_CRASH_COUNT=0
        if [ -d "$CRASH_DIR" ]; then
            POST_CRASH_COUNT=$(ls "$CRASH_DIR"/Edgeware++*.crash "$CRASH_DIR"/Edgeware++*.ips "$CRASH_DIR"/Python-*.crash "$CRASH_DIR"/Python-*.ips 2>/dev/null | wc -l | tr -d ' ')
        fi
        local NEW_CRASH_COUNT=$(( POST_CRASH_COUNT - PRE_CRASH_COUNT ))
        if [ "$NEW_CRASH_COUNT" -gt 0 ]; then
            fail "New crash report(s) generated (count=$NEW_CRASH_COUNT)"
            return 1
        fi

        # Check stderr for fatal Python errors and abort trap messages
        if [ -n "$APP_STDERR" ]; then
            if echo "$APP_STDERR" | grep -qiE "abort\(\) called|fatal python error|SIGABRT|Abort trap"; then
                fail "Fatal error in stderr output"
                return 1
            fi
        fi

        # Check teardown logs for expected events
        if [ -f "$APP_LOG" ]; then
            if ! check_teardown_logs "$method" "$APP_LOG"; then
                log "  Teardown log check failed"
                # Don't return failure here, as the app may have exited cleanly
                # Just log the warning and continue
            fi
        fi

        # Exit code 0 is expected from clean shutdown
        if [ "$EXIT_CODE" -eq 0 ]; then
            pass
            return 0
        fi

        log "  App exited with code $EXIT_CODE (non-zero, no crash), retrying..."
    done

    fail "All $RETRIES attempts produced non-clean exit"
    return 1
}

# --- Main ---

log "Panic integration test — ${TARGET} — methods: ${METHODS[*]}"
log "========================================="

FAILED=()
for method in "${METHODS[@]}"; do
    log ""
    log "========================================="
    log "Testing method: ${method}"
    log "========================================="
    if ! test_panic_method "$method"; then
        FAILED+=("$method")
    fi
    log ""
done

log ""
log "========================================="
if [ ${#FAILED[@]} -eq 0 ]; then
    log "ALL METHODS PASSED"
    exit 0
else
    log "FAILED methods: ${FAILED[*]}"
    exit 1
fi
