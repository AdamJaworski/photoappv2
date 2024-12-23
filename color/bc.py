import time

import numpy as np

from global_imports import *
import global_variables as gv

class BrightnessContrast(ctk.CTkToplevel):
    """Brightness Contrast"""
    def __init__(self, parent, draw_image_func, on_apply_func):
        super().__init__(fg_color=gv.BACKGROUND_DARK)
        self.transient(parent)

        eof_main_width = int(self.winfo_screenwidth() / 2 + self.winfo_screenwidth() / 3.4)
        eof_main_height = int(self.winfo_screenheight() / 2 - self.winfo_screenheight() / 3)
        self.geometry(f"360x200+{eof_main_width + 10}+{eof_main_height}")
        self.title("Brightness/Contrast")
        self.protocol("WM_DELETE_WINDOW", self.__on_cancel)
        self.resizable(False, False)

        self.draw_image    = draw_image_func
        self.on_apply_func = on_apply_func

        self.image_on_open = gv.IMAGES[gv.ACTIVE_INDEX].get_current_layer_image()
        self.alpha = self.image_on_open[:, :, 3]

        self.image = cv2.cvtColor(self.image_on_open, cv2.COLOR_BGRA2BGR).astype(np.float64)

        self.brightness = tk.IntVar()
        self.contrast = tk.DoubleVar(value=1.0)

        self.preview = tk.BooleanVar()
        self.preview.set(True)

        self.brightness.trace_add('write', self.__on_value_change)
        self.contrast.trace_add('write', self.__on_value_change)

        self.preview.trace_add('write', self.__on_preview_change)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        LabeledSlider(self, text='Brightness', variable=self.brightness, s_range=(-100, 100)).grid(row=0, column=0, columnspan=3, padx=10, sticky='nsew')
        contrast = LabeledSlider(self, text='Contrast', variable=self.contrast, s_range=(0, 2), bind_var=False)
        contrast.slider.set(1)
        #contrast.slider.configure(number_of_steps=100)
        contrast.grid(row=1, column=0, columnspan=3, padx=10, sticky='nsew')
        ctk.CTkCheckBox(self, height=25, text='Preview', variable=self.preview).grid(row=2, column=1, columnspan=1, padx=10, pady=(10,0), sticky='nsew')

        Button(self, text="Cancel", command=self.__on_cancel).grid(row=3, column=0, columnspan=1, padx=10, pady=10, sticky='nsew')
        Button(self, text="Apply", command=self.__on_apply).grid(row=3, column=2, columnspan=1, padx=10, pady=10, sticky='nsew')

        apply_values(self.image, int(2), float(1.0))

    def close(self):
        self.destroy()
        gv.allow_edit_window_open = True

    def __on_apply(self):
        self.preview.set(True)
        self.__on_value_change()
        gv.IMAGES[gv.ACTIVE_INDEX].save_history_state('Brightness/Contrast')
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

        image = apply_values(self.image, self.brightness.get(), self.contrast.get())
        image = np.clip(image, 0, 255).astype(np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        image[:, :, 3] = self.alpha

        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(image)
        self.draw_image()

    def __on_preview_change(self, *args):
        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(self.image_on_open)
        self.__on_value_change()
        self.draw_image()


@njit(parallel=True) #parallel=True makes it x10 faster
def apply_values(image, brightness, contrast):
    return np.power(np.add(image, brightness), contrast)