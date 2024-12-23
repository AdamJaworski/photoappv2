import customtkinter as ctk
from gui.slider import Slider
from gui.label import Label
import global_variables as gv

class LabeledSlider(ctk.CTkFrame):
    def __init__(self, master, text: str, variable, s_range, bind_var=True):
        super().__init__(master, fg_color=gv.BACKGROUND_DARK)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.label = Label(self, text)

        self.slider = Slider(self, variable, s_range)

        pady = 5
        self.label.grid(row=0, column=0, padx=5, pady=(pady,0), sticky='nw')
        self.slider.grid(row=1, column=0, padx=5, columnspan=2, pady=(0,pady), sticky='nsew')

        if bind_var:
            self.label_variable = Label(self, '0')
            self.label_variable.grid(row=0, column=1, padx=5, pady=(pady,0), sticky='ne')
            self.variable = variable
            variable.trace_add('write', self.update)

    def update(self, *args):
        self.label_variable.configure(text=str(self.variable.get()))