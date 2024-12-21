import customtkinter as ctk
import cv2
import tkinter as tk
import numpy as np
import time

from numba import njit, prange
from PIL import ImageTk, Image
from pillow_heif import register_heif_opener
from struct_module.button import Button
from struct_module.slider import Slider
from struct_module.labeled_slider import LabeledSlider


register_heif_opener()