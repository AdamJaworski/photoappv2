import customtkinter as ctk
import cv2
import tkinter as tk
import numpy as np
import time

from numba import njit
from PIL import ImageTk, Image
from pillow_heif import register_heif_opener

register_heif_opener()