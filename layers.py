import cv2

from global_imports import *
import global_variables as gv

class Layers(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__()
        self.transient(parent)

        eof_main_width = int(self.winfo_screenwidth() / 2 + self.winfo_screenwidth() / 3.4)
        eof_main_height = int(self.winfo_screenheight() / 2 + self.winfo_screenheight() / 3)
        self.geometry(f"370x220+{eof_main_width + 10}+{eof_main_height - 220}")
        self.title("Layers")
        self.protocol("WM_DELETE_WINDOW", None)
        self.resizable(False, True)

        self.inter = cv2.INTER_AREA

        self.layer_frames = []
        self.images = []
        self.alpha = []
        self.canvas_list = []
        self.canvas_list_alpha = []
        self.__refresh_layers()



    def __refresh_layers(self):
        self.images = []
        """Required to store instances of images in layer canvas - without it GC would remove image"""
        self.alpha = []
        self.canvas_list = []
        self.canvas_list_alpha = []
        for frame in self.layer_frames:
            frame.destroy()

        for i in range(len(gv.IMAGES[gv.ACTIVE_INDEX].layers)):
            self.grid_columnconfigure(i, weight=1)
            frame = ctk.CTkFrame(self, fg_color=gv.DARK_BLUE, height=50)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="ew")

            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_columnconfigure(2, weight=1)

            new_w, new_h = self.__get_height_n_width()

            canvas = tk.Canvas(master=frame, width=new_w, height=new_h, bd=0, highlightthickness=0, relief='ridge', background=gv.DARK_BLUE)
            canvas.grid(row=0, column=0,padx=(20,0), pady=5)

            canvas2 = tk.Canvas(master=frame, width=new_w, height=new_h, bd=0, highlightthickness=0, relief='ridge', background=gv.DARK_BLUE)
            canvas2.grid(row=0, column=1,padx=(0,20), pady=5)

            tk_image = cv2.resize(cv2.cvtColor(gv.IMAGES[gv.ACTIVE_INDEX].layers[i].image, cv2.COLOR_BGRA2BGR), (int(new_w), int(new_h)), interpolation=self.inter)
            alpha = cv2.resize(gv.IMAGES[gv.ACTIVE_INDEX].layers[i].image[:, :, 3], (int(new_w), int(new_h)), interpolation=self.inter)

            tk_image = ImageTk.PhotoImage(Image.fromarray(tk_image))
            alpha = ImageTk.PhotoImage(Image.fromarray(alpha))

            self.images.append(tk_image)
            self.alpha.append(alpha)

            canvas.create_image(0, 0, anchor='nw', image=tk_image)
            canvas2.create_image(0, 0, anchor='nw', image=alpha)

            self.canvas_list.append(canvas)
            self.canvas_list_alpha.append(canvas2)

            label = ctk.CTkLabel(frame, text=gv.IMAGES[gv.ACTIVE_INDEX].layers[i].name, text_color=gv.BACKGROUND_LIGHT)
            label.grid(row=0, column=3, padx=20, pady=5)

            self.layer_frames.append(frame)

        self.layer_frames[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()].configure(fg_color=gv.LIGHT_GREY)

    def refresh_active_layer_image(self):
        new_w, new_h = self.__get_height_n_width()

        image = gv.IMAGES[gv.ACTIVE_INDEX].layers[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()].image
        tk_image = cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGRA2BGR), (int(new_w), int(new_h)), interpolation=self.inter)
        tk_image = ImageTk.PhotoImage(Image.fromarray(tk_image))

        alpha = cv2.resize(image[:, :, 3], (int(new_w), int(new_h)), interpolation=self.inter)
        alpha = ImageTk.PhotoImage(Image.fromarray(alpha))
        self.canvas_list[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()].delete('all')
        self.canvas_list_alpha[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()].delete('all')
        self.images[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()] = tk_image
        self.alpha[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()] = alpha
        self.canvas_list[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()].create_image(0, 0, anchor=tk.NW, image=tk_image)
        self.canvas_list_alpha[gv.IMAGES[gv.ACTIVE_INDEX].get_active_layer_index()].create_image(0, 0, anchor=tk.NW, image=alpha)

    @staticmethod
    def __get_height_n_width():
        if gv.IMAGES[gv.ACTIVE_INDEX].ratio > 1:
            new_h = 40
            new_w = new_h / gv.IMAGES[gv.ACTIVE_INDEX].ratio
        else:
            new_w = 70
            new_h = new_w * gv.IMAGES[gv.ACTIVE_INDEX].ratio
        return new_w, new_h