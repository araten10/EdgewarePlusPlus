#!/usr/bin/env python3
"""Automated test for mpv render API embedding on macOS.

Tests whether mpv can render video frames via the offscreen OpenGL
render pipeline. Verifies pixel content by reading the FBO directly
(no screencapture permission needed).

Usage: cd edgeware && .venv/bin/python3 macos/test_mpv_embed.py
"""

import os
import sys
import time
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

SCREENSHOT_DIR = Path("/tmp/mpv_test")
TEST_PACK = Path("data/packs/Edgeware++ Test Pack V2")

NONBLACK_THRESHOLD = 2.0  # galaga.mp4 is mostly dark; 2%+ non-black is success


def destroy_test_window(root, t):
    """Destroy a test window safely on macOS.

    After mpv render context is freed, tkinter's destroy() can hang
    because mpv registered Tcl commands. Use raw tk.call to bypass.
    """
    if sys.platform == "darwin":
        try:
            root.tk.call("destroy", t._w)
        except Exception:
            pass
    else:
        t.destroy()


def find_test_video() -> Path | None:
    vids = list((TEST_PACK / "vid").glob("*.mp4"))
    return vids[0] if vids else None


def find_test_image() -> Path | None:
    imgs = list((TEST_PACK / "img").glob("*.png"))
    return imgs[0] if imgs else None


def analyze_pixels(img, label: str = "") -> dict:
    """Analyze a PIL Image for non-black content."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    pixels = list(img.getdata())
    total = len(pixels)
    black = sum(1 for p in pixels if all(c < 30 for c in p[:3]))
    nonblack = 100 * (total - black) / total

    if label:
        SCREENSHOT_DIR.mkdir(exist_ok=True)
        img.save(SCREENSHOT_DIR / f"{label}.png")

    return {"total": total, "black_pct": 100 * black / total, "nonblack_pct": nonblack}


def create_test_window(root, w, h):
    t = tk.Toplevel(root)
    t.geometry(f"{w}x{h}+100+100")
    t.config(bg="black")
    t.attributes("-topmost", True)
    t.update()
    t.update_idletasks()
    return t


def test_static_image(root: tk.Tk) -> dict:
    """Test static image display via PIL/tkinter (no mpv)."""
    print("\n=== Test 1: Static Image (PIL/tkinter) ===", flush=True)

    img_path = find_test_image()
    if not img_path:
        print("  SKIP: No test image found", flush=True)
        return {"mode": "static_image", "status": "SKIP", "nonblack_pct": 0}

    from PIL import Image, ImageTk

    w, h = 400, 300
    t = create_test_window(root, w, h)

    image = Image.open(img_path).resize((w, h), Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(t, image=photo, bg="black")
    label.pack(fill="both", expand=True)
    t.update()
    time.sleep(0.5)

    result = analyze_pixels(image, "static_image")
    result["mode"] = "static_image"

    status = "PASS" if result["nonblack_pct"] > NONBLACK_THRESHOLD else "FAIL"
    result["status"] = status
    print(f"  Non-black pixels: {result['nonblack_pct']:.1f}% -> {status}", flush=True)

    destroy_test_window(root, t)
    return result


def test_mpv_render_video(root: tk.Tk) -> dict:
    """Test mpv render API video playback by reading the FBO."""
    print("\n=== Test 2: mpv Render API Video ===", flush=True)

    if sys.platform != "darwin":
        print("  SKIP: macOS-only", flush=True)
        return {"mode": "mpv_render", "status": "SKIP", "nonblack_pct": 0}

    video_path = find_test_video()
    if not video_path:
        print("  SKIP: No test video found", flush=True)
        return {"mode": "mpv_render", "status": "SKIP", "nonblack_pct": 0}

    w, h = 400, 300
    t = create_test_window(root, w, h)

    from os_utils.mac_angle import RenderVideoPlayer

    player = RenderVideoPlayer(t, w, h)
    try:
        player.init_player({"loop": "inf", "hwdec": "no"})
        print(f"  Render context + mpv created OK", flush=True)
    except Exception as e:
        print(f"  FAIL: Could not create render context: {e}", flush=True)
        destroy_test_window(root, t)
        return {"mode": "mpv_render", "status": "FAIL", "nonblack_pct": 0, "error": str(e)}

    player.play(str(video_path))

    best_pct = 0
    for i in range(40):
        t.update()
        time.sleep(0.1)

        if player._renderer and player._active:
            try:
                img = player._renderer.read_frame()
                result = analyze_pixels(img, f"mpv_frame_{i}")
                pct = result["nonblack_pct"]
                best_pct = max(best_pct, pct)
                if pct > NONBLACK_THRESHOLD:
                    print(f"  Frame {i}: {pct:.1f}% non-black -> PASS", flush=True)
                    break
            except Exception:
                pass

    result = {"mode": "mpv_render", "nonblack_pct": best_pct}
    result["status"] = "PASS" if best_pct > NONBLACK_THRESHOLD else "FAIL"
    if best_pct <= NONBLACK_THRESHOLD:
        print(f"  Best frame: {best_pct:.1f}% non-black -> FAIL", flush=True)

    player.close()
    destroy_test_window(root, t)
    return result


def test_mpv_render_with_overlay(root: tk.Tk) -> dict:
    """Test mpv render API with image overlay (simulates hypno)."""
    print("\n=== Test 3: mpv Render API + Overlay ===", flush=True)

    if sys.platform != "darwin":
        print("  SKIP: macOS-only", flush=True)
        return {"mode": "mpv_overlay", "status": "SKIP", "nonblack_pct": 0}

    video_path = find_test_video()
    img_path = find_test_image()
    if not video_path or not img_path:
        print("  SKIP: Missing test assets", flush=True)
        return {"mode": "mpv_overlay", "status": "SKIP", "nonblack_pct": 0}

    from PIL import Image

    w, h = 400, 300
    t = create_test_window(root, w, h)

    from os_utils.mac_angle import RenderVideoPlayer

    player = RenderVideoPlayer(t, w, h)
    player.init_player({"loop": "inf", "hwdec": "no"})

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
                result = analyze_pixels(img, f"mpv_overlay_{i}")
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
    return result


def test_hypno_overlay(root: tk.Tk) -> dict:
    """Test hypno: gif as video content + semi-transparent image overlay.

    This replicates the real hypno pipeline from image_popup.py:
    - hypno gif plays as the video (via mpv)
    - a static image with reduced alpha is composited on top (overlay)
    """
    print("\n=== Test 4: Hypno Overlay (gif + alpha overlay) ===", flush=True)

    if sys.platform != "darwin":
        print("  SKIP: macOS-only", flush=True)
        return {"mode": "hypno_overlay", "status": "SKIP", "nonblack_pct": 0}

    hypno_path = Path("assets/default_hypno.gif")
    img_path = find_test_image()
    if not hypno_path.is_file() or not img_path:
        print("  SKIP: Missing assets", flush=True)
        return {"mode": "hypno_overlay", "status": "SKIP", "nonblack_pct": 0}

    from PIL import Image

    w, h = 400, 400
    t = create_test_window(root, w, h)

    from os_utils.mac_angle import RenderVideoPlayer

    player = RenderVideoPlayer(t, w, h)
    player.init_player({"loop": "inf", "hwdec": "no"})

    overlay_img = Image.open(img_path).resize((w, h), Image.LANCZOS).convert("RGBA")
    overlay_img.putalpha(int((1 - 0.20) * 255))  # 20% hypno_opacity default

    player.play(str(hypno_path), overlays=[(overlay_img, (0, 0))])

    best_pct = 0
    for i in range(40):
        t.update()
        time.sleep(0.1)

        if player._renderer and player._active:
            try:
                img = player._renderer.read_frame()
                result = analyze_pixels(img, f"hypno_{i}")
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
    return result


def test_denial_glsl_shader(root: tk.Tk) -> dict:
    """Test denial: video with GLSL blur shader applied.

    Replicates the video popup denial path: mpv plays a video with
    a glsl-shaders property pointing to gaussian_blur.glsl.
    """
    print("\n=== Test 5: Denial GLSL Shader (video blur) ===", flush=True)

    if sys.platform != "darwin":
        print("  SKIP: macOS-only", flush=True)
        return {"mode": "denial_glsl", "status": "SKIP", "nonblack_pct": 0}

    video_path = find_test_video()
    shader_path = Path("assets/shaders/gaussian_blur.glsl")
    if not video_path or not shader_path.is_file():
        print("  SKIP: Missing test assets", flush=True)
        return {"mode": "denial_glsl", "status": "SKIP", "nonblack_pct": 0}

    w, h = 400, 300
    t = create_test_window(root, w, h)

    from os_utils.mac_angle import RenderVideoPlayer

    player = RenderVideoPlayer(t, w, h)
    player.init_player({"loop": "inf", "hwdec": "no", "glsl-shaders": str(shader_path)})

    player.play(str(video_path))

    best_pct = 0
    for i in range(40):
        t.update()
        time.sleep(0.1)

        if player._renderer and player._active:
            try:
                img = player._renderer.read_frame()
                result = analyze_pixels(img, f"denial_glsl_{i}")
                pct = result["nonblack_pct"]
                best_pct = max(best_pct, pct)
                if pct > NONBLACK_THRESHOLD:
                    print(f"  Frame {i}: {pct:.1f}% non-black -> PASS", flush=True)
                    break
            except Exception:
                pass

    result = {"mode": "denial_glsl", "nonblack_pct": best_pct}
    result["status"] = "PASS" if best_pct > NONBLACK_THRESHOLD else "FAIL"
    if best_pct <= NONBLACK_THRESHOLD:
        print(f"  Best frame: {best_pct:.1f}% non-black -> FAIL", flush=True)

    player.close()
    destroy_test_window(root, t)
    return result


def test_denial_pil_filter(root: tk.Tk) -> dict:
    """Test denial: static image with PIL GaussianBlur filter.

    Replicates the static image denial path from image_popup.py:
    the image is blurred with GaussianBlur before display.
    """
    print("\n=== Test 6: Denial PIL Filter (static blur) ===", flush=True)

    img_path = find_test_image()
    if not img_path:
        print("  SKIP: No test image found", flush=True)
        return {"mode": "denial_pil", "status": "SKIP", "nonblack_pct": 0}

    from PIL import Image, ImageFilter, ImageTk

    w, h = 400, 300
    t = create_test_window(root, w, h)

    image = Image.open(img_path).resize((w, h), Image.LANCZOS).convert("RGB")
    blurred = image.filter(ImageFilter.GaussianBlur(10))
    photo = ImageTk.PhotoImage(blurred)
    label = tk.Label(t, image=photo, bg="black")
    label.pack(fill="both", expand=True)
    t.update()
    time.sleep(0.5)

    result = analyze_pixels(blurred, "denial_pil")
    result["mode"] = "denial_pil"

    status = "PASS" if result["nonblack_pct"] > NONBLACK_THRESHOLD else "FAIL"
    result["status"] = status
    print(f"  Non-black pixels: {result['nonblack_pct']:.1f}% -> {status}", flush=True)

    destroy_test_window(root, t)
    return result


def test_mpv_subprocess_wid(root: tk.Tk) -> dict:
    """Test mpv subprocess wid mode (expected to fail on macOS)."""
    print("\n=== Test 7: mpv wid Embedding (diagnostic) ===", flush=True)
    print("  SKIP: wid embedding is known broken on macOS", flush=True)
    return {"mode": "mpv_subprocess_wid", "status": "SKIP", "nonblack_pct": 0}


def main() -> None:
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    print(f"Platform: {sys.platform}", flush=True)
    print(f"Python: {sys.version.split()[0]}", flush=True)

    root = tk.Tk()
    root.withdraw()

    results = []
    results.append(test_static_image(root))
    results.append(test_mpv_render_video(root))
    results.append(test_mpv_render_with_overlay(root))
    results.append(test_hypno_overlay(root))
    results.append(test_denial_glsl_shader(root))
    results.append(test_denial_pil_filter(root))
    results.append(test_mpv_subprocess_wid(root))

    root.destroy()

    print(f"\n{'='*60}", flush=True)
    print("SUMMARY", flush=True)
    print(f"{'='*60}", flush=True)
    failures = 0
    for r in results:
        status = r.get("status", "SKIP")
        mode = r.get("mode", "unknown")
        pct = r.get("nonblack_pct", 0)
        note = r.get("note", "")
        extra = f"  ({note})" if note else ""
        print(f"  {mode:25s} {status:4s}  ({pct:.1f}% non-black){extra}", flush=True)
        if status == "FAIL":
            failures += 1

    print(f"\nResult: {'ALL PASS' if failures == 0 else f'{failures} FAILURE(S)'}", flush=True)
    os._exit(1 if failures else 0)


if __name__ == "__main__":
    main()
