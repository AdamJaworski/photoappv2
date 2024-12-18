from global_imports import *
import global_variables as gv

class Layers(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__()
        self.transient(parent)

        eof_main_width = int(self.winfo_screenwidth() / 2 + self.winfo_screenwidth() / 3.4)
        eof_main_height = int(self.winfo_screenheight() / 2 + self.winfo_screenheight() / 3)
        self.geometry(f"320x220+{eof_main_width + 10}+{eof_main_height - 220}")
        self.title("Layers")
        self.protocol("WM_DELETE_WINDOW", None)
        self.resizable(False, True)

        self.layer_frames = []
        self.images = []
        self.canvas_list = []
        self.__refresh_layers()


    def __refresh_layers(self):
        self.images = []
        """Required to store instances of images in layer canvas - without it GC would remove image"""
        self.canvas_list = []
        for frame in self.layer_frames:
            frame.destroy()

        for i in range(len(gv.IMAGES[gv.ACTIVE_INDEX].layers)):
            self.grid_columnconfigure(i, weight=1)
            frame = ctk.CTkFrame(self, fg_color=gv.DARK_BLUE, height=50)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="ew")

            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=1)

            new_w, new_h = self.__get_height_n_width()

            canvas = tk.Canvas(master=frame, width=new_w, height=new_h, bd=0, highlightthickness=0, relief='ridge', background=gv.DARK_BLUE)
            canvas.grid(row=0, column=0,padx=20, pady=5)

            tk_image = cv2.resize(gv.IMAGES[gv.ACTIVE_INDEX].layers[i].image, (int(new_w), int(new_h)), interpolation=cv2.INTER_LANCZOS4)
            tk_image = ImageTk.PhotoImage(Image.fromarray(tk_image))
            self.images.append(tk_image)
            canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)

            self.canvas_list.append(canvas)

            label = ctk.CTkLabel(frame, text=gv.IMAGES[gv.ACTIVE_INDEX].layers[i].name, text_color=gv.BACKGROUND_LIGHT)
            label.grid(row=0, column=1, padx=20, pady=5)

            self.layer_frames.append(frame)

        self.layer_frames[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()].configure(fg_color=gv.LIGHT_GREY)

    def refresh_active_layer_image(self):
        new_w, new_h = self.__get_height_n_width()

        tk_image = cv2.resize(gv.IMAGES[gv.ACTIVE_INDEX].layers[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()].image, (int(new_w), int(new_h)),
                              interpolation=cv2.INTER_LANCZOS4)
        tk_image = ImageTk.PhotoImage(Image.fromarray(tk_image))

        self.canvas_list[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()].delete('all')
        self.images[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()] = tk_image
        self.canvas_list[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()].create_image(0, 0, anchor=tk.NW, image=tk_image)

    @staticmethod
    def __get_height_n_width():
        if gv.IMAGES[gv.ACTIVE_INDEX].ratio > 1:
            new_h = 40
            new_w = new_h / gv.IMAGES[gv.ACTIVE_INDEX].ratio
        else:
            new_w = 70
            new_h = new_w * gv.IMAGES[gv.ACTIVE_INDEX].ratio
        return new_w, new_h