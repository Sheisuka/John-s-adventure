from os import walk, path
import pygame as pg
from PIL import Image
import sys


def import_folder(path):
    surface_list = []
    for _, __, img_names in walk(path):
        for img in img_names:
            full_path = path + '/' + img
            width, height = (Image.open(full_path)).size
            if 'slime' in full_path:
                width, height = int(width * 1.5), int(height * 1.5)
            elif 'chest' in full_path:
                width, height = int(width * 1.8), int(height * 1.8)
            elif 'particle' in full_path:
                width, height = int(width * 0.8), int(height * 0.8)
            image_surface = pg.transform.scale((pg.image.load(full_path).convert_alpha()),
                                               (int(width * 1.5), int(height * 1.5)))

            surface_list.append(image_surface)

    return surface_list

def get_abs_path(rel_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")
    return path.join(base_path, rel_path)
