from global_imports import *
import global_variables as gv
from color.hsv import Hsv
from color.rgb import Rgb

class ActionBar(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(fg_color=gv.BACKGROUND_DARK)
        self.draw_function = parent.draw_image
        self.after_image_operation_apply = parent.after_image_operation_apply

        # Geometry
        center_x = int(self.winfo_screenwidth() / 2 - int(self.winfo_screenwidth() / 1.7) / 2)
        y_offset = int(self.winfo_screenheight() / 10)
        self.y_height = int(self.winfo_screenheight() / 30)
        self.x_width = int(self.winfo_screenwidth() / 2.7)
        self.geometry(f'{self.x_width}x{self.y_height}+{center_x}+{y_offset}')

        self.child = None

        self.title("")
        self.overrideredirect(False)
        self.protocol("WM_DELETE_WINDOW", self.disable_event)
        self.resizable(False, False)

        self.create_tab(self.file, ["Open", "Save", "Save as..", "Close", "Settings"], 'File')
        self.create_tab(self.image, ["Resize"], 'Image')
        self.create_tab(self.color, ["HSV", "RGB", "Brightness/Contrast"], 'Color')
        self.create_tab(self.filter_f, ["Blur", "Canny", "Vignette"], 'Filter')
        self.create_tab(self.view, ["Fit on screen", "Reset viewport"], 'View')

    def disable_event(self):
        pass

    def create_tab(self, command, values, keyword):
        tab = ctk.CTkOptionMenu(self,
                                height=int(self.y_height * 0.9),
                                width=int(self.x_width / 5),
                                values=values,
                                command=lambda x : command(tab, keyword, x),
                                hover=True,
                                corner_radius=0,
                                fg_color=gv.BACKGROUND_MIDDLE,
                                button_color=gv.BACKGROUND_MIDDLE,
                                button_hover_color=gv.BACKGROUND_LIGHT)
        tab.set(keyword)
        tab.pack(side='left', padx=1)

    def file(self, tab, title, choice):
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

    def image(self, tab, title, choice):
        tab.set(title)
        match choice:
            case 'Resize':
                pass


    def color(self, tab, title, choice):
        tab.set(title)
        if not gv.allow_edit_window_open:
            return

        match choice:
            case 'HSV':
                self.child = Hsv(self.draw_function, self.after_image_operation_apply)
            case 'RGB':
                self.child = Rgb(self.draw_function, self.after_image_operation_apply)
            case 'Brightness/Contrast':
                pass

        gv.allow_edit_window_open = False

    def filter_f(self, tab, title, choice):
        tab.set(title)
        match choice:
            case 'Blur':
                pass
            case 'Canny':
                pass
            case 'Vignette':
                pass

    def view(self, tab, title, choice):
        tab.set(title)
        match choice:
            case 'Fit on screen':
                pass
            case 'Reset viewport':
                pass
