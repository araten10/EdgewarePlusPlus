import ctypes
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from tkinter import Toplevel

from paths import PATH, CustomAssets, Process

try:
    import vlc
except FileNotFoundError:
    # Defined for type hints
    class vlc:
        MediaPlayer = None


PYW = {
    Process.CONFIG: PATH / "config.pyw",
    Process.MAIN: PATH / "edgeware.pyw",
    Process.PANIC: PATH / "panic.pyw",
}


def set_borderless(window: Toplevel) -> None:
    window.overrideredirect(True)


def set_wallpaper(wallpaper: Path) -> None:
    ctypes.windll.user32.SystemParametersInfoW(20, 0, str(wallpaper), 0)


def set_vlc_window(player: vlc.MediaPlayer, window_id: int) -> None:
    player.set_hwnd(window_id)


def open_directory(url: str) -> None:
    subprocess.Popen(f'explorer "{url}"')


def make_shortcut(title: str, process: Path, icon: Path, location: Path | None = None) -> None:
    filename = f"{title}.lnk"
    file = (location if location else Path(os.path.expanduser("~\\Desktop"))) / filename

    pyw_process = PYW[process]

    with tempfile.NamedTemporaryFile(
        "w",
        suffix=".bat",
        delete=False,
    ) as bat:
        bat.writelines(
            [
                '@echo off\nset SCRIPT="%TEMP%\\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"\n',
                'echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%\n',
                'echo sLinkFile = "' + str(file) + '" >> %SCRIPT%\n',
                "echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%\n",
                'echo oLink.WorkingDirectory = "' + str(pyw_process.parent) + '\\" >> %SCRIPT%\n',
                'echo oLink.IconLocation = "' + str(icon) + '" >> %SCRIPT%\n',
                'echo oLink.TargetPath = "' + str(pyw_process) + '" >> %SCRIPT%\n',
                "echo oLink.Save >> %SCRIPT%\n",
                "cscript /nologo %SCRIPT%\n",
                "del %SCRIPT%",
            ]
        )  # write built shortcut script text to temporary batch file

    try:
        subprocess.run(bat.name)
    except Exception as e:
        logging.warning(f"failed to call or remove temp batch file for making shortcuts\n\tReason: {e}")

    if os.path.exists(bat.name):
        os.remove(bat.name)


def toggle_run_at_startup(state: bool) -> None:
    startup_path = Path(os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"))
    if state:
        make_shortcut("Edgeware++", PYW[Process.MAIN], CustomAssets.icon(), startup_path)
    else:
        (startup_path / "Edgeware++.lnk").unlink(missing_ok=True)
