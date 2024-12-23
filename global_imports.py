from pillow_heif import register_heif_opener
from gui import *
import cv2
import numpy as np
import tkinter as tk
import customtkinter as ctk
import time
from PIL import Image, ImageTk
from numba import njit, prange



register_heif_opener()

DEBUG = False

def printf(string: str):
    if DEBUG:
        print(string)