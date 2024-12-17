import global_variables as gv
import customtkinter as ctk

class Button(ctk.CTkButton):
    def __init__(self, master, command, text, width=110, height=30):
        super().__init__(master,
                         width=width,
                         height=height,
                         command=command,
                         text=text,
                         corner_radius=5,
                         border_width=3,
                         fg_color=gv.BACKGROUND_MIDDLE,
                         hover_color=gv.BUTTON_HOVER,
                         text_color=gv.BUTTON_TEXT,
                         border_color=gv.BUTTON_BORDER
                         )
