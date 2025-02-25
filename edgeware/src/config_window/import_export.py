import os
import shutil
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox

from config_window.utils import refresh
from paths import DEFAULT_PACK_PATH, PATH, Data, PackPaths


def import_pack(default: bool) -> None:
    pack_zip = filedialog.askopenfile("r", defaultextension=".zip")
    if not pack_zip:
        return

    if not zipfile.is_zipfile(pack_zip.name):
        messagebox.showerror("Error", "Selected file is not a zip file.")
        return

    pack_name = Path(pack_zip.name).with_suffix("").name
    import_location = DEFAULT_PACK_PATH if default else Data.PACKS / pack_name
    relative = import_location.relative_to(PATH)

    if import_location.exists():
        type = "directory" if import_location.is_dir() else "file"
        delete = shutil.rmtree if import_location.is_dir() else os.remove

        confirm = messagebox.askyesno(
            "Confirm",
            f'Pack import location "{relative}" already exists. '
            f"This {type} will be deleted and overwritten. Is this okay?"
            "\n\nNOTE: Importing large packs might take a while, please be patient!",
        )
        if not confirm:
            messagebox.showinfo("Cancelled", "Pack import cancelled.")
            return
        delete(import_location)

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

    messagebox.showinfo("Done", f'Pack imported to "{relative}". Refreshing config window.')
    refresh()


def export_pack() -> None:
    export_location = filedialog.asksaveasfile("w", defaultextension=".zip")
    with zipfile.ZipFile(export_location.name, "w", compression=zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(DEFAULT_PACK_PATH):
            root_path = Path(root)

            for file in files:
                zip.write(root_path / file, file if root_path == DEFAULT_PACK_PATH else os.path.join(root_path.name, file))

            for dir in dirs:
                zip.write(root_path / dir, dir)

    messagebox.showinfo("Done", f'Pack exported to "{export_location.name}".')
