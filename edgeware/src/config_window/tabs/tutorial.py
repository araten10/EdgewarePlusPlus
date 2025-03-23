import textwrap
from tkinter import (
    CENTER,
    GROOVE,
    RAISED,
    Frame,
    Label,
    Message,
    Misc,
    ttk,
)
from tkinter.font import Font

from config_window.utils import set_widget_states
from config_window.vars import Vars
from pack import Pack
from widgets.scroll_frame import ScrollFrame

TUTORIAL_TEST = "Magni et ipsum illo tempore qui ut sunt. Tempore voluptatibus odit nesciunt. Nihil aut modi corporis placeat eligendi. Qui distinctio voluptatem laborum molestiae necessitatibus ratione.\n\nQui sint autem voluptatem. Eveniet quo voluptatem sed voluptas ut quo. Ratione vel et adipisci qui totam. Voluptatum impedit blanditiis veritatis iusto asperiores. Quis incidunt temporibus et. Illo quibusdam sunt quo dolor.\n\nNostrum qui dolore fugit molestiae blanditiis a. Ab dolorem illo sint aut modi. Quae molestiae corrupti esse esse iusto itaque harum.\n\nCupiditate est odio qui soluta consectetur pariatur maiores. Ut et odio soluta voluptatum. Dolorem accusantium cumque consequuntur.\n\nPerspiciatis dolores ducimus sed enim animi quaerat distinctio cumque. Enim delectus natus ut aperiam excepturi. Rem saepe sed quod neque sapiente possimus et dolor. In corrupti ratione ab dignissimos provident dolorem corrupti aut. Tempore quisquam facere non quod perferendis ut autem."

class TutorialTab(Frame):
    def __init__(self, vars: Vars, title_font: Font):
        super().__init__()

        tutorial_frame = Frame(self)
        tutorial_frame.pack(expand=1, fill="both")
        tutorial_notebook = ttk.Notebook(tutorial_frame, style="lefttab.TNotebook")
        tutorial_notebook.pack(expand=1, fill="both")

        tab_about = ScrollFrame()
        tutorial_notebook.add(tab_about, text="About")
        Label(tab_about.viewPort, text=TUTORIAL_TEST, anchor="nw", wraplength=460).pack()

        tab_drive = ScrollFrame()
        tutorial_notebook.add(tab_drive, text="Hard Drive")
        Label(tab_drive.viewPort, text=TUTORIAL_TEST, anchor="nw", wraplength=460).pack()

        tab_hibernate_type = ScrollFrame()
        tutorial_notebook.add(tab_hibernate_type, text="Hibernate Types")
        Label(tab_hibernate_type.viewPort, text=TUTORIAL_TEST, anchor="nw", wraplength=460).pack()

        tab_file = ScrollFrame()
        tutorial_notebook.add(tab_file, text="File")
        Label(tab_file.viewPort, text=TUTORIAL_TEST, anchor="nw", wraplength=460).pack()
