"""macOS offscreen ANGLE (EGL/GLES-on-Metal) renderer for mpv.

Drop-in replacement for the NSOpenGLContext-based OffscreenRenderer.
Same external interface: __init__(width, height), read_frame(),
make_current(), free(), plus the public `width`/`height` attributes and
the `_fbo` attribute that RenderVideoPlayer._render_tick() reads directly.

Internally this uses ANGLE (https://github.com/google/angle) instead of
Apple's deprecated OpenGL.framework. ANGLE implements EGL + GLES2/3 and,
on macOS, can be backed by Metal, so mpv's "opengl" render API keeps
working unmodified.

PREREQUISITE: you need ANGLE's `libEGL.dylib` and `libGLESv2.dylib`
somewhere on disk. Pass their directory as `angle_lib_dir`, or set the
ANGLE_LIB_DIR environment variable, or place them next to this file.
"""
from __future__ import annotations

import ctypes
import logging
import os
import sys
from ctypes import CFUNCTYPE, c_char_p, c_int, c_int32, c_uint, c_void_p, cast, pointer
from pathlib import Path
from tkinter import Label, Misc
from typing import Callable

from PIL import Image, ImageTk

if sys.platform != "darwin":
    raise ImportError("mac_angle is macOS-only")

import mpv

log = logging.getLogger(__name__)

if getattr(sys, "frozen", False):
    # Check Contents/Frameworks/ first (copy placed there by build script for
    # @rpath resolution), then fall back to the original datas location.
    _ANGLE_FW = (
        Path(sys.executable).parent.parent / "Frameworks"
    )
    _ANGLE_DATA = (
        Path(sys.executable).parent.parent / "Resources"
        / "src" / "os_utils" / "angle_libs"
    )
    if (_ANGLE_FW / "libEGL.dylib").is_file():
        _FROZEN_ANGLE_DIR = str(_ANGLE_FW)
    else:
        _FROZEN_ANGLE_DIR = str(_ANGLE_DATA)
else:
    _FROZEN_ANGLE_DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "angle_libs"
    )

# --------------------------------------------------------------------------
# GL/GLES constants
# --------------------------------------------------------------------------
GL_RGBA = 0x1908
GL_UNSIGNED_BYTE = 0x1401
GL_FRAMEBUFFER = 0x8D40
GL_READ_FRAMEBUFFER = 0x8CA8
GL_COLOR_ATTACHMENT0 = 0x8CE0
GL_RENDERBUFFER = 0x8D41
GL_RGBA8 = 0x8058
GL_FRAMEBUFFER_COMPLETE = 0x8CD5

# --------------------------------------------------------------------------
# EGL constants
# --------------------------------------------------------------------------
EGL_NO_DISPLAY = 0
EGL_NO_CONTEXT = 0
EGL_NO_SURFACE = 0
EGL_DEFAULT_DISPLAY = 0

EGL_NONE = 0x3038
EGL_WIDTH = 0x3057
EGL_HEIGHT = 0x3056
EGL_SURFACE_TYPE = 0x3033
EGL_PBUFFER_BIT = 0x0001
EGL_RENDERABLE_TYPE = 0x3040
EGL_OPENGL_ES3_BIT = 0x0040
EGL_OPENGL_ES2_BIT = 0x0004
EGL_RED_SIZE = 0x3024
EGL_GREEN_SIZE = 0x3023
EGL_BLUE_SIZE = 0x3022
EGL_ALPHA_SIZE = 0x3021
EGL_CONTEXT_CLIENT_VERSION = 0x3098
EGL_OPENGL_ES_API = 0x30A0

# ANGLE platform-selection extension (eglext_angle.h).
EGL_PLATFORM_ANGLE_ANGLE = 0x3202
EGL_PLATFORM_ANGLE_TYPE_ANGLE = 0x3203
EGL_PLATFORM_ANGLE_TYPE_DEFAULT_ANGLE = 0x3206
EGL_PLATFORM_ANGLE_TYPE_METAL_ANGLE = 0x3489


def _find_angle_libs(angle_lib_dir: str | None) -> tuple[str, str]:
    """Locate libEGL.dylib / libGLESv2.dylib from an explicit dir, env var,
    or next to this file. Raises with a clear message if not found."""
    candidates = []
    if angle_lib_dir:
        candidates.append(angle_lib_dir)
    if os.environ.get("ANGLE_LIB_DIR"):
        candidates.append(os.environ["ANGLE_LIB_DIR"])
    candidates.append(os.path.dirname(os.path.abspath(__file__)))

    for d in candidates:
        egl = os.path.join(d, "libEGL.dylib")
        gles = os.path.join(d, "libGLESv2.dylib")
        if os.path.isfile(egl) and os.path.isfile(gles):
            return egl, gles

    raise RuntimeError(
        "Could not find ANGLE's libEGL.dylib / libGLESv2.dylib. Pass "
        "angle_lib_dir=... to OffscreenRenderer, set the ANGLE_LIB_DIR "
        "environment variable, or place both dylibs next to this file. "
        f"Searched: {candidates}"
    )


class _EGL:
    """Thin ctypes wrapper around the subset of EGL/GLES2 we need."""

    def __init__(self, egl_path: str, gles_path: str) -> None:
        self.egl = ctypes.cdll.LoadLibrary(egl_path)
        self.gles = ctypes.cdll.LoadLibrary(gles_path)

        # --- EGL core ---
        self.egl.eglGetProcAddress.restype = c_void_p
        self.egl.eglGetProcAddress.argtypes = [c_char_p]

        self.egl.eglGetDisplay.restype = c_void_p
        self.egl.eglGetDisplay.argtypes = [c_void_p]

        self.egl.eglInitialize.restype = c_int
        self.egl.eglInitialize.argtypes = [c_void_p, ctypes.POINTER(c_int32), ctypes.POINTER(c_int32)]

        self.egl.eglBindAPI.restype = c_int
        self.egl.eglBindAPI.argtypes = [c_uint]

        self.egl.eglChooseConfig.restype = c_int
        self.egl.eglChooseConfig.argtypes = [c_void_p, c_void_p, c_void_p, c_int, c_void_p]

        self.egl.eglCreatePbufferSurface.restype = c_void_p
        self.egl.eglCreatePbufferSurface.argtypes = [c_void_p, c_void_p, c_void_p]

        self.egl.eglCreateContext.restype = c_void_p
        self.egl.eglCreateContext.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p]

        self.egl.eglMakeCurrent.restype = c_int
        self.egl.eglMakeCurrent.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p]

        self.egl.eglDestroySurface.restype = c_int
        self.egl.eglDestroySurface.argtypes = [c_void_p, c_void_p]

        self.egl.eglDestroyContext.restype = c_int
        self.egl.eglDestroyContext.argtypes = [c_void_p, c_void_p]

        self.egl.eglTerminate.restype = c_int
        self.egl.eglTerminate.argtypes = [c_void_p]

        self.egl.eglGetError.restype = c_int
        self.egl.eglGetError.argtypes = []

        # --- optional ANGLE extension, resolved dynamically ---
        proc = self.egl.eglGetProcAddress(b"eglGetPlatformDisplayEXT")
        if proc:
            fn_type = ctypes.CFUNCTYPE(c_void_p, c_uint, c_void_p, c_void_p)
            self.eglGetPlatformDisplayEXT = fn_type(proc)
        else:
            self.eglGetPlatformDisplayEXT = None

        # --- GLES2/3 functions ---
        g = self.gles
        g.glGenFramebuffers.restype = None
        g.glGenFramebuffers.argtypes = [c_uint, c_void_p]
        g.glDeleteFramebuffers.restype = None
        g.glDeleteFramebuffers.argtypes = [c_uint, c_void_p]
        g.glBindFramebuffer.restype = None
        g.glBindFramebuffer.argtypes = [c_uint, c_uint]
        g.glGenRenderbuffers.restype = None
        g.glGenRenderbuffers.argtypes = [c_uint, c_void_p]
        g.glDeleteRenderbuffers.restype = None
        g.glDeleteRenderbuffers.argtypes = [c_uint, c_void_p]
        g.glBindRenderbuffer.restype = None
        g.glBindRenderbuffer.argtypes = [c_uint, c_uint]
        g.glRenderbufferStorage.restype = None
        g.glRenderbufferStorage.argtypes = [c_uint, c_uint, c_int, c_int]
        g.glFramebufferRenderbuffer.restype = None
        g.glFramebufferRenderbuffer.argtypes = [c_uint, c_uint, c_uint, c_uint]
        g.glCheckFramebufferStatus.restype = c_uint
        g.glCheckFramebufferStatus.argtypes = [c_uint]
        g.glReadPixels.restype = None
        g.glReadPixels.argtypes = [c_int, c_int, c_int, c_int, c_uint, c_uint, c_void_p]
        g.glViewport.restype = None
        g.glViewport.argtypes = [c_int, c_int, c_int, c_int]


_GetProcAddrCB = CFUNCTYPE(c_void_p, c_void_p, c_char_p)


class OffscreenRenderer:
    """Offscreen ANGLE (EGL + GLES, Metal-backed) renderer using an FBO."""

    def __init__(self, width: int, height: int, angle_lib_dir: str | None = None) -> None:
        self.width = width
        self.height = height

        egl_path, gles_path = _find_angle_libs(angle_lib_dir)
        self._egl = _EGL(egl_path, gles_path)

        self._display = self._create_display()
        major, minor = c_int32(), c_int32()
        if not self._egl.egl.eglInitialize(self._display, pointer(major), pointer(minor)):
            raise RuntimeError(f"eglInitialize failed (error 0x{self._egl.egl.eglGetError():X})")
        log.info(f"ANGLE/EGL initialized: {major.value}.{minor.value}")

        self._egl.egl.eglBindAPI(EGL_OPENGL_ES_API)

        config = self._choose_config()

        surface_attribs = (c_int32 * 5)(EGL_WIDTH, width, EGL_HEIGHT, height, EGL_NONE)
        self._surface = self._egl.egl.eglCreatePbufferSurface(
            self._display, config, cast(surface_attribs, c_void_p)
        )
        if not self._surface:
            raise RuntimeError(f"eglCreatePbufferSurface failed (error 0x{self._egl.egl.eglGetError():X})")

        ctx_attribs = (c_int32 * 3)(EGL_CONTEXT_CLIENT_VERSION, 3, EGL_NONE)
        self._context = self._egl.egl.eglCreateContext(
            self._display, config, EGL_NO_CONTEXT, cast(ctx_attribs, c_void_p)
        )
        if not self._context:
            raise RuntimeError(f"eglCreateContext failed (error 0x{self._egl.egl.eglGetError():X})")

        self.make_current()

        gles = self._egl.gles
        fbo_ids = (c_uint * 1)()
        gles.glGenFramebuffers(1, cast(fbo_ids, c_void_p))
        self._fbo = fbo_ids[0]

        rbo_ids = (c_uint * 1)()
        gles.glGenRenderbuffers(1, cast(rbo_ids, c_void_p))
        self._rbo = rbo_ids[0]

        gles.glBindFramebuffer(GL_FRAMEBUFFER, self._fbo)
        gles.glBindRenderbuffer(GL_RENDERBUFFER, self._rbo)
        gles.glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA8, width, height)
        gles.glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, self._rbo)

        status = gles.glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f"FBO incomplete: 0x{status:X}")

        self._pixel_buffer = ctypes.create_string_buffer(width * height * 4)

        # Set viewport once — it only changes when the FBO size changes.
        self.viewport(0, 0, width, height)

        # Bound method usable directly as mpv's get_proc_address callback.
        self.get_proc_address = _GetProcAddrCB(self._get_proc_address)

        log.info(f"OffscreenRenderer (ANGLE/Metal): {width}x{height} FBO ready (id={self._fbo})")

    def _create_display(self) -> c_void_p:
        if self._egl.eglGetPlatformDisplayEXT is not None:
            attribs = (c_int32 * 3)(
                EGL_PLATFORM_ANGLE_TYPE_ANGLE, EGL_PLATFORM_ANGLE_TYPE_METAL_ANGLE, EGL_NONE
            )
            display = self._egl.eglGetPlatformDisplayEXT(
                EGL_PLATFORM_ANGLE_ANGLE, c_void_p(EGL_DEFAULT_DISPLAY), cast(attribs, c_void_p)
            )
            if display:
                log.info("ANGLE display created with explicit Metal backend")
                return display
            log.warning("eglGetPlatformDisplayEXT(Metal) failed, falling back to eglGetDisplay")

        display = self._egl.egl.eglGetDisplay(c_void_p(EGL_DEFAULT_DISPLAY))
        if not display:
            raise RuntimeError("eglGetDisplay failed to produce a display")
        return display

    def _choose_config(self) -> c_void_p:
        # Added EGL_ALPHA_SIZE so ANGLE actually allocates alpha space properly, 
        # fixing the black overlay issue.
        attribs = (c_int32 * 13)(
            EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
            EGL_RENDERABLE_TYPE, EGL_OPENGL_ES3_BIT,
            EGL_RED_SIZE, 8,
            EGL_GREEN_SIZE, 8,
            EGL_BLUE_SIZE, 8,
            EGL_ALPHA_SIZE, 8,
            EGL_NONE,
        )
        configs = (c_void_p * 1)()
        num_configs = c_int32()
        ok = self._egl.egl.eglChooseConfig(
            self._display, cast(attribs, c_void_p), cast(configs, c_void_p), 1, pointer(num_configs)
        )
        if not ok or num_configs.value == 0:
            raise RuntimeError(f"eglChooseConfig found no matching config (error 0x{self._egl.egl.eglGetError():X})")
        return configs[0]

    def _get_proc_address(self, _ctx: c_void_p, name: c_char_p) -> int:
        try:
            addr = self._egl.egl.eglGetProcAddress(name)
            if addr:
                return addr
            fn = getattr(self._egl.gles, name.decode())
            return ctypes.cast(fn, c_void_p).value or 0
        except (AttributeError, UnicodeDecodeError):
            log.debug(f"ANGLE: unknown GL function requested: {name!r}")
            return 0

    def viewport(self, x: int, y: int, width: int, height: int) -> None:
        """Set the ANGLE GLES viewport."""
        self._egl.gles.glViewport(x, y, width, height)

    def read_frame(self) -> Image.Image:
        """Read the current FBO contents as a PIL Image (RGBA, top-down)."""
        gles = self._egl.gles
        gles.glBindFramebuffer(GL_READ_FRAMEBUFFER, self._fbo)
        gles.glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE, self._pixel_buffer)
        
        # Wrapped the buffer in bytes() to safely copy the data, preventing 
        # a race condition on the next _pixel_buffer write.
        return Image.frombuffer("RGBA", (self.width, self.height), bytes(self._pixel_buffer), "raw", "RGBA", 0, 1)

    def make_current(self) -> None:
        ok = self._egl.egl.eglMakeCurrent(self._display, self._surface, self._surface, self._context)
        if not ok:
            raise RuntimeError(f"eglMakeCurrent failed (error 0x{self._egl.egl.eglGetError():X})")

    def free(self) -> None:
        gles = self._egl.gles
        gles.glDeleteRenderbuffers(1, pointer(c_uint(self._rbo)))
        gles.glDeleteFramebuffers(1, pointer(c_uint(self._fbo)))

        egl = self._egl.egl
        egl.eglMakeCurrent(self._display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT)
        egl.eglDestroySurface(self._display, self._surface)
        egl.eglDestroyContext(self._display, self._context)
        egl.eglTerminate(self._display)
        log.info("OffscreenRenderer (ANGLE/Metal) freed")


class RenderVideoPlayer(Label):
    """VideoPlayer using mpv render API for macOS."""

    def __init__(self, master: Misc, width: int, height: int, target_fps: int = 60) -> None:
        super().__init__(master, width=width, height=height, bg="black")
        self.pack()

        self._width = width
        self._height = height
        self._tick_interval_ms = max(1, round(1000 / target_fps))
        self._renderer: OffscreenRenderer | None = None
        self._player: mpv.MPV | None = None
        self._render_ctx: mpv.MpvRenderContext | None = None
        self._photo: ImageTk.PhotoImage | None = None
        self._active = False
        self._after_id = None
        self._overlays: list[tuple[Image.Image, tuple[int, int]]] = []
        self._on_eof: Callable[[], None] | None = None

        self._root: Misc = master
        while hasattr(self._root, "master") and self._root.master:
            self._root = self._root.master

    def init_player(self, properties: dict[str, str]) -> None:
        """Create mpv player and render context. Call before play()."""
        self._player = mpv.MPV(vo="libmpv", start_event_thread=True)
        for key, value in properties.items():
            self._player[key] = value

        self._renderer = OffscreenRenderer(self._width, self._height, angle_lib_dir=_FROZEN_ANGLE_DIR)
        self._renderer.make_current()

        # Switched get_proc_address to use the OffscreenRenderer's own method,
        # fully detaching from Apple OpenGL references.
        self._render_ctx = mpv.MpvRenderContext(
            self._player, "opengl",
            opengl_init_params={"get_proc_address": self._renderer.get_proc_address},
            advanced_control=True,
        )

    def play(
        self,
        media: str,
        overlays: list[tuple[Image.Image, tuple[int, int]]] | None = None,
        on_eof: Callable[[], None] | None = None,
    ) -> None:
        if not self._player or not self._render_ctx:
            raise RuntimeError("Call init_player() first")

        self._overlays = overlays or []
        self._on_eof = on_eof

        self._active = True
        self._player.play(media)
        self._render_tick()

    def _render_tick(self) -> None:
        """Main-thread render loop driven by tkinter after()."""
        if not self._active:
            return

        try:
            if self._render_ctx and self._render_ctx.update():
                self._renderer.make_current()
                
                self._render_ctx.render(
                    opengl_fbo={"fbo": self._renderer._fbo, "w": self._renderer.width, "h": self._renderer.height},
                    flip_y=False,
                )
                self._render_ctx.report_swap()

                img = self._renderer.read_frame()
                if self._overlays:
                    try:
                        for overlay, pos in self._overlays:
                            if overlay is None:
                                continue
                            canvas = Image.new("RGBA", (img.width, img.height), (0, 0, 0, 0))
                            canvas.paste(overlay, pos, overlay)
                            img = Image.alpha_composite(img, canvas)
                    except Exception as e:
                        log.warning(f"Overlay compositing error, showing frame without overlays: {e}")

                if self._photo is None:
                    self._photo = ImageTk.PhotoImage(img)
                    self.config(image=self._photo)
                else:
                    self._photo.paste(img)
            elif self._on_eof and self._player:
                try:
                    if self._player.eof_reached:
                        self._active = False
                        self._on_eof()
                        return
                except Exception:
                    pass
        except Exception as e:
            log.warning(f"Render error: {e}")

        self._after_id = self._root.after(self._tick_interval_ms, self._render_tick)

    def close(self) -> None:
        """Stop playback and release references.

        On macOS, mpv's internal threads can deadlock when we try to free
        render contexts or GL resources while they're still active. Calling
        terminate() or freeing the render context is unsafe here. However,
        player.stop() is a safe, high-level client API call that cleanly
        stops playback (including audio) without touching internal locks.
        """
        self._active = False
        self._after_id = None

        if self._player:
            self._player.stop()

        self._renderer = None
        self._player = None
        self._render_ctx = None