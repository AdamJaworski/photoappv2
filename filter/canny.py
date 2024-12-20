from global_imports import *
import global_variables as gv

class Canny(ctk.CTkToplevel):
    """Brightness Contrast"""
    def __init__(self, parent, draw_image_func, on_apply_func):
        super().__init__(fg_color=gv.BACKGROUND_DARK)
        self.transient(parent)

        eof_main_width = int(self.winfo_screenwidth() / 2 + self.winfo_screenwidth() / 3.4)
        eof_main_height = int(self.winfo_screenheight() / 2 - self.winfo_screenheight() / 3)
        self.geometry(f"380x230+{eof_main_width + 10}+{eof_main_height}")
        self.title("Canny")
        self.protocol("WM_DELETE_WINDOW", self.__on_cancel)
        self.resizable(False, False)

        self.draw_image    = draw_image_func
        self.on_apply_func = on_apply_func

        self.image_on_open = gv.IMAGES[gv.ACTIVE_INDEX].get_current_layer_image()
        self.alpha = self.image_on_open[:, :, 3]

        self.threshold1 = tk.IntVar()
        self.threshold2 = tk.IntVar()
        self.contrast = tk.DoubleVar(value=1.0)

        self.preview = tk.BooleanVar()
        self.preview.set(True)

        self.invert = tk.BooleanVar()
        self.invert.set(False)

        self.threshold1.trace_add('write', self.__on_value_change)
        self.threshold2.trace_add('write', self.__on_value_change)

        self.preview.trace_add('write', self.__on_preview_change)
        self.invert.trace_add('write', self.__on_preview_change)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        LabeledSlider(self, text='Threshold 1', variable=self.threshold1, s_range=(0, 720)).grid(row=0, column=0, columnspan=3, padx=10, sticky='nsew')
        LabeledSlider(self, text='Threshold 2', variable=self.threshold2, s_range=(0, 720)).grid(row=1, column=0, columnspan=3, padx=10, sticky='nsew')
        ctk.CTkCheckBox(self, height=25, text='Preview', variable=self.preview).grid(row=2, column=0, columnspan=1, padx=10, pady=(10,0), sticky='nsew')
        ctk.CTkCheckBox(self, height=25, text='Invert', variable=self.invert).grid(row=2, column=2, columnspan=1, padx=10, pady=(10,0), sticky='nsew')

        Button(self, text="Cancel", command=self.__on_cancel).grid(row=3, column=0, columnspan=1, padx=10, pady=10, sticky='nsew')
        Button(self, text="Apply as an alpha", command=self.__on_mask_apply).grid(row=3, column=1, columnspan=1, padx=10, pady=10, sticky='nsew')
        Button(self, text="Apply", command=self.__on_apply).grid(row=3, column=2, columnspan=1, padx=10, pady=10, sticky='nsew')

        self.__on_value_change()

    def close(self):
        self.destroy()
        gv.allow_edit_window_open = True

    def __on_apply(self):
        self.preview.set(True)
        self.__on_value_change()
        gv.IMAGES[gv.ACTIVE_INDEX].save_history_state('Canny')
        self.on_apply_func()
        self.close()

    def __on_mask_apply(self):
        image = cv2.Canny(self.image_on_open, self.threshold1.get(), self.threshold2.get())
        if self.invert.get():
            image = (((image / 255).astype(np.uint8) ^ 1) * 255).astype(np.uint8)

        self.image_on_open[:, :, 3] = image
        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(self.image_on_open)
        gv.IMAGES[gv.ACTIVE_INDEX].save_history_state('Canny')
        self.on_apply_func()
        self.close()
        self.draw_image()

    def __on_cancel(self):
        self.preview.set(False)
        self.__on_preview_change()
        self.close()

    def __on_value_change(self, *args):
        # if preview is disable
        if not self.preview.get():
            return

        image = cv2.Canny(self.image_on_open, self.threshold1.get(), self.threshold2.get())
        if self.invert.get():
            image = (((image / 255).astype(np.uint8) ^ 1) * 255).astype(np.uint8)

        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
        image[:, :, 3] = self.alpha

        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(image)
        self.draw_image()

    def __on_preview_change(self, *args):
        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(self.image_on_open)
        self.__on_value_change()
        self.draw_image()
