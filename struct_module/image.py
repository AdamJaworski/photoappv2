import numpy as np

import global_variables as gv
from global_imports import *

class ImageW:
    layers: list
    history: list
    ratio: float
    size: tuple

    def __init__(self, layer_name, image, colorspace):
        self.__top_layers = None
        self.__bottom_layers = None
        self.__transparent_alpha_layer = None
        self.__active_layer_index = 0

        self.original_size = (image.shape[0], image.shape[1])
        self.original_image = image.copy()
        self.original_colorspace = colorspace

        self.layers = []
        self.layers.append(Layer(layer_name, image, colorspace, 0))
        self.next_layer_id = 1

        self.history = []
        self.history.append(History('open', self.original_image, self.layers[0]))

        self.ratio = image.shape[0] / image.shape[1]
        self.size = (image.shape[0], image.shape[1])

        self.__recalculate_dummy_alpha()
        self.__compress_top_layers()
        self.__compress_bottom_layers()

    def save_history_state(self, operation_name: str):
        """Adds state to history"""
        self.history.append(History(operation_name, self.get_current_layer_image(), self.layers[self.__active_layer_index]))

    def change_active_layer(self, new_index):
        """Change active layer func is required to recalculate compressed layers above and bellow it"""
        self.__active_layer_index = new_index
        self.__compress_top_layers()
        self.__compress_bottom_layers()

    def change_layer_visibility(self, index):
        """Changing visibility , based on index of the layer will require to recalculate compressed layers"""
        pass

    def create_new_layer(self):
        """Adding layer will require compress layers to be recalculated"""
        self.layers.append(Layer(f'Layer {self.next_layer_id}', self.original_image, self.original_colorspace, self.next_layer_id))
        self.next_layer_id += 1

        self.__compress_bottom_layers()

    def get_active_layer_index(self) -> int:
        """Returns active layer index of ImageW instance, required for some external operations like layers"""
        return self.__active_layer_index

    def get_current_layer_image(self) -> np.array:
        return self.layers[self.__active_layer_index].image

    def set_current_layer_image(self, image: np.array):
        self.layers[self.__active_layer_index].image = image

    def get_display_image(self) -> Image:
        if not self.layers[self.__active_layer_index].enable:
            compressed_layers_image = merge_layers(self.__top_layers, self.__transparent_alpha_layer, self.__bottom_layers)
        else:
            compressed_layers_image = merge_layers(self.__top_layers, self.get_current_layer_image(), self.__bottom_layers)

        return compressed_layers_image.astype(gv.DATA_TYPE)

    def __compress_top_layers(self):
        """Pre compress layers before drawing to speed up multilayer workflow"""
        if self.__active_layer_index == 0:
            self.__top_layers = self.__transparent_alpha_layer
        else:
            self.__top_layers = collapse_layers(self.layers[:self.__active_layer_index])

        self.__top_layers = np.ascontiguousarray(self.__top_layers)

    def __compress_bottom_layers(self):
        """Pre compress layers before drawing to speed up multilayer workflow"""
        if self.__active_layer_index == len(self.layers) - 1:
            self.__bottom_layers = self.__transparent_alpha_layer
        else:
            self.__bottom_layers = collapse_layers(self.layers[self.__active_layer_index + 1:])

        self.__bottom_layers = np.ascontiguousarray(self.__bottom_layers)

    def __recalculate_dummy_alpha(self):
        __transparent_alpha = np.zeros((self.size[0], self.size[1]), dtype=gv.DATA_TYPE)
        self.__transparent_alpha_layer = np.ascontiguousarray(cv2.merge([__transparent_alpha, __transparent_alpha, __transparent_alpha, __transparent_alpha]))

    def resize(self, new_size: tuple, interpolation):
        self.size = new_size
        for layer in self.layers:
            layer.image = cv2.resize(layer.original_image, new_size[::-1], interpolation=interpolation)
        self.__recalculate_dummy_alpha()
    
    def debug(self):
        cv2.imshow('top_layer', self.__top_layers)
        cv2.imshow('mid_layer', self.get_current_layer_image())
        cv2.imshow('bottom_layer', self.__bottom_layers)


class Layer:
    name: str
    image: np.array
    colorspace: str
    enable: bool
    id: int

    def __init__(self, layer_name, image, colorspace, id_int):
        self.original_image = image.copy()
        self.name = layer_name
        self.image = image
        self.colorspace = colorspace
        self.id = id_int
        self.enable = True


class History:
    """History saves image after operation"""
    def __init__(self, name, image, layer):
        self.name = f'{layer.name}:  {name}'
        self.layer_id = layer.id
        self.state = image


def collapse_layers(layer_list: list):
    """layer_list is list of Layers:
        class Layer:
            name: str
            image: np.array
            colorspace: str
            enable: bool
            id: int
    """
    if len(layer_list) == 0:
        raise RuntimeError("Got empty list as input")

    if len(layer_list) == 1:
        return layer_list[0].image

    # Initialize output image (bottom layer) and its alpha
    out_im = layer_list[-1].image[:, :, :3].astype(np.float64) / 255
    alpha = layer_list[-1].image[:, :, 3].astype(np.float64) / 255

    # Iterate over the remaining layers from bottom to top
    for layer in reversed(layer_list[:len(layer_list) - 1]):
        if not layer.enable:
            continue

        # Extract top layer alpha and color
        alpha_new = layer.image[:, :, 3].astype(np.float64) / 255
        image = layer.image[:, :, :3].astype(np.float64) / 255

        # Store old alpha before updating
        old_alpha = alpha
        # Compute new alpha according to alpha compositing formula
        alpha = alpha_new + old_alpha * (1 - alpha_new)

        # Compute the new composite color
        # C_out = (C_f * α_f + C_b * α_b * (1 - α_f)) / α_out
        out_im = (
            image * alpha_new[:, :, None] +
            out_im * old_alpha[:, :, None] * (1 - alpha_new[:, :, None])
        ) / np.clip(alpha[:, :, None], 1e-8, 1.0)

    # Combine the final composite color with the final alpha
    out_im = np.dstack([out_im, alpha])

    # Convert back to uint8
    return np.clip(out_im * 255, 0, 255).astype(np.uint8)

@njit(fastmath=True, parallel=True)
def merge_layers(foreground, mid_layer, background):
    """
    Merge three RGBA layers (foreground over mid_layer over background)
    using Porter-Duff 'over' in one pass, in a Numba-accelerated loop.

    Parameters
    ----------
    foreground : np.ndarray, shape (H, W, 4), dtype=uint8
    mid_layer  : np.ndarray, shape (H, W, 4), dtype=uint8
    background : np.ndarray, shape (H, W, 4), dtype=uint8

    Returns
    -------
    output : np.ndarray, shape (H, W, 4), dtype=uint8
        The merged RGBA image.
    """
    h, w, _ = foreground.shape
    
    # Prepare the output array
    output = np.empty((h, w, 4), dtype=np.uint8)
    
    for i in prange(h):
        for j in range(w):
            # ---------------------
            # Load Foreground pixel
            # ---------------------
            fr = foreground[i, j, 0]
            fg = foreground[i, j, 1]
            fb = foreground[i, j, 2]
            fa = foreground[i, j, 3]
            
            # ---------------------
            # Load Mid-layer pixel
            # ---------------------
            mr = mid_layer[i, j, 0]
            mg = mid_layer[i, j, 1]
            mb = mid_layer[i, j, 2]
            ma = mid_layer[i, j, 3]
            
            # ---------------------
            # Load Background pixel
            # ---------------------
            br = background[i, j, 0]
            bg_ = background[i, j, 1]
            bb = background[i, j, 2]
            ba = background[i, j, 3]
            
            # Convert to floating [0..1] to do alpha compositing
            fr_f = fr / 255.0
            fg_f = fg / 255.0
            fb_f = fb / 255.0
            fa_f = fa / 255.0
            
            mr_f = mr / 255.0
            mg_f = mg / 255.0
            mb_f = mb / 255.0
            ma_f = ma / 255.0
            
            br_f = br / 255.0
            bg_f = bg_ / 255.0
            bb_f = bb / 255.0
            ba_f = ba / 255.0
            
            # -----------------------------------------
            # Step 1: Composite Foreground over Mid-layer
            # -----------------------------------------
            a_fg_mid = fa_f + ma_f * (1.0 - fa_f)
            if a_fg_mid < 1e-8:
                # Edge case: combined alpha is ~0
                fg_mid_r = 0.0
                fg_mid_g = 0.0
                fg_mid_b = 0.0
            else:
                inv = 1.0 / a_fg_mid
                fg_mid_r = (fr_f * fa_f + mr_f * ma_f * (1.0 - fa_f)) * inv
                fg_mid_g = (fg_f * fa_f + mg_f * ma_f * (1.0 - fa_f)) * inv
                fg_mid_b = (fb_f * fa_f + mb_f * ma_f * (1.0 - fa_f)) * inv
            
            # -----------------------------------------
            # Step 2: Composite (FG over Mid) over Background
            # -----------------------------------------
            a_out = a_fg_mid + ba_f * (1.0 - a_fg_mid)
            if a_out < 1e-8:
                # Edge case: final alpha is ~0
                out_r = 0.0
                out_g = 0.0
                out_b = 0.0
            else:
                inv_out = 1.0 / a_out
                out_r = (fg_mid_r * a_fg_mid + br_f * ba_f * (1.0 - a_fg_mid)) * inv_out
                out_g = (fg_mid_g * a_fg_mid + bg_f  * ba_f * (1.0 - a_fg_mid)) * inv_out
                out_b = (fg_mid_b * a_fg_mid + bb_f  * ba_f * (1.0 - a_fg_mid)) * inv_out
            
            # -----------------------------------------
            # Store in output, back to [0..255]
            # -----------------------------------------
            output[i, j, 0] = np.uint8(out_r * 255.0)
            output[i, j, 1] = np.uint8(out_g * 255.0)
            output[i, j, 2] = np.uint8(out_b * 255.0)
            output[i, j, 3] = np.uint8(a_out * 255.0)
    
    return output