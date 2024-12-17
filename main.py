import global_variables as gv
from global_imports import *
from file.import_image import ImageImport
from main_display.image_display import ImageDisplay, CloseImage
from main_display.action_bar import ActionBar
from layers import Layers
from history import History

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
        self.empty_workspace_frame.grid(sticky='nsew')

        ctk.CTkButton(self.empty_workspace_frame, text='Open Image', command=lambda: ImageImport(self.on_first_image)).pack(expand=True)

        self.mainloop()

    def after_image_operation_apply(self):
        """Call this function after applying operation to image e.g. HSV"""
        self.layers.refresh_active_layer_image()
        self.history.refresh_history()

    def draw_image(self):
        self.image_output.delete('all')
        image = gv.IMAGES[gv.ACTIVE_INDEX].get_display_image()

        new_w = int(gv.IMAGES[gv.ACTIVE_INDEX].size[0] * self.zoom_factor)
        new_h = int(gv.IMAGES[gv.ACTIVE_INDEX].size[1] * self.zoom_factor)

        image = cv2.resize(image, (new_h, new_w), interpolation=cv2.INTER_NEAREST)

        self.imagetk = ImageTk.PhotoImage(Image.fromarray(image))
        self.image_output.create_image(self.image_x, self.image_y, image=self.imagetk, anchor='center')

    def move_image(self):
        self.image_output.delete('all')
        self.image_output.create_image(self.image_x, self.image_y, image=self.imagetk, anchor='center')

    def on_first_image(self):
        self.empty_workspace_frame.grid_forget()
        self.image_output = ImageDisplay(self)
        self.close_button = CloseImage(self, self.close_edit)
        self.layers = Layers()
        self.history = History()

        self.action_bar = ActionBar(self)
        self.draw_image()

    def close_edit(self):
        gv.IMAGES.remove(gv.IMAGES[gv.ACTIVE_INDEX])

        if len(gv.IMAGES) == 0:
            self.close_button.destroy()
            self.image_output.destroy()
            if self.action_bar.child:
                self.action_bar.child.close()
            self.action_bar.destroy()
            self.layers.destroy()
            self.empty_workspace_frame.grid(column=0, columnspan=2, row=0, sticky='nsew')
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
