from global_imports import *
import global_variables as gv

class Hsv(ctk.CTkToplevel):
    """Hue Saturation Value"""
    def __init__(self, draw_image_func, on_apply_func):
        super().__init__()
        eof_main_width = int(self.winfo_screenwidth() / 2 + self.winfo_screenwidth() / 3.4)
        eof_main_height = int(self.winfo_screenheight() / 2 - self.winfo_screenheight() / 3)
        self.geometry(f"360x220+{eof_main_width + 10}+{eof_main_height}")
        self.title("HSV")
        self.protocol("WM_DELETE_WINDOW", self.__on_cancel)
        self.resizable(False, False)

        self.draw_image = draw_image_func
        self.on_apply_func = on_apply_func

        self.image_on_open = gv.IMAGES[gv.ACTIVE_INDEX].get_current_layer_image()

        self.alpha = self.image_on_open[:, :, 3]

        self.h_channel, self.s_channel, self.v_channel = cv2.split(cv2.cvtColor(self.image_on_open, cv2.COLOR_BGR2HSV))

        # NumPy cant dynamically change type, so adding over 255 or subtracting below 0 would run into error
        self.h_channel = self.h_channel.astype(np.int16)
        self.s_channel = self.s_channel.astype(np.int16)
        self.v_channel = self.v_channel.astype(np.int16)

        self.h = tk.IntVar()
        self.s = tk.IntVar()
        self.v = tk.IntVar()
        self.preview = tk.BooleanVar()
        self.preview.set(True)

        self.h.trace_add('write', self.__on_value_change)
        self.s.trace_add('write', self.__on_value_change)
        self.v.trace_add('write', self.__on_value_change)
        self.preview.trace_add('write', self.__on_preview_change)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        Slider(self, variable=self.h, s_range=(-100, 100)).grid(row=0, column=0, columnspan=3, padx=10, pady=(10,0), sticky='nsew')
        Slider(self, variable=self.s, s_range=(-100, 100)).grid(row=1, column=0, columnspan=3, padx=10, pady=(10,0), sticky='nsew')
        Slider(self, variable=self.v, s_range=(-100, 100)).grid(row=2, column=0, columnspan=3, padx=10, pady=(10,0), sticky='nsew')

        ctk.CTkCheckBox(self, height=25, text='Preview', variable=self.preview).grid(row=3, column=1, columnspan=1, padx=10, pady=(10,0), sticky='nsew')

        Button(self, text="Apply",  command=self.__on_apply) .grid(row=4, column=0, columnspan=1, padx=10, pady=10, sticky='nsew')
        Button(self, text="Cancel", command=self.__on_cancel).grid(row=4, column=2, columnspan=1, padx=10, pady=10, sticky='nsew')

    def close(self):
        self.destroy()
        gv.allow_edit_window_open = True

    def __on_apply(self):
        self.preview.set(True)
        self.__on_value_change()
        gv.IMAGES[gv.ACTIVE_INDEX].save_history_state('HSV')
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

        h_channel = (self.h_channel + self.h.get())
        s_channel = (self.s_channel + self.s.get())
        v_channel = (self.v_channel + self.v.get())

        # clipping at 0, 255 prevents values below 0 to jump back to uint8 max
        image = np.clip(cv2.merge([h_channel, s_channel, v_channel]), 0, 255).astype(np.uint8)
        # cvtColor requires correct datatype (uint8) so its required to first change type
        image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        image[:, :, 3] = self.alpha

        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(image)

        self.draw_image()

    def __on_preview_change(self, *args):
        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(self.image_on_open)
        self.__on_value_change()
        self.draw_image()
