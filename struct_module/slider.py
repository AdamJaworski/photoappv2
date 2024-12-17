import global_variables as gv
import customtkinter as ctk

class Slider(ctk.CTkSlider):
    def __init__(self, master, variable, s_range: tuple, width=110, height=10):
        super().__init__(master,
                         width=width,
                         height=height,
                         variable=variable,
                         from_=s_range[0],
                         to=s_range[1],
                         corner_radius=5,
                         border_width=3,
                         fg_color=gv.BACKGROUND_MIDDLE,
                         #hover_color=gv.BUTTON_HOVER,
                         #text_color=gv.BUTTON_TEXT,
                         border_color=gv.BUTTON_BORDER
                         )
