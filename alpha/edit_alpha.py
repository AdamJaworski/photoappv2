from global_imports import *
import global_variables as gv

class EditAlpha(ctk.CTkToplevel):
    """Block-like alpha edit"""
    def __init__(self, parent, draw_image_func, on_apply_func):
        super().__init__()
        self.transient(parent)

        eof_main_width = int(self.winfo_screenwidth() / 2 + self.winfo_screenwidth() / 3.4)
        eof_main_height = int(self.winfo_screenheight() / 2 - self.winfo_screenheight() / 3)
        self.geometry(f"320x160+{eof_main_width + 10}+{eof_main_height}")
        self.title("Fill alpha")
        self.protocol("WM_DELETE_WINDOW", self.__on_cancel)
        self.resizable(False, False)

        self.draw_image    = draw_image_func
        self.on_apply_func = on_apply_func

        self.image_on_open = gv.IMAGES[gv.ACTIVE_INDEX].get_current_layer_image()
        self.alpha_on_open = gv.IMAGES[gv.ACTIVE_INDEX].get_current_layer_image()[:, :, 3] # alpha
        self.grey_scale_im = cv2.cvtColor(gv.IMAGES[gv.ACTIVE_INDEX].get_current_layer_image(), cv2.COLOR_BGRA2GRAY)

        self.preview = ctk.CTkOptionMenu()

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        LabeledSlider(self, text='Value', variable=self.value, s_range=(0, 255)).grid(row=0, column=0, columnspan=3, padx=10, sticky='nsew')

        ctk.CTkCheckBox(self, height=25, text='Preview', variable=self.preview).grid(row=1, column=1, columnspan=1, padx=10, pady=(10,0), sticky='nsew')

        Button(self, text="Cancel", command=self.__on_cancel).grid(row=2, column=0, columnspan=1, padx=10, pady=10, sticky='nsew')
        Button(self, text="Apply", command=self.__on_apply).grid(row=2, column=2, columnspan=1, padx=10, pady=10, sticky='nsew')

        self.value.set(128)

    def close(self):
        self.destroy()
        gv.allow_edit_window_open = True

    def __on_apply(self):
        self.preview.set(True)
        self.__on_value_change()
        gv.IMAGES[gv.ACTIVE_INDEX].save_history_state('Fill alpha')
        self.on_apply_func()
        self.close()

    def __on_cancel(self):
        self.preview.set(False)
        self.__on_preview_change()
        self.close()

    def __on_value_change(self, *args):
        # if preview is disable
        if not self.preview.get():
            return

        image = self.image_on_open.copy()
        image[:, :, 3] = np.ones((self.image_on_open.shape[0], self.image_on_open.shape[1]), dtype=np.uint8) * self.value.get()

        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(image)

        self.draw_image()

    def __on_preview_change(self, *args):
        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(self.image_on_open)
        self.__on_value_change()
        self.draw_image()
