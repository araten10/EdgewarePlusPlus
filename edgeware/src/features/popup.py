import random
import time
from threading import Thread
from tkinter import Button, Label, Tk, Toplevel

from features.misc import open_web, panic
from features.theme import get_theme
from pack import Pack
from paths import Assets
from roll import roll
from screeninfo import get_monitors
from settings import Settings
from utils import utils
from utils.utils import State


class Popup(Toplevel):
    def __init__(self, root: Tk, settings: Settings, pack: Pack, state: State):
        state.popup_number += 1
        super().__init__()

        self.root = root
        self.settings = settings
        self.pack = pack
        self.state = state
        self.theme = get_theme(settings)

        self.bind("<KeyPress>", lambda event: panic(self.root, self.settings, self.state, event.keysym))
        self.attributes("-topmost", True)
        self.attributes("-type", "splash")
        # TODO: May be needed for opacity on some Linux setups
        # self.update_idletasks()
        # self.overrideredirect(True)
        # self.wait_visibility()

        self.opacity = self.settings.opacity
        self.attributes("-alpha", self.opacity)

    def init_finish(self) -> None:
        self.try_caption()
        self.try_button()
        self.try_move()
        self.try_timeout()
        self.try_pump_scare()
        self.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

    def compute_geometry(self, source_width: int, source_height: int) -> None:
        self.monitor = random.choice(get_monitors())

        source_size = max(source_width, source_height) / min(self.monitor.width, self.monitor.height)
        target_size = (random.randint(30, 70) if not self.settings.lowkey_mode else random.randint(20, 50)) / 100
        scale = target_size / source_size

        self.width = int(source_width * scale)
        self.height = int(source_height * scale)

        if self.settings.lowkey_mode:
            corner = self.settings.lowkey_corner
            if corner == 4:  # Random corner
                corner = random.randint(0, 3)

            right = corner == 0 or corner == 3  # Top right or bottom right
            bottom = corner == 2 or corner == 3  # Bottom left or bottom right
            self.x = self.monitor.x + (self.monitor.width - self.width if right else 0)
            self.y = self.monitor.y + (self.monitor.height - self.height if bottom else 0)
        else:
            self.x = random.randint(self.monitor.x, self.monitor.x + self.monitor.width - self.width)
            self.y = random.randint(self.monitor.y, self.monitor.y + self.monitor.height - self.height)

    def try_caption(self) -> None:
        if self.settings.captions_in_popups:
            label = Label(self, text=self.pack.random_caption(), wraplength=self.width, fg=self.theme.fg, bg=self.theme.bg)
            label.place(x=5, y=5)

    def try_button(self) -> None:
        if self.settings.buttonless:
            self.bind("<ButtonRelease-1>", lambda event: self.close())
        else:
            button = Button(
                self,
                text=self.pack.close_text,
                command=self.close,
                fg=self.theme.fg,
                bg=self.theme.bg,
                activeforeground=self.theme.fg,
                activebackground=self.theme.bg,
            )
            button.place(x=-10, y=-10, relx=1, rely=1, anchor="se")

    def try_move(self) -> None:
        def move() -> None:
            speed_x = 0 if self.settings.moving_chance else self.settings.moving_speed
            speed_y = 0 if self.settings.moving_chance else self.settings.moving_speed
            while speed_x == 0 and speed_y == 0:
                speed_x = random.randint(-self.settings.moving_speed, self.settings.moving_speed)
                speed_y = random.randint(-self.settings.moving_speed, self.settings.moving_speed)

            try:
                while True:
                    self.x += speed_x
                    self.y += speed_y

                    left = self.x <= self.monitor.x
                    right = self.x + self.width >= self.monitor.x + self.monitor.width
                    if left or right:
                        speed_x = -speed_x

                    top = self.y <= self.monitor.y
                    bottom = self.y + self.height >= self.monitor.y + self.monitor.height
                    if top or bottom:
                        speed_y = -speed_y

                    self.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
                    time.sleep(0.01)
            except Exception:
                pass  # Exception thrown when closing

        if roll(self.settings.moving_chance):
            Thread(target=move, daemon=True).start()

    def try_timeout(self) -> None:
        def fade_out() -> None:
            try:
                while self.opacity > 0:
                    self.opacity -= 0.01
                    self.attributes("-alpha", self.opacity)
                    time.sleep(0.015)
                self.close()
            except Exception:
                pass  # Exception thrown when manually closed during fade out

        if self.settings.timeout_enabled and not self.state.pump_scare:
            self.after(self.settings.timeout, Thread(target=fade_out, daemon=True).start)

    def try_pump_scare(self) -> None:
        if self.state.pump_scare:
            self.after(2500, self.close)

    def try_web_open(self) -> None:
        if self.settings.web_on_popup_close and roll((100 - self.settings.web_chance) / 2):
            open_web(self.pack)

    def try_mitosis(self) -> None:
        if self.settings.mitosis_mode:
            # Imports done here to avoid circular imports
            from features.image_popup import ImagePopup
            from features.video_popup import VideoPopup

            for n in range(self.settings.mitosis_strength):
                try:
                    popup = random.choices([ImagePopup, VideoPopup], [self.settings.image_chance, self.settings.video_chance], k=1)[0]
                except Exception:
                    popup = ImagePopup  # Exception thrown when both chances are 0
                popup(self.root, self.settings, self.pack, self.state)

    def try_reset_wallpaper(self) -> None:
        if self.settings.hibernate_fix_wallpaper and self.state.reset_wallpaper():
            utils.set_wallpaper(Assets.DEFAULT_PANIC_WALLPAPER)

    def close(self) -> None:
        self.state.popup_number -= 1
        self.try_web_open()
        self.try_mitosis()
        self.try_reset_wallpaper()
        self.destroy()