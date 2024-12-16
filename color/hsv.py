import numpy as np

from global_imports import *
import global_variables as gv

class Hsv(ctk.CTkToplevel):
    def __init__(self, draw_image_func):
        super().__init__()
        eof_main_width = int(self.winfo_screenwidth() / 2 + self.winfo_screenwidth() / 3.4)
        eof_main_height = int(self.winfo_screenheight() / 2 - self.winfo_screenheight() / 3)
        self.geometry(f"360x220+{eof_main_width + 10}+{eof_main_height}")
        self.title("HSV")
        self.protocol("WM_DELETE_WINDOW", self.__on_cancel)
        self.resizable(False, False)

        self.draw_image = draw_image_func

        self.image_on_open = gv.IMAGES[gv.ACTIVE_INDEX].get_current_layer_image()

        self.alpha = self.image_on_open[:, :, 3]

        self.h_channel, self.s_channel, self.v_channel = cv2.split(cv2.cvtColor(self.image_on_open, cv2.COLOR_BGR2HSV))

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

        ctk.CTkSlider(self, width=350, height=20, variable=self.h, from_=-100, to=100).pack(pady=7)
        ctk.CTkSlider(self, width=350, height=20, variable=self.s, from_=-100, to=100).pack(pady=7)
        ctk.CTkSlider(self, width=350, height=20, variable=self.v, from_=-100, to=100).pack(pady=7)

        ctk.CTkCheckBox(self, height=25, text='Preview', variable=self.preview).pack()

        ctk.CTkButton(self, text="Apply", command=self.__on_apply).pack(pady=10)
        ctk.CTkButton(self, text="Cancel", command=self.__on_cancel).pack()

    def close(self):
        self.destroy()
        gv.allow_edit_window_open = True

    def __on_apply(self):
        self.preview.set(True)
        self.__on_value_change()
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

        image = np.clip(cv2.merge([h_channel, s_channel, v_channel]), 0, 255).astype(np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        image[:, :, 3] = self.alpha

        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(image)

        self.draw_image()

    def __on_preview_change(self, *args):
        gv.IMAGES[gv.ACTIVE_INDEX].set_current_layer_image(self.image_on_open)
        self.__on_value_change()
        self.draw_image()
