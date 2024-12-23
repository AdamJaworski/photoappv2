import global_variables as gv
from global_imports import *
from file.import_image import ImageImport
from main_display.image_display import ImageDisplay
from main_display.action_bar import ActionBar
from main_display.layers import Layers
from main_display.history import History

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.image_output = None
        self.imagetk = None

        self.image_x = 0
        self.image_y = 0
        self.last_x = 0
        self.last_y = 0

        self.zoom_factor = 1.0

        # Geometry
        center_x = int(self.winfo_screenwidth() / 2 - int(self.winfo_screenwidth() / 1.7) / 2)
        center_y = int(self.winfo_screenheight() / 2 - int(self.winfo_screenheight() / 1.5) / 2)

        self.geometry(f'{int(self.winfo_screenwidth() / 1.7)}x{int(self.winfo_screenheight() / 1.5)}+{center_x}+{center_y}')

        ctk.set_appearance_mode('dark')
        self.title('Image Editor')

        # Empty layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Empty frame
        self.empty_workspace_frame = ctk.CTkFrame(self)
        self.empty_workspace_frame.grid(rowspan=2, sticky='nsew')

        Button(self.empty_workspace_frame, text='Open Image', command=lambda: ImageImport(self.on_first_image)).pack(expand=True)

        self.bind('<Configure>', self.resize_grid)
        self.mainloop()


    def resize_grid(self, event):
        minsize = self.winfo_height() - 0.9 * int(self.winfo_screenheight() / 30) - 5
        self.grid_rowconfigure(1, weight=1, minsize=minsize)

    def after_image_operation_apply(self):
        """Call this function after applying operation to image e.g. HSV"""
        self.layers.refresh_active_layer_image()
        self.history.refresh_history()

    def draw_image(self):
        """Function need to render"""
        printf(f'\n{"="*40}')
        start = time.time()
        self.image_output.delete('all')
        image = gv.IMAGES[gv.ACTIVE_INDEX].get_display_image()

        printf(f'Get display: {time.time() - start}')
        start = time.time()

        new_w = int(gv.IMAGES[gv.ACTIVE_INDEX].size[0] * self.zoom_factor)
        new_h = int(gv.IMAGES[gv.ACTIVE_INDEX].size[1] * self.zoom_factor)

        interpolation = cv2.INTER_AREA if self.zoom_factor < 1 else cv2.INTER_LINEAR

        image = cv2.resize(image, (new_h, new_w), interpolation=interpolation)

        printf(f'Resize: {time.time() - start}')
        start = time.time()

        self.imagetk = ImageTk.PhotoImage(Image.fromarray(image))
        self.image_output.create_image(self.image_x, self.image_y, image=self.imagetk, anchor='center')

        printf(f'Draw: {time.time() - start}')
        printf('=' * 40)

    def move_image(self):
        self.image_output.delete('all')
        self.image_output.create_image(self.image_x, self.image_y, image=self.imagetk, anchor='center')

    def on_first_image(self):
        self.empty_workspace_frame.grid_forget()

        self.image_output = ImageDisplay(self)
        self.layers = Layers(self)
        self.history = History(self)

        self.action_bar = ActionBar(self)
        self.draw_image()

    def close_edit(self):
        gv.IMAGES.remove(gv.IMAGES[gv.ACTIVE_INDEX])

        if len(gv.IMAGES) == 0:
            self.image_output.destroy()
            if self.action_bar.child:
                self.action_bar.child.close()
            self.action_bar.destroy()
            self.layers.destroy()
            self.history.destroy()
            self.empty_workspace_frame.grid(column=0, columnspan=2, row=0, rowspan=2, sticky='nsew')
        else:
            self.draw_image()

    def zoom_image(self, event):
        # Adjust zoom factor based on mouse wheel scroll
        if event.delta > 0:
            zoom_delta = 1.1  # Zoom in
        elif event.delta < 0:
            zoom_delta = 0.9  # Zoom out
        else:
            return

        # Calculate new zoom factor
        new_zoom_factor = self.zoom_factor * zoom_delta

        # Limit the zoom factor to prevent excessive zooming
        new_zoom_factor = max(0.1, min(new_zoom_factor, 10))
        # Update zoom factor
        self.zoom_factor = new_zoom_factor

        # Update the image
        self.draw_image()

    def on_mouse_press(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def on_move_press(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.last_x = event.x
        self.last_y = event.y
        self.image_x += dx
        self.image_y += dy
        self.move_image()


if __name__ == "__main__":
    App()
