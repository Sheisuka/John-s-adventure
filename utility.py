from os import walk
import pygame as pg
from PIL import Image

def import_folder(path):
    surface_list = []
    for _, __, img_names in walk(path):
        for img in img_names:
            full_path = path + '/' + img
            width, height = (Image.open(full_path)).size
            image_surface = pg.transform.scale((pg.image.load(full_path).convert_alpha()), (int(width * 1.5), int(height * 1.5)))

            surface_list.append(image_surface)

    return surface_list
