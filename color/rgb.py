from global_imports import *
import global_variables as gv

class Rgb(ctk.CTkToplevel):
    """Red Green Blue"""
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

        self.b_channel, self.g_channel, self.r_channel, self.alpha = cv2.split(self.image_on_open)

        # NumPy cant dynamically change type, so adding over 255 or subtracting below 0 would run into error
        self.r_channel = self.r_channel.astype(np.int16)
        self.g_channel = self.g_channel.astype(np.int16)
        self.b_channel = self.b_channel.astype(np.int16)

        self.r = tk.IntVar()
        self.g = tk.IntVar()
        self.b = tk.IntVar()
        self.preview = tk.BooleanVar()
        self.preview.set(True)

        self.r.trace_add('write', self.__on_value_change)
        self.g.trace_add('write', self.__on_value_change)
        self.b.trace_add('write', self.__on_value_change)
        self.preview.trace_add('write', self.__on_preview_change)

        ctk.CTkSlider(self, width=350, height=20, variable=self.b, from_=-100, to=100).pack(pady=7)
        ctk.CTkSlider(self, width=350, height=20, variable=self.g, from_=-100, to=100).pack(pady=7)
        ctk.CTkSlider(self, width=350, height=20, variable=self.r, from_=-100, to=100).pack(pady=7)

        ctk.CTkCheckBox(self, height=25, text='Preview', variable=self.preview).pack()

        ctk.CTkButton(self, text="Apply", command=self.__on_apply).pack(pady=10)
        ctk.CTkButton(self, text="Cancel", command=self.__on_cancel).pack()

    def close(self):
        self.destroy()
        gv.allow_edit_window_open = True

    def __on_apply(self):
        self.preview.set(True)
        self.__on_value_change()
        gv.IMAGES[gv.ACTIVE_INDEX].save_history_state('RGB')
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

        r_channel = (self.r_channel + self.r.get())
        g_channel = (self.g_channel + self.g.get())
        b_channel = (self.b_channel + self.b.get())

        # clipping at 0, 255 prevents values below 0 to jump back to uint8 max
        image = np.clip(cv2.merge([b_channel, g_channel, r_channel]), 0, 255).astype(np.uint8)
        # cvtColor requires correct datatype (uint8) so its required to first change type

        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        image[:, :, 3] = self.alpha

        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(image)

        self.draw_image()

    def __on_preview_change(self, *args):
        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(self.image_on_open)
        self.__on_value_change()
        self.draw_image()
