from global_imports import *
import global_variables as gv

class ImageDisplay(tk.Canvas):
    def __init__(self, parent):
        super().__init__(master=parent, background=gv.BACKGROUND_LIGHT, bd=0, highlightthickness=0, relief='ridge')
        self.grid(row=1, column=0, sticky='nsew')
        # Bind events for zooming and panning
        self.zoom_factor = 1.0

        self.bind('<MouseWheel>', parent.zoom_image)
        self.bind('<ButtonPress-1>', parent.on_mouse_press)
        self.bind('<B1-Motion>', parent.on_move_press)
