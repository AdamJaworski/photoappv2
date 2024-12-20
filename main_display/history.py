from global_imports import *
import global_variables as gv

class History(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__()
        self.transient(parent)

        eof_main_width = int(self.winfo_screenwidth() / 2 + self.winfo_screenwidth() / 3.4)
        eof_main_height = int(self.winfo_screenheight() / 2 + self.winfo_screenheight() / 3)
        self.geometry(f"220x220+{int((self.winfo_screenwidth() - eof_main_width) / 2.5)}+{eof_main_height - 220}")
        self.title("History")
        self.protocol("WM_DELETE_WINDOW", None)
        self.resizable(False, True)

        self.grid_columnconfigure(0, weight=1)
        self.history_frames = []
        self.refresh_history()

    def refresh_history(self):
        for frame in self.history_frames:
            frame.destroy()

        for i, history_log in enumerate(gv.IMAGES[gv.ACTIVE_INDEX].history):
            self.grid_rowconfigure(i, weight=0)
            frame = ctk.CTkFrame(self, fg_color=gv.DARK_BLUE, height=50)
            frame.grid(row=i, column=0, padx=10, pady=(5,0), sticky="new")

            frame.grid_rowconfigure(0, weight=0)
            frame.grid_columnconfigure(0, weight=0)
            #frame.grid_columnconfigure(1, weight=1)

            label = ctk.CTkLabel(frame, text=history_log.name, text_color=gv.BACKGROUND_LIGHT)
            label.pack(anchor='center')
            #label.grid(row=0, column=0, padx=20, pady=5)

            self.history_frames.append(frame)
