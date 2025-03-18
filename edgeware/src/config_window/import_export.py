import os
import shutil
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox

from config_window.utils import confirm_overwrite, refresh
from paths import DEFAULT_PACK_PATH, Data, PackPaths


def import_pack(default: bool) -> None:
    pack_zip = filedialog.askopenfile("r", defaultextension=".zip")
    if not pack_zip:
        return

    if not zipfile.is_zipfile(pack_zip.name):
        messagebox.showerror("Error", "Selected file is not a zip file.")
        return

    pack_name = Path(pack_zip.name).with_suffix("").name
    import_location = DEFAULT_PACK_PATH if default else Data.PACKS / pack_name

    if not confirm_overwrite(import_location):
        messagebox.showinfo("Cancelled", "Pack import cancelled.")
        return

    with zipfile.ZipFile(pack_zip.name, "r") as zip:
        import_location.mkdir(parents=True, exist_ok=True)
        zip.extractall(import_location)

    # Packs are often incorrectly packaged such that they get imported as:
    #   import_location/pack_name/[files]
    # instead of:
    #   import_location/[files]
    #
    # As a remedy, when pack files are not found in import_location and only
    # one subdirectory exists, move all files from the subdirectory one level
    # up and check if pack files exist again.
    pack_paths = PackPaths(import_location)
    check_vars = [var for var in vars(pack_paths) if var not in ["root", "splash"]]
    paths_exist = lambda: any(getattr(pack_paths, var).exists() for var in check_vars)  # noqa: E731
    failure = lambda: messagebox.showerror("Error", "Pack appears to be incorrectly packaged, unable to recover.")  # noqa: E731

    if not paths_exist():
        files = os.listdir(import_location)
        if len(files) != 1:
            failure()
            return

        subdir = import_location / files[0]
        if not subdir.is_dir():
            failure()
            return

        for file in os.listdir(subdir):
            shutil.move(subdir / file, import_location / file)
        subdir.rmdir()

    if not paths_exist():
        failure()
        return

    messagebox.showinfo("Done", f'Pack imported to "{import_location}". Refreshing config window.')
    refresh()
