import global_variables as gv
import customtkinter as ctk

class Slider(ctk.CTkSlider):
    def __init__(self, master, variable, s_range: tuple):
        super().__init__(master,
                         variable=variable,
                         from_=s_range[0],
                         to=s_range[1],
                         corner_radius=5,
                         border_width=3,
                         fg_color=gv.BACKGROUND_DARK,
                         button_color=gv.LIGHT_GREY,
                         button_hover_color=gv.BUTTON_HOVER,
                         progress_color=gv.BACKGROUND_MIDDLE,
                         border_color=gv.BUTTON_BORDER
                         )
