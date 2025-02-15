# Edgeware++ Pack Tool

This is a supplementary program to Edgeware++ to aide in creating packs.

## Running

### Windows

Run `PackToolScript.bat` and follow the instructions presented.

### Linux

Run the `setup.sh` script to create a Python virtual environment, install the
required Python packages, and create a script `pack_tool.sh` to run the Pack
Tool through the command line.

Running `./pack_tool.sh -h` lists all available options, but the most important
commands commands to keep in mind are:

Create a new pack to the directory `my_pack`:

```
$ ./pack_tool.sh -n my_pack
```

Compile the pack in `my_pack` to `build` (another output directory can be
specified with `-o`):

```
$ ./pack_tool.sh my_pack
```

## Pack Structure

The pack structure used by Edgeware is well known, but it has several problems
that make creating packs in the format confusing and cumbersome. The structure
uses strange JSON formats, setting up media moods is difficult, and there is
poor discoverability of new features supported by packs.

Despite these problems, the default pack structure has not been changed in
order to maintain compatibility between old and new packs and versions of
Edgeware. That is why the Pack Tool uses a separate pack format in order to
make creating packs easier, and these packs can then be automatically compiled
to the actual format used by Edgeware.

```
.
├── media
│   ├── default
│   │   ├── audio.mp3
│   │   ├── image.png
│   │   ├── video.mp4
│   │   └── ...
│   └── ...
│       ├── audio.mp3
│       ├── image.png
│       ├── video.mp4
│       └── ...
├── subliminals
│   ├── image.gif
│   └── ...
├── wallpapers
│   ├── wallpaper.png
│   └── ...
├── icon.ico
├── loading_splash.{png, gif, jpg, jpeg, bmp}
└── pack.yml
```
