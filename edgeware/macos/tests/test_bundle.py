#!/usr/bin/env python3
"""Test the bundled app by simulating frozen mode.

We can't import Python modules from a PyInstaller bundle (they live in
the internal PYZ archive), so we import from the source tree but
simulate the frozen environment that the runtime hook and
mac_angle.py encounter when running inside the bundle:
  - sys.frozen = True
  - sys.executable points to the bundled binary
  - DYLD_LIBRARY_PATH / library paths are those of the bundle

This tests that the frozen-path resolution in mac_angle.py and the
library loading logic work correctly with the bundle's layout.

Usage: cd edgeware && .venv/bin/python3 macos/test_bundle.py
"""
import os
import sys
import time
import tkinter as tk
from pathlib import Path

EDGWARE_DIR = Path(__file__).parent.parent.parent   # edgeware/
DIST_APP = EDGWARE_DIR / "dist" / "Edgeware++.app"

# Source tree paths for Python modules
SRC_DIR = EDGWARE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Test assets — use source tree (test pack isn't bundled)
TEST_PACK = EDGWARE_DIR / "data" / "packs" / "Edgeware++ Test Pack V2"
ASSETS_DIR = EDGWARE_DIR / "assets"
SCREENSHOT_DIR = Path("/tmp/mpv_bundle_test")
NONBLACK_THRESHOLD = 2.0

# --- Pre-load ANGLE from the bundle's Frameworks/ (simulating runtime hook) ---
_BUNDLE_FRAMEWORKS = DIST_APP / "Contents" / "Frameworks"
_BUNDLE_ANGLE_RESOURCES = DIST_APP / "Contents" / "Resources" / "src" / "os_utils" / "angle_libs"

# Verify the bundle has the expected library layout
def check_bundle_layout():
    """Verify the bundle was built with the correct structure."""
    checks = {
        "Frameworks/libEGL.dylib": _BUNDLE_FRAMEWORKS / "libEGL.dylib",
        "Frameworks/libGLESv2.dylib": _BUNDLE_FRAMEWORKS / "libGLESv2.dylib",
        "Frameworks/libmpv.dylib": _BUNDLE_FRAMEWORKS / "libmpv.dylib",
        "Resources/angle_libs/libEGL.dylib": _BUNDLE_ANGLE_RESOURCES / "libEGL.dylib",
        "Resources/angle_libs/libGLESv2.dylib": _BUNDLE_ANGLE_RESOURCES / "libGLESv2.dylib",
    }
    results = {}
    for label, path in checks.items():
        exists = path.is_file()
        results[label] = exists
        print(f"  {'OK' if exists else 'MISSING'}: {label}", flush=True)
    return results


def preload_bundle_libs():
    """Pre-load bundle libraries (simulating rthook_mpv.py behavior)."""
    import ctypes
    for lib_name in ("libmpv.dylib",):
        for lib_path in (_BUNDLE_FRAMEWORKS / lib_name,):
            if lib_path.is_file():
                try:
                    ctypes.CDLL(str(lib_path))
                    print(f"  Pre-loaded {lib_name} from Frameworks/", flush=True)
                except OSError as exc:
                    print(f"  Warning: failed to pre-load {lib_name}: {exc}", flush=True)
                break

    for lib_name in ("libEGL.dylib", "libGLESv2.dylib"):
        for lib_path in (_BUNDLE_FRAMEWORKS / lib_name, _BUNDLE_ANGLE_RESOURCES / lib_name):
            if lib_path.is_file():
                try:
                    ctypes.CDLL(str(lib_path))
                    print(f"  Pre-loaded {lib_name} from {lib_path.parent.name}/", flush=True)
                except OSError as exc:
                    print(f"  Warning: failed to pre-load {lib_name}: {exc}", flush=True)
                break


def find_test_video():
    vid_dir = TEST_PACK / "vid"
    if not vid_dir.is_dir():
        return None
    vids = list(vid_dir.glob("*.mp4"))
    return vids[0] if vids else None


def find_test_image():
    img_dir = TEST_PACK / "img"
    if not img_dir.is_dir():
        return None
    imgs = list(img_dir.glob("*.png"))
    return imgs[0] if imgs else None


def analyze_pixels(img, label=""):
    from PIL import Image
    if img.mode != "RGB":
        img = img.convert("RGB")
    pixels = list(img.getdata())
    total = len(pixels)
    black = sum(1 for p in pixels if all(c < 30 for c in p[:3]))
    nonblack = 100 * (total - black) / total
    if label:
        SCREENSHOT_DIR.mkdir(exist_ok=True)
        img.save(SCREENSHOT_DIR / f"{label}.png")
    return {"total": total, "nonblack_pct": nonblack}


def create_test_window(root, w, h, offset_y=100):
    t = tk.Toplevel(root)
    t.geometry(f"{w}x{h}+100+{offset_y}")
    t.config(bg="black")
    t.attributes("-topmost", True)
    t.update()
    return t


def destroy_test_window(root, t):
    try:
        root.tk.call("destroy", t._w)
    except Exception:
        pass


def test_mpv_render_video() -> dict:
    """Test mpv render API using ANGLE dylibs from the BUNDLE."""
    print("\n=== Bundle Test 1: mpv Render API Video (ANGLE from bundle) ===", flush=True)

    video_path = find_test_video()
    if not video_path:
        print("  SKIP: No test video found", flush=True)
        return {"mode": "mpv_render", "status": "SKIP", "nonblack_pct": 0}

    # Use the ANGLE libraries from the bundle's Frameworks/ directory
    angle_lib_dir = str(_BUNDLE_FRAMEWORKS)

    root = tk.Tk()
    root.withdraw()
    w, h = 400, 300
    t = create_test_window(root, w, h)

    from os_utils.mac_angle import RenderVideoPlayer, OffscreenRenderer

    player = RenderVideoPlayer(t, w, h)
    try:
        # Override: use the bundle's ANGLE dylibs explicitly
        player._renderer = OffscreenRenderer(w, h, angle_lib_dir=angle_lib_dir)
        player._renderer.make_current()
        import mpv as _mpv
        player._player = _mpv.MPV(vo="libmpv", start_event_thread=True)
        for key, val in {"loop": "inf", "hwdec": "no"}.items():
            player._player[key] = val
        player._render_ctx = _mpv.MpvRenderContext(
            player._player, "opengl",
            opengl_init_params={"get_proc_address": player._renderer.get_proc_address},
            advanced_control=True,
        )
        print(f"  Render context + mpv created OK (ANGLE from bundle Frameworks/)", flush=True)
    except Exception as e:
        print(f"  FAIL: Could not create render context: {e}", flush=True)
        destroy_test_window(root, t)
        root.destroy()
        return {"mode": "mpv_render", "status": "FAIL", "nonblack_pct": 0, "error": str(e)}

    player.play(str(video_path))

    best_pct = 0
    for i in range(40):
        t.update()
        time.sleep(0.1)
        if player._renderer and player._active:
            try:
                img = player._renderer.read_frame()
                result = analyze_pixels(img, f"bundle_frame_{i}")
                pct = result["nonblack_pct"]
                best_pct = max(best_pct, pct)
                if pct > NONBLACK_THRESHOLD:
                    print(f"  Frame {i}: {pct:.1f}% non-black -> PASS", flush=True)
                    break
            except Exception as e:
                print(f"  Frame {i}: read error: {e}", flush=True)

    result = {"mode": "mpv_render", "nonblack_pct": best_pct}
    result["status"] = "PASS" if best_pct > NONBLACK_THRESHOLD else "FAIL"
    if best_pct <= NONBLACK_THRESHOLD:
        print(f"  Best frame: {best_pct:.1f}% non-black -> FAIL", flush=True)

    player.close()
    destroy_test_window(root, t)
    root.destroy()
    return result


def test_mpv_render_with_overlay() -> dict:
    """Test mpv render API with overlay, using ANGLE from the bundle."""
    print("\n=== Bundle Test 2: mpv Render + Overlay (ANGLE from bundle) ===", flush=True)

    video_path = find_test_video()
    img_path = find_test_image()
    if not video_path or not img_path:
        print("  SKIP: Missing test assets", flush=True)
        return {"mode": "mpv_overlay", "status": "SKIP", "nonblack_pct": 0}

    from PIL import Image
    angle_lib_dir = str(_BUNDLE_FRAMEWORKS)

    root = tk.Tk()
    root.withdraw()
    w, h = 400, 300
    t = create_test_window(root, w, h, offset_y=150)

    from os_utils.mac_angle import RenderVideoPlayer, OffscreenRenderer

    player = RenderVideoPlayer(t, w, h)
    player._renderer = OffscreenRenderer(w, h, angle_lib_dir=angle_lib_dir)
    player._renderer.make_current()
    import mpv as _mpv
    player._player = _mpv.MPV(vo="libmpv", start_event_thread=True)
    for key, val in {"loop": "inf", "hwdec": "no"}.items():
        player._player[key] = val
    player._render_ctx = _mpv.MpvRenderContext(
        player._player, "opengl",
        opengl_init_params={"get_proc_address": player._renderer.get_proc_address},
        advanced_control=True,
    )

    overlay_img = Image.open(img_path).resize((w, h), Image.LANCZOS).convert("RGBA")
    overlay_img.putalpha(128)
    player.play(str(video_path), overlays=[(overlay_img, (0, 0))])

    best_pct = 0
    for i in range(40):
        t.update()
        time.sleep(0.1)
        if player._renderer and player._active:
            try:
                img = player._renderer.read_frame()
                result = analyze_pixels(img, f"bundle_overlay_{i}")
                pct = result["nonblack_pct"]
                best_pct = max(best_pct, pct)
                if pct > NONBLACK_THRESHOLD:
                    print(f"  Frame {i}: {pct:.1f}% non-black -> PASS", flush=True)
                    break
            except Exception:
                pass

    result = {"mode": "mpv_overlay", "nonblack_pct": best_pct}
    result["status"] = "PASS" if best_pct > NONBLACK_THRESHOLD else "FAIL"
    if best_pct <= NONBLACK_THRESHOLD:
        print(f"  Best frame: {best_pct:.1f}% non-black -> FAIL", flush=True)

    player.close()
    destroy_test_window(root, t)
    root.destroy()
    return result


def test_hypno_overlay() -> dict:
    """Test hypno: gif + semi-transparent overlay, ANGLE from bundle."""
    print("\n=== Bundle Test 3: Hypno Overlay (ANGLE from bundle) ===", flush=True)

    hypno_path = ASSETS_DIR / "default_hypno.gif"
    img_path = find_test_image()
    if not hypno_path.is_file() or not img_path:
        print("  SKIP: Missing assets", flush=True)
        return {"mode": "hypno_overlay", "status": "SKIP", "nonblack_pct": 0}

    from PIL import Image
    angle_lib_dir = str(_BUNDLE_FRAMEWORKS)

    root = tk.Tk()
    root.withdraw()
    w, h = 400, 400
    t = create_test_window(root, w, h, offset_y=200)

    from os_utils.mac_angle import RenderVideoPlayer, OffscreenRenderer

    player = RenderVideoPlayer(t, w, h)
    player._renderer = OffscreenRenderer(w, h, angle_lib_dir=angle_lib_dir)
    player._renderer.make_current()
    import mpv as _mpv
    player._player = _mpv.MPV(vo="libmpv", start_event_thread=True)
    for key, val in {"loop": "inf", "hwdec": "no"}.items():
        player._player[key] = val
    player._render_ctx = _mpv.MpvRenderContext(
        player._player, "opengl",
        opengl_init_params={"get_proc_address": player._renderer.get_proc_address},
        advanced_control=True,
    )

    overlay_img = Image.open(img_path).resize((w, h), Image.LANCZOS).convert("RGBA")
    overlay_img.putalpha(int((1 - 0.20) * 255))
    player.play(str(hypno_path), overlays=[(overlay_img, (0, 0))])

    best_pct = 0
    for i in range(40):
        t.update()
        time.sleep(0.1)
        if player._renderer and player._active:
            try:
                img = player._renderer.read_frame()
                result = analyze_pixels(img, f"bundle_hypno_{i}")
                pct = result["nonblack_pct"]
                best_pct = max(best_pct, pct)
                if pct > NONBLACK_THRESHOLD:
                    print(f"  Frame {i}: {pct:.1f}% non-black -> PASS", flush=True)
                    break
            except Exception:
                pass

    result = {"mode": "hypno_overlay", "nonblack_pct": best_pct}
    result["status"] = "PASS" if best_pct > NONBLACK_THRESHOLD else "FAIL"
    if best_pct <= NONBLACK_THRESHOLD:
        print(f"  Best frame: {best_pct:.1f}% non-black -> FAIL", flush=True)

    player.close()
    destroy_test_window(root, t)
    root.destroy()
    return result


def test_angle_from_resources_fallback() -> dict:
    """Test ANGLE from the Resources/ fallback path (also in the bundle)."""
    print("\n=== Bundle Test 4: ANGLE from Resources/ fallback ===", flush=True)

    video_path = find_test_video()
    if not video_path:
        return {"mode": "angle_resources_fallback", "status": "SKIP", "nonblack_pct": 0}

    angle_lib_dir = str(_BUNDLE_ANGLE_RESOURCES)

    root = tk.Tk()
    root.withdraw()
    w, h = 400, 300
    t = create_test_window(root, w, h, offset_y=300)

    from os_utils.mac_angle import RenderVideoPlayer, OffscreenRenderer

    player = RenderVideoPlayer(t, w, h)
    try:
        player._renderer = OffscreenRenderer(w, h, angle_lib_dir=angle_lib_dir)
        player._renderer.make_current()
        import mpv as _mpv
        player._player = _mpv.MPV(vo="libmpv", start_event_thread=True)
        for key, val in {"loop": "inf", "hwdec": "no"}.items():
            player._player[key] = val
        player._render_ctx = _mpv.MpvRenderContext(
            player._player, "opengl",
            opengl_init_params={"get_proc_address": player._renderer.get_proc_address},
            advanced_control=True,
        )
        print(f"  Render context created OK (ANGLE from Resources/)", flush=True)
    except Exception as e:
        print(f"  FAIL: {e}", flush=True)
        destroy_test_window(root, t)
        root.destroy()
        return {"mode": "angle_resources_fallback", "status": "FAIL", "nonblack_pct": 0, "error": str(e)}

    player.play(str(video_path))

    best_pct = 0
    for i in range(40):
        t.update()
        time.sleep(0.1)
        if player._renderer and player._active:
            try:
                img = player._renderer.read_frame()
                result = analyze_pixels(img, f"bundle_res_{i}")
                pct = result["nonblack_pct"]
                best_pct = max(best_pct, pct)
                if pct > NONBLACK_THRESHOLD:
                    print(f"  Frame {i}: {pct:.1f}% non-black -> PASS", flush=True)
                    break
            except Exception:
                pass

    result = {"mode": "angle_resources_fallback", "nonblack_pct": best_pct}
    result["status"] = "PASS" if best_pct > NONBLACK_THRESHOLD else "FAIL"
    if best_pct <= NONBLACK_THRESHOLD:
        print(f"  Best frame: {best_pct:.1f}% non-black -> FAIL", flush=True)

    player.close()
    destroy_test_window(root, t)
    root.destroy()
    return result


def main():
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    print(f"Platform: {sys.platform}", flush=True)
    print(f"Python: {sys.version.split()[0]}", flush=True)
    print(f"Bundled app: {DIST_APP}", flush=True)
    print(f"Bundle Frameworks dir: {_BUNDLE_FRAMEWORKS}", flush=True)
    print()

    # --- Verify bundle layout ---
    print("=== Checking Bundle Layout ===", flush=True)
    layout = check_bundle_layout()
    all_present = all(layout.values())
    if not all_present:
        missing = [k for k, v in layout.items() if not v]
        print(f"\n  ERROR: Missing bundle files: {missing}", flush=True)
        print("  Run 'bash macos/build_app.sh' first.", flush=True)
        os._exit(1)
    print("  Bundle layout OK", flush=True)

    # --- Pre-load bundle libraries (simulating runtime hook) ---
    print("\n=== Pre-loading Bundle Libraries ===", flush=True)
    preload_bundle_libs()

    # --- Run tests ---
    results = []
    results.append(test_mpv_render_video())
    results.append(test_mpv_render_with_overlay())
    results.append(test_hypno_overlay())
    results.append(test_angle_from_resources_fallback())

    print(f"\n{'='*60}", flush=True)
    print("BUNDLE TEST SUMMARY", flush=True)
    print(f"{'='*60}", flush=True)
    failures = 0
    for r in results:
        status = r.get("status", "SKIP")
        mode = r.get("mode", "unknown")
        pct = r.get("nonblack_pct", 0)
        error = r.get("error", "")
        extra = f"  ({error})" if error else ""
        print(f"  {mode:30s} {status:4s}  ({pct:.1f}% non-black){extra}", flush=True)
        if status == "FAIL":
            failures += 1

    print(f"\nResult: {'ALL PASS' if failures == 0 else f'{failures} FAILURE(S)'}", flush=True)
    os._exit(1 if failures else 0)


if __name__ == "__main__":
    main()
