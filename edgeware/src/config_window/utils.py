import logging
from tkinter import Frame, Label, Widget

from settings import load_config
from utils import utils

BUTTON_FACE = "SystemButtonFace" if utils.is_windows() else "gray90"

# TODO: Don't load this here
config = load_config()


def all_children(widget: Widget) -> list[Widget]:
    return [widget] + [subchild for child in widget.winfo_children() for subchild in all_children(child)]


def get_live_version() -> str:
    url = "http://raw.githubusercontent.com/araten10/EdgewarePlusPlus/main/edgeware/assets/default_config.json"

    test = config["toggleInternet"]
    if test != 0:
        logging.info("GitHub connection is disabled, version will not be checked.")
        return "Version check disabled!"

    try:
        with open(urllib.request.urlretrieve(url)[0], "r") as liveDCfg:
            return json.loads(liveDCfg.read())["versionplusplus"]
    except Exception as e:
        logging.warning(f"Failed to fetch version on GitHub.\n\tReason: {e}")
        return "Could not check version."


def set_widget_states(state: bool, widgets: list[Widget], demo: str = False):
    theme = config["themeType"].strip()

    # TODO: Use the same Theme objects as the main program
    if theme == "Original" or (config["themeNoConfig"] and not demo):
        set_widget_states_with_colors(state, widgets, BUTTON_FACE, "gray35")
    else:
        if theme == "Dark":
            set_widget_states_with_colors(state, widgets, "#282c34", "gray65")
        if theme == "The One":
            set_widget_states_with_colors(state, widgets, "#282c34", "#37573d")
        if theme == "Ransom":
            set_widget_states_with_colors(state, widgets, "#841212", "#573737")
        if theme == "Goth":
            set_widget_states_with_colors(state, widgets, "#282c34", "#4b3757")
        if theme == "Bimbo":
            set_widget_states_with_colors(state, widgets, "#ffc5cd", "#bc7abf")


def set_widget_states_with_colors(state: bool, widgets: list[Widget], color_on: str, color_off: str):
    for widget in widgets:
        if not (isinstance(widget, Frame) or isinstance(widget, Label)):
            widget.configure(state=("normal" if state else "disabled"))
        widget.configure(bg=(color_on if state else color_off))
