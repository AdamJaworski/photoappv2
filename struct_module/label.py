import customtkinter as ctk

class Label(ctk.CTkLabel):
    def __init__(self, master, text: str):
        super().__init__(master, text=text) #height=None