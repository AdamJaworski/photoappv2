from global_imports import *
import global_variables as gv

def create_new_layer(parent, draw_image_func, on_apply_func):
    gv.IMAGES[gv.ACTIVE_INDEX].create_new_layer()
    parent.layers.refresh_layers()
    draw_image_func()