import pygame as pg
from utility import import_folder, get_abs_path


class ParticleEffect(pg.sprite.Sprite):
    def __init__(self, pos, type):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.5
        if type == 'jump':
            self.frames = import_folder(get_abs_path('graph/character/particles/jump'))
        if type == 'land':
            self.frames = import_folder(get_abs_path('graph/character/particles/land'))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def animation(self):
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]
            self.frame_index += self.animation_speed

    def update(self, x_shift):
        self.animation()
        self.rect.x += x_shift
