import pygame as pg
from utility import get_abs_path


class Tile(pg.sprite.Sprite):
    def __init__(self, path, pos):
        super().__init__()
        self.image = pg.image.load(get_abs_path(path)).convert_alpha()
        if 'dirt' in path:
            self.image = pg.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift
