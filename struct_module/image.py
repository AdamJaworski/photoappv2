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
            compressed_layers_image = merge_layers(self.__top_layers, self.layers[self.__active_layer_index].image, self.__bottom_layers)

        compressed_layers_image[:, :, 3] = np.clip(compressed_layers_image[:, :, 3].astype(np.int16) + 1, 0, 255)
        return compressed_layers_image.astype(gv.DATA_TYPE)

    def __compress_top_layers(self):
        """Pre compress layers before drawing to speed up multilayer workflow"""
        if self.__active_layer_index == 0:
            self.__top_layers = self.__transparent_alpha_layer
        else:
            self.__top_layers = collapse_layers(self.layers[:self.__active_layer_index])

    def __compress_bottom_layers(self):
        """Pre compress layers before drawing to speed up multilayer workflow"""
        if self.__active_layer_index == len(self.layers) - 1:
            self.__bottom_layers = self.__transparent_alpha_layer
        else:
            self.__bottom_layers = collapse_layers(self.layers[self.__active_layer_index + 1:])

    def __recalculate_dummy_alpha(self):
        __transparent_alpha = np.zeros((self.size[0], self.size[1]), dtype=gv.DATA_TYPE)
        self.__transparent_alpha_layer = cv2.merge([__transparent_alpha, __transparent_alpha, __transparent_alpha, __transparent_alpha])

    def resize(self, new_size: tuple, interpolation):
        self.size = new_size
        for layer in self.layers:
            layer.image = cv2.resize(layer.original_image, new_size[::-1], interpolation=interpolation)
        self.__recalculate_dummy_alpha()

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
    if len(layer_list) == 0:
        raise RuntimeError("Got empty list as input")

    if len(layer_list) == 1:
        return layer_list[0].image

    out_im = np.zeros((layer_list[0].image.shape[0], layer_list[0].image.shape[1], 4), dtype=np.float64)
    total_alpha = np.zeros((layer_list[0].image.shape[0], layer_list[0].image.shape[1]), dtype=np.float64)
    for layer in layer_list:
      alpha = np.clip(layer.image[:, :, 3].astype(np.float64)/255 - total_alpha, 0, 1)
      alpha_per_channel = cv2.merge([alpha, alpha, alpha])
      out_im[:, :, :3] += (layer.image[:, :, :3] / 255) * alpha_per_channel
      total_alpha += alpha

    out_im[:, :, 3] = total_alpha

    return np.clip(out_im * 255, 0, 255).astype(np.uint8)

@njit
def merge_layers(top_layer, mid_layer, bottom_layer):
    h, w, _ = top_layer.shape
    output = np.zeros((h, w, 4), dtype=np.uint8)

    for i in range(h):
        for j in range(w):
            # Initialize output color and alpha
            C_out_r, C_out_g, C_out_b = 0.0, 0.0, 0.0
            alpha_out = 0.0

            # Process top layer
            a1 = top_layer[i, j, 3] / 255.0
            if a1 == 1.0:
                # Fully opaque, no need to blend further
                output[i, j] = top_layer[i, j]
                continue
            elif a1 > 0.0:
                r1 = top_layer[i, j, 0] / 255.0
                g1 = top_layer[i, j, 1] / 255.0
                b1 = top_layer[i, j, 2] / 255.0

                alpha_out = a1
                C_out_r = r1
                C_out_g = g1
                C_out_b = b1
            else:
                pass

            # Process mid layer
            a2 = mid_layer[i, j, 3] / 255.0
            if a2 == 1.0 and alpha_out == 0.0:
                output[i, j] = mid_layer[i, j]
                continue
            elif a2 > 0.0:
                r2 = mid_layer[i, j, 0] / 255.0
                g2 = mid_layer[i, j, 1] / 255.0
                b2 = mid_layer[i, j, 2] / 255.0

                alpha_out_new = a2 + alpha_out * (1 - a2)
                C_out_r = (r2 * a2 + C_out_r * alpha_out * (1 - a2)) / alpha_out_new
                C_out_g = (g2 * a2 + C_out_g * alpha_out * (1 - a2)) / alpha_out_new
                C_out_b = (b2 * a2 + C_out_b * alpha_out * (1 - a2)) / alpha_out_new
                alpha_out = alpha_out_new

                if alpha_out >= 1.0:
                    output[i, j, 0] = int(C_out_r * 255)
                    output[i, j, 1] = int(C_out_g * 255)
                    output[i, j, 2] = int(C_out_b * 255)
                    output[i, j, 3] = 255
                    continue
            else:
                pass

            # Process bottom layer
            a3 = bottom_layer[i, j, 3] / 255.0
            if a3 > 0.0:
                r3 = bottom_layer[i, j, 0] / 255.0
                g3 = bottom_layer[i, j, 1] / 255.0
                b3 = bottom_layer[i, j, 2] / 255.0

                alpha_out_new = a3 + alpha_out * (1 - a3)
                C_out_r = (r3 * a3 + C_out_r * alpha_out * (1 - a3)) / alpha_out_new
                C_out_g = (g3 * a3 + C_out_g * alpha_out * (1 - a3)) / alpha_out_new
                C_out_b = (b3 * a3 + C_out_b * alpha_out * (1 - a3)) / alpha_out_new
                alpha_out = alpha_out_new

            # Set the output pixel
            output[i, j, 0] = int(C_out_r * 255)
            output[i, j, 1] = int(C_out_g * 255)
            output[i, j, 2] = int(C_out_b * 255)
            output[i, j, 3] = int(alpha_out * 255)

    return output
