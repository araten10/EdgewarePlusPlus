from tkinter import (
    Button,
    Scale,
    Checkbutton,
    Frame,
    Label,
    Listbox,
    Message,
    OptionMenu,
    Scale,
    Text,
    Tk,
    font,
)

class ManualScale(tk.Frame):
    def __init__(self, label: Label, *args, **kwargs):
        super().__init__(borderwidth=1, relief="groove", *args, **kwargs)
        inner = Frame(self)
        Scale(inner, label=label, orient="horizontal").pack(fill="x", expand=True)
        Button(inner, text="Manual").pack(fill="x", expand=True, pady=[4, 0])
        inner.pack(padx=4, pady=4, fill="both", expand=True)

    def pack(self):
        super().pack(padx=4, pady=4, side="left", expand=True, fill="x")


class Toggle(tk.Checkbutton):
    def __init__(self, text: str, *args, **kwargs):
        super().__init__(text=text, borderwidth=1, relief="groove", *args, **kwargs)

    def pack(self):
        super().pack(padx=4, pady=4, ipadx=4, ipady=4, side="left", expand=True)


class Section(tk.Frame):
    def __init__(self, title: str, message: str, *args, **kwargs):
        super().__init__(borderwidth=2, relief="raised", *args, **kwargs)
        title_font = font.Font(font="Default")
        title_font.configure(size=15)
        Label(self, text=title, font=title_font).pack()
        Message(self, text=message, width=675).pack(fill="both")

    def pack(self):
        super().pack(padx=8, pady=8, fill="x")


class SettingsRow(tk.Frame):
    def pack(self):
        super().pack(fill="x")
