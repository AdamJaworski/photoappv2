from global_imports import *
import global_variables as gv


class ActionBar(ctk.CTkToplevel):
    def __init__(self):
        super().__init__(fg_color=gv.BACKGROUND_DARK)
        # Geometry
        center_x = int(self.winfo_screenwidth() / 2 - int(self.winfo_screenwidth() / 1.7) / 2)
        y_offset = int(self.winfo_screenheight() / 10)
        self.y_height = int(self.winfo_screenheight() / 30)
        self.x_width = int(self.winfo_screenwidth() / 1.7)
        self.geometry(f'{self.x_width}x{self.y_height}+{center_x}+{y_offset}')

        self.title("")
        self.attributes('-topmost', True)
        self.overrideredirect(False)
        self.protocol("WM_DELETE_WINDOW")
        self.resizable(False, False)

        self.create_tab(file, ["Open", "Save", "Save as..", "Close", "Settings"], 'File')
        self.create_tab(image, ["Resize"], 'Image')
        self.create_tab(color, ["HSV", "RGB", "Brightness/Contrast"], 'Color')
        self.create_tab(filter, ["Blur", "Canny", "Vignette"], 'Filter')


    def create_tab(self, command, values, keyword):
        tab = ctk.CTkOptionMenu(self,
                                height=int(self.y_height * 0.9),
                                width=int(self.x_width / 10),
                                values=values,
                                command=lambda x : command(tab, keyword, x),
                                hover=True,
                                corner_radius=0,
                                fg_color=gv.BACKGROUND_MIDDLE,
                                button_color=gv.BACKGROUND_MIDDLE,
                                button_hover_color=gv.BACKGROUND_LIGHT)
        tab.set(keyword)
        tab.pack(side='left', padx=1)

def file(tab, title, choice):
    tab.set(title)
    match choice:
        case 'Open':
            pass
        case 'Save':
            pass
        case 'Save as..':
            pass
        case 'Close':
            pass
        case 'Settings':
            pass

def image(tab, title, choice):
    tab.set(title)
    match choice:
        case 'Resize':
            pass


def color(tab, title, choice):
    tab.set(title)
    match choice:
        case 'HSV':
            pass
        case 'RGB':
            pass
        case 'Brightness/Contrast':
            pass


def filter(tab, title, choice):
    tab.set(title)
    match choice:
        case 'Blur':
            pass
        case 'Canny':
            pass
        case 'Vignette':
            pass