import webbrowser
from tkinter import (
    CENTER,
    GROOVE,
    RAISED,
    Button,
    Checkbutton,
    Frame,
    Label,
    Message,
    OptionMenu,
    Scale,
    StringVar,
    Text,
    Tk,
)
from tkinter.font import Font

from config_window.utils import BUTTON_FACE, all_children, set_widget_states
from config_window.vars import Vars
from panic import send_panic
from paths import CustomAssets
from PIL import ImageTk
from widgets.tooltip import CreateToolTip

START_TEXT = 'Welcome to Edgeware++!\nYou can use the tabs at the top of this window to navigate the various config settings for the main program. Annoyance/Runtime is for how the program works while running, Modes is for more complicated and involved settings that change how Edgeware works drastically, and Troubleshooting and About are for learning this program better and fixing errors should anything go wrong.\n\nAside from these helper memos, there are also tooltips on several buttons and sliders. If you see your mouse cursor change to a "question mark", hover for a second or two to see more information on the setting.'
PANIC_TEXT = '"Panic" is a feature that allows you to instantly halt the program and revert your desktop background back to the "panic background" set in the wallpaper sub-tab. (found in the annoyance tab)\n\nThere are a few ways to initiate panic, but one of the easiest to access is setting a hotkey here. You should also make sure to change your panic wallpaper to your currently used wallpaper before using Edgeware!'


def assign_key(parent: Tk, button: Button, var: StringVar, key):
    button.configure(text=f"Set Panic\nButton\n<{key.keysym}>")
    var.set(str(key.keysym))
    parent.destroy()


def get_keyboard_input(button: Button, var: StringVar):
    child = Tk()
    child.resizable(False, False)
    child.title("Key Listener")
    child.wm_attributes("-topmost", 1)
    child.geometry("250x250")
    child.focus_force()
    Label(child, text="Press any key or exit").pack(expand=1, fill="both")
    child.bind("<KeyPress>", lambda key: assign_key(child, button, var, key))
    child.mainloop()


class StartTab(Frame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message], local_version: int, live_version: int):
        super().__init__()

        test_group = []

        start_message = Message(self, text=START_TEXT, justify=CENTER, width=675)
        start_message.pack(fill="both")
        message_group.append(start_message)

        # version information
        Label(self, text="Information", font=title_font, relief=GROOVE).pack(pady=2)
        infoHostFrame = Frame(self, borderwidth=5, relief=RAISED)
        zipGitFrame = Frame(infoHostFrame)
        openGitButton = Button(zipGitFrame, text="Open Edgeware++ Github", command=lambda: webbrowser.open("https://github.com/araten10/EdgewarePlusPlus"))

        verPlusFrame = Frame(infoHostFrame)
        local_verPlusLabel = Label(verPlusFrame, text=f"EdgeWare++ Local Version:\n{local_version}")
        web_verPlusLabel = Label(
            verPlusFrame, text=f"EdgeWare++ Github Version:\n{live_version}", bg=(BUTTON_FACE if (local_version == live_version) else "red")
        )
        directDownloadButton = Button(
            zipGitFrame,
            text="Download Newest Update",
            command=lambda: webbrowser.open("https://github.com/araten10/EdgewarePlusPlus/archive/refs/heads/main.zip"),
        )

        infoHostFrame.pack(fill="x")
        zipGitFrame.pack(fill="both", side="left", expand=1)
        openGitButton.pack(fill="both", expand=1)

        verPlusFrame.pack(fill="both", side="left", expand=1)
        local_verPlusLabel.pack(fill="x")
        web_verPlusLabel.pack(fill="x")
        directDownloadButton.pack(fill="both", expand=1)

        theme_types = ["Original", "Dark", "The One", "Ransom", "Goth", "Bimbo"]

        Label(self, text="Theme", font=title_font, relief=GROOVE).pack(pady=2)
        themeFrame = Frame(self, borderwidth=5, relief=RAISED)
        subThemeFrame = Frame(themeFrame)
        testThemeFrame = Frame(themeFrame)
        testThemePopup = Frame(testThemeFrame)
        testThemePrompt = Frame(testThemeFrame)
        testThemeConfig = Frame(testThemeFrame)

        themeDropdown = OptionMenu(subThemeFrame, vars.theme, *theme_types, command=lambda key: themeHelper(key))
        themeDropdown.configure(width=12)
        ignoreConfigToggle = Checkbutton(subThemeFrame, text="Ignore Config", variable=vars.theme_ignore_config, cursor="question_arrow")

        ignoreconfigttp = CreateToolTip(ignoreConfigToggle, "When enabled, the selected theme does not apply to the config window.")

        def themeHelper(theme):
            skiplist = [testThemeFrame, testThemePopup, testThemePrompt, testThemeConfig, testPopupTitle, testPromptTitle, testConfigTitle]
            if theme == "Original":
                for widget in all_children(testThemeFrame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="#f0f0f0")
                    if isinstance(widget, Button):
                        widget.configure(bg="#f0f0f0", fg="black", font="TkDefaultFont", activebackground="#f0f0f0", activeforeground="black")
                    if isinstance(widget, Label):
                        widget.configure(bg="#f0f0f0", fg="black", font="TkDefaultFont")
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="#f0f0f0", fg="black", font="TkDefaultFont", activebackground="#f0f0f0", activeforeground="black")
                    if isinstance(widget, Text):
                        widget.configure(bg="white", fg="black")
                    if isinstance(widget, Scale):
                        widget.configure(bg="#f0f0f0", fg="black", font="TkDefaultFont", activebackground="#f0f0f0", troughcolor="#c8c8c8")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="#f0f0f0", fg="black", font="TkDefaultFont", selectcolor="white", activebackground="#f0f0f0", activeforeground="black"
                        )
                testpopupttp.background = "#ffffff"
                testpopupttp.foreground = "#000000"
                testpopupttp.bordercolor = "#000000"
            if theme == "Dark":
                for widget in all_children(testThemeFrame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="#282c34")
                    if isinstance(widget, Button):
                        widget.configure(bg="#282c34", fg="ghost white", font=("Segoe UI", 9), activebackground="#282c34", activeforeground="ghost white")
                    if isinstance(widget, Label):
                        widget.configure(bg="#282c34", fg="ghost white", font=("Segoe UI", 9))
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="#282c34", fg="ghost white", font=("Segoe UI", 9), activebackground="#282c34", activeforeground="ghost white")
                    if isinstance(widget, Text):
                        widget.configure(bg="#1b1d23", fg="ghost white")
                    if isinstance(widget, Scale):
                        widget.configure(bg="#282c34", fg="ghost white", font=("Segoe UI", 9), activebackground="#282c34", troughcolor="#c8c8c8")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="#282c34",
                            fg="ghost white",
                            font=("Segoe UI", 9),
                            selectcolor="#1b1d23",
                            activebackground="#282c34",
                            activeforeground="ghost white",
                        )
                testpopupttp.background = "#1b1d23"
                testpopupttp.foreground = "#ffffff"
                testpopupttp.bordercolor = "#ffffff"
            if theme == "The One":
                for widget in all_children(testThemeFrame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="#282c34")
                    if isinstance(widget, Button):
                        widget.configure(bg="#282c34", fg="#00ff41", font=("Consolas", 8), activebackground="#1b1d23", activeforeground="#00ff41")
                    if isinstance(widget, Label):
                        widget.configure(bg="#282c34", fg="#00ff41", font=("Consolas", 8))
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="#282c34", fg="#00ff41", font=("Consolas", 8), activebackground="#282c34", activeforeground="#00ff41")
                    if isinstance(widget, Text):
                        widget.configure(bg="#1b1d23", fg="#00ff41")
                    if isinstance(widget, Scale):
                        widget.configure(bg="#282c34", fg="#00ff41", font=("Consolas", 8), activebackground="#282c34", troughcolor="#009a22")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="#282c34", fg="#00ff41", font=("Consolas", 8), selectcolor="#1b1d23", activebackground="#282c34", activeforeground="#00ff41"
                        )
                testpopupttp.background = "#1b1d23"
                testpopupttp.foreground = "#00ff41"
                testpopupttp.bordercolor = "#00ff41"
            if theme == "Ransom":
                for widget in all_children(testThemeFrame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="#841212")
                    if isinstance(widget, Button):
                        widget.configure(bg="#841212", fg="yellow", font=("Arial", 9), activebackground="#841212", activeforeground="yellow")
                    if isinstance(widget, Label):
                        widget.configure(bg="#841212", fg="white", font=("Arial Bold", 9))
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="#841212", fg="white", font=("Arial Bold", 9), activebackground="#841212", activeforeground="white")
                    if isinstance(widget, Text):
                        widget.configure(bg="white", fg="black")
                    if isinstance(widget, Scale):
                        widget.configure(bg="#841212", fg="white", font=("Arial", 9), activebackground="#841212", troughcolor="#c8c8c8")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="#841212", fg="white", font=("Arial", 9), selectcolor="#5c0d0d", activebackground="#841212", activeforeground="white"
                        )
                testpopupttp.background = "#ff2600"
                testpopupttp.foreground = "#ffffff"
                testpopupttp.bordercolor = "#000000"
            if theme == "Goth":
                for widget in all_children(testThemeFrame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="#282c34")
                    if isinstance(widget, Button):
                        widget.configure(bg="#282c34", fg="MediumPurple1", font=("Constantia", 9), activebackground="#282c34", activeforeground="MediumPurple1")
                    if isinstance(widget, Label):
                        widget.configure(bg="#282c34", fg="MediumPurple1", font=("Constantia", 9))
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="#282c34", fg="MediumPurple1", font=("Constantia", 9), activebackground="#282c34", activeforeground="MediumPurple1")
                    if isinstance(widget, Text):
                        widget.configure(bg="MediumOrchid2", fg="purple4")
                    if isinstance(widget, Scale):
                        widget.configure(bg="#282c34", fg="MediumPurple1", font=("Constantia", 9), activebackground="#282c34", troughcolor="MediumOrchid2")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="#282c34",
                            fg="MediumPurple1",
                            font=("Constantia", 9),
                            selectcolor="#1b1d23",
                            activebackground="#282c34",
                            activeforeground="MediumPurple1",
                        )
                testpopupttp.background = "#1b1d23"
                testpopupttp.foreground = "#cc60ff"
                testpopupttp.bordercolor = "#b999fe"
            if theme == "Bimbo":
                for widget in all_children(testThemeFrame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="pink")
                    if isinstance(widget, Button):
                        widget.configure(bg="pink", fg="deep pink", font=("Constantia", 9), activebackground="hot pink", activeforeground="deep pink")
                    if isinstance(widget, Label):
                        widget.configure(bg="pink", fg="deep pink", font=("Constantia", 9))
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="pink", fg="deep pink", font=("Constantia", 9), activebackground="hot pink", activeforeground="deep pink")
                    if isinstance(widget, Text):
                        widget.configure(bg="light pink", fg="magenta2")
                    if isinstance(widget, Scale):
                        widget.configure(bg="pink", fg="deep pink", font=("Constantia", 9), activebackground="pink", troughcolor="hot pink")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="pink", fg="deep pink", font=("Constantia", 9), selectcolor="light pink", activebackground="pink", activeforeground="deep pink"
                        )
                testpopupttp.background = "#ffc5cd"
                testpopupttp.foreground = "#ff3aa3"
                testpopupttp.bordercolor = "#ff84c1"
            set_widget_states(False, test_group, theme)

        testPopupTitle = Label(testThemePopup, text="Popup")
        self.testPopupImage = ImageTk.PhotoImage(file=CustomAssets.theme_demo())  # Stored to avoid garbage collection
        testPopupLabel = Label(testThemePopup, image=self.testPopupImage, width=150, height=75, borderwidth=2, relief=GROOVE, cursor="question_arrow")
        testPopupButton = Button(testPopupLabel, text="Test~")
        testPopupCaption = Label(testPopupLabel, text="Lewd Caption Here!")

        testpopupttp = CreateToolTip(
            testPopupLabel,
            "NOTE: the test image is very small, buttons and captions will appear proportionally larger here!\n\n" "Also, look! The tooltip changed too!",
        )

        testPromptBody = Frame(testThemePrompt, borderwidth=2, relief=GROOVE, width=150, height=75)
        testPromptTitle = Label(testThemePrompt, text="Prompt")
        testPromptInput = Text(testPromptBody, width=18, height=1)
        testPromptButton = Button(testPromptBody, text="Sure!")

        testConfigBody = Frame(testThemeConfig, borderwidth=2, relief=GROOVE)
        testConfigTitle = Label(testThemeConfig, text="Config")
        testCColumn1 = Frame(testConfigBody)
        testToggle = Checkbutton(testConfigBody, text="Check")
        testOptionsMenuVar = StringVar(self, "Option")
        test_types = ["Option", "Menu"]
        testConfigMenu = OptionMenu(testConfigBody, testOptionsMenuVar, *test_types)
        testConfigMenu.config(highlightthickness=0)

        testCColumn2 = Frame(testConfigBody)
        testScaleActivated = Scale(testCColumn2, orient="horizontal", from_=1, to=100, highlightthickness=0)
        testButtonActivated = Button(testCColumn2, text="Activated")

        testCColumn3 = Frame(testConfigBody)
        testScaleDeactivated = Scale(testCColumn3, orient="horizontal", from_=1, to=100, highlightthickness=0)
        testButtonDeactivated = Button(testCColumn3, text="Deactivated")

        test_group.append(testScaleDeactivated)
        test_group.append(testButtonDeactivated)
        set_widget_states(False, test_group)

        themeFrame.pack(fill="x")
        subThemeFrame.pack(fill="both", side="left")
        themeDropdown.pack(fill="both", side="top")
        ignoreConfigToggle.pack(fill="both", side="top")
        testThemeFrame.pack(fill="both", side="left", expand=1)

        testThemePopup.pack(fill="both", side="left", padx=1)
        testPopupTitle.pack(side="top")
        # why ipadx and ipady don't support tuples but padx and pady do is beyond me... i'm a perfectionist and hate bottom and right being one pixel smaller but
        # its a small enough issue im not going to bother doing some hacks to make it look right
        testPopupLabel.pack(side="top", ipadx=1, ipady=1)
        testPopupButton.place(x=140 - testPopupButton.winfo_reqwidth(), y=70 - testPopupButton.winfo_reqheight())
        testPopupCaption.place(x=5, y=5)

        testThemePrompt.pack(fill="both", side="left", padx=1)
        testPromptTitle.pack()
        testPromptBody.pack(fill="both", expand=1)
        Label(testPromptBody, text="Do as I say~").pack(fill="both", expand=1)
        testPromptInput.pack(fill="both")
        testPromptButton.pack(expand=1)

        testThemeConfig.pack(fill="both", side="left", padx=1)
        testConfigTitle.pack(side="top")
        testConfigBody.pack(fill="both", expand=1)
        testCColumn1.pack(side="left", fill="both", expand=1)
        testCColumn2.pack(side="left", fill="both", expand=1)
        testCColumn3.pack(side="left", fill="both", expand=1)
        testToggle.pack(fill="y")
        testConfigMenu.pack(fill="y")
        testButtonActivated.pack(fill="y")
        testScaleActivated.pack(fill="y", expand=1)
        testButtonDeactivated.pack(fill="y")
        testScaleDeactivated.pack(fill="y", expand=1)

        themeHelper(vars.theme.get())

        # other
        Label(self, text="Other", font=title_font, relief=GROOVE).pack(pady=2)
        otherHostFrame = Frame(self, borderwidth=5, relief=RAISED)
        toggleFrame2 = Frame(otherHostFrame)
        toggleFrame3 = Frame(otherHostFrame)

        toggleFlairButton = Checkbutton(toggleFrame2, text="Show Loading Flair", variable=vars.startup_splash, cursor="question_arrow")
        toggleROSButton = Checkbutton(toggleFrame2, text="Run Edgeware on Save & Exit", variable=vars.run_on_save_quit)
        toggleMessageButton = Checkbutton(otherHostFrame, text="Disable Config Help Messages\n(requires save & restart)", variable=vars.message_off)
        toggleDesktopButton = Checkbutton(toggleFrame3, text="Create Desktop Icons", variable=vars.desktop_icons)
        toggleSafeMode = Checkbutton(toggleFrame3, text='Warn if "Dangerous" Settings Active', variable=vars.safe_mode, cursor="question_arrow")

        otherHostFrame.pack(fill="x")
        toggleFrame2.pack(fill="both", side="left", expand=1)
        toggleFlairButton.pack(fill="x")
        toggleROSButton.pack(fill="x")
        toggleFrame3.pack(fill="both", side="left", expand=1)
        toggleDesktopButton.pack(fill="x")
        toggleSafeMode.pack(fill="x")
        toggleMessageButton.pack(fill="both", expand=1)

        loadingFlairttp = CreateToolTip(
            toggleFlairButton, 'Displays a brief "loading" image before EdgeWare startup, which can be set per-pack by the pack creator.'
        )
        safeModettp = CreateToolTip(
            toggleSafeMode,
            "Asks you to confirm before saving if certain settings are enabled.\n"
            "Things defined as Dangerous Settings:\n\n"
            "Extreme (code red! code red! make sure you fully understand what these do before using!):\n"
            "Replace Images\n\n"
            "Major (very dangerous, can affect your computer):\n"
            "Launch on Startup, Fill Drive\n\n"
            "Medium (can lead to embarassment or reduced control over EdgeWare):\n"
            "Timer Mode, Mitosis Mode, Show on Discord, short hibernate cooldown\n\n"
            "Minor (low risk but could lead to unwanted interactions):\n"
            "Disable Panic Hotkey, Run on Save & Exit",
        )

        # panic
        Label(self, text="Panic Settings", font=title_font, relief=GROOVE).pack(pady=2)

        panicMessage = Message(self, text=PANIC_TEXT, justify=CENTER, width=675)
        panicMessage.pack(fill="both")
        message_group.append(panicMessage)

        panicFrame = Frame(self, borderwidth=5, relief=RAISED)

        setPanicButtonButton = Button(
            panicFrame,
            text=f"Set Panic\nButton\n<{vars.panic_key.get()}>",
            command=lambda: get_keyboard_input(setPanicButtonButton, vars.panic_key),
            cursor="question_arrow",
        )
        doPanicButton = Button(panicFrame, text="Perform Panic", command=send_panic)

        setpanicttp = CreateToolTip(setPanicButtonButton, 'NOTE: To use this hotkey you must be "focused" on a EdgeWare popup. Click on a popup before using.')

        panicFrame.pack(fill="x")
        setPanicButtonButton.pack(fill="x", side="left", expand=1)
        doPanicButton.pack(fill="both", side="left", expand=1)
