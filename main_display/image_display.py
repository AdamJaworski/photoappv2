from global_imports import *
import global_variables as gv

class ImageDisplay(tk.Canvas):
    def __init__(self, parent):
        super().__init__(master=parent, background=gv.BACKGROUND_LIGHT, bd=0, highlightthickness=0, relief='ridge')
        self.grid(row=0, column=0, sticky='nsew')
        # Bind events for zooming and panning
        self.zoom_factor = 1.0

        self.bind('<MouseWheel>', parent.zoom_image)
        self.bind('<ButtonPress-1>', parent.on_button_press)
        self.bind('<B1-Motion>', parent.on_move_press)

class CloseImage(ctk.CTkButton):
    def __init__(self, parent, close_edit):
        super().__init__(master=parent, text='x', text_color='#FFF', fg_color='transparent', width=40, height=40, corner_radius=0, hover_color='#8a0606', command=close_edit)
        self.place(relx=0.99, rely=0.01, anchor='ne')
