import global_variables as gv
from global_imports import *
from struct_module.image import ImageW

class ImageImport(ctk.CTkToplevel):
    def __init__(self, on_import_func):
        super().__init__()
        self.on_import_func = on_import_func

        self.geometry("320x150+50+50")
        self.title("Import image")
        self.attributes('-topmost', True)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.url_var = tk.StringVar()

        ctk.CTkEntry(self, height=40, textvariable=self.url_var).pack(fill='x', pady=5, padx=5)

        ctk.CTkButton(self, text="Open", command=self.open).pack(pady=10)
        ctk.CTkButton(self, text="Find", command=self.find).pack()

    def open(self):
        image = Image.open(self.url_var.get())
        image = np.array(image)

        # add alpha channel
        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

        # append image to workplace
        gv.IMAGES.append(ImageW('background', image, 'BGRA'))

        # on import func to refresh gui
        self.close()
        self.on_import_func()

    def find(self):
        self.url_var.set(tk.filedialog.askopenfilename())

    def close(self):
        self.destroy()