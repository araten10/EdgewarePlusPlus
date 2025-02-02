import logging
import os
from tkinter import (
    CENTER,
    SINGLE,
    Button,
    Checkbutton,
    Frame,
    Label,
    Listbox,
    Message,
    Scale,
    filedialog,
)

from config_window.utils import (
    config,
    confirm_box,
    set_widget_states,
)
from config_window.vars import Vars
from pack import Pack
from paths import CustomAssets, Data
from PIL import Image, ImageTk
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip

ROTATE_TEXT = "Turning on wallpaper rotate disables built-in pack wallpapers, allowing you to cycle through your own instead. Keep in mind some packs use the corruption feature to rotate wallpapers without this setting enabled."
PANIC_TEXT = "This is the panic wallpaper, make sure to set it to your default wallpaper ASAP! Otherwise quitting edgeware via panic will leave you with a nice and generic windows one instead."


class WallpaperTab(ScrollFrame):
    def __init__(self, vars: Vars, message_group: list[Message], pack: Pack):
        super().__init__()

        self.pack = pack

        rotate_message = Message(self.viewPort, text=ROTATE_TEXT, justify=CENTER, width=675)
        rotate_message.pack(fill="both")
        message_group.append(rotate_message)

        Checkbutton(
            self.viewPort,
            text="Rotate Wallpapers",
            variable=vars.rotate_wallpaper,
            command=lambda: set_widget_states(vars.rotate_wallpaper.get(), wallpaper_group),
        ).pack(fill="x")

        self.wallpaper_list = Listbox(self.viewPort, selectmode=SINGLE)
        self.wallpaper_list.pack(fill="x")
        for key in config["wallpaperDat"]:
            self.wallpaper_list.insert(1, key)

        add_wallpaper_button = Button(self.viewPort, text="Add/Edit Wallpaper", command=self.add_wallpaper)
        add_wallpaper_button.pack(fill="x")
        remove_wallpaper_button = Button(self.viewPort, text="Remove Wallpaper", command=self.remove_wallpaper)
        remove_wallpaper_button.pack(fill="x")
        auto_import_button = Button(self.viewPort, text="Auto Import", command=self.auto_import)
        auto_import_button.pack(fill="x")
        rotate_delay = Scale(
            self.viewPort,
            orient="horizontal",
            label="Rotate Timer (sec)",
            from_=5,
            to=300,
            variable=vars.wallpaper_timer,
            command=lambda val: update_max(rotate_variance, int(val) - 1),
        )
        rotate_delay.pack(fill="x")
        rotate_variance = Scale(
            self.viewPort, orient="horizontal", label="Rotate Variation (sec)", from_=0, to=(vars.wallpaper_timer.get() - 1), variable=vars.wallpaper_variance
        )
        rotate_variance.pack(fill="x")

        wallpaper_group = [self.wallpaper_list, add_wallpaper_button, remove_wallpaper_button, auto_import_button, rotate_delay, rotate_variance]
        set_widget_states(vars.rotate_wallpaper.get(), wallpaper_group)

        panic_message = Message(self.viewPort, text=PANIC_TEXT, justify=CENTER, width=675)
        panic_message.pack(fill="both")
        message_group.append(panic_message)

        panic_wallpaper_frame = Frame(self.viewPort)
        panic_wallpaper_frame.pack(fill="x", expand=1)

        change_panic_wallpaper_frame = Frame(panic_wallpaper_frame)
        change_panic_wallpaper_frame.pack(side="left", fill="y")
        change_panic_wallpaper_button = Button(
            change_panic_wallpaper_frame, text="Change Panic Wallpaper", command=self.change_panic_wallpaper, cursor="question_arrow"
        )
        change_panic_wallpaper_button.pack(fill="x", padx=5, pady=5, expand=1)
        CreateToolTip(
            change_panic_wallpaper_button,
            "When you use panic, the wallpaper will be set to this image.\n\n"
            "This is useful since most packs have a custom wallpaper, which is usually porn...!\n\n"
            "It is recommended to find your preferred/original desktop wallpaper and set it to that.",
        )

        panic_wallpaper_preview_frame = Frame(panic_wallpaper_frame)
        panic_wallpaper_preview_frame.pack(side="right", fill="x", expand=1)
        Label(panic_wallpaper_preview_frame, text="Current Panic Wallpaper").pack(fill="x")
        self.panic_wallpaper_label = Label(panic_wallpaper_preview_frame, text="Current Panic Wallpaper")
        self.panic_wallpaper_label.pack()
        self.load_panic_wallpaper()

    def add_wallpaper(self) -> None:
        file = filedialog.askopenfile("r", filetypes=[("image file", ".jpg .jpeg .png")])
        if not isinstance(file, type(None)):
            lname = simpledialog.askstring("Wallpaper Name", "Wallpaper Label\n(Name displayed in list)")
            if not isinstance(lname, type(None)):
                print(file.name.split("/")[-1])
                config["wallpaperDat"][lname] = file.name.split("/")[-1]
                self.wallpaper_list.insert(1, lname)

    def remove_wallpaper(self) -> None:
        index = int(self.wallpaper_list.curselection()[0])
        itemName = self.wallpaper_list.get(index)
        if index > 0:
            del config["wallpaperDat"][itemName]
            self.wallpaper_list.delete(self.wallpaper_list.curselection())
        else:
            messagebox.showwarning("Remove Default", "You cannot remove the default wallpaper.")

    def auto_import(self) -> None:
        allow_ = confirm_box(
            self.wallpaper_list, "Confirm", "Current list will be cleared before new list is imported from the /resource folder. Is that okay?"
        )
        if allow_:
            # clear list
            while True:
                try:
                    del config["wallpaperDat"][self.wallpaper_list.get(1)]
                    self.wallpaper_list.delete(1)
                except Exception:
                    break
            for file in os.listdir(self.pack.paths.root):
                if (file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg")) and file != "wallpaper.png":
                    name_ = file.split(".")[0]
                    self.wallpaper_list.insert(1, name_)
                    config["wallpaperDat"][name_] = file

    def change_panic_wallpaper(self) -> None:
        file = filedialog.askopenfile("rb", filetypes=[("image file", ".jpg .jpeg .png")])
        if not file:
            return

        try:
            image = Image.open(file.name).convert("RGB")
            image.save(Data.PANIC_WALLPAPER)
            self.load_panic_wallpaper()
        except Exception as e:
            logging.warning(f"failed to open/change panic wallpaper\n{e}")

    def load_panic_wallpaper(self) -> None:
        self.panic_wallpaper_image = ImageTk.PhotoImage(
            Image.open(CustomAssets.panic_wallpaper()).resize((int(self.winfo_screenwidth() * 0.13), int(self.winfo_screenheight() * 0.13)), Image.NEAREST)
        )
        self.panic_wallpaper_label.config(image=self.panic_wallpaper_image)
        self.panic_wallpaper_label.update_idletasks()
