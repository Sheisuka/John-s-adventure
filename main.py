import sys
import pygame as pg
from settings import *
from level import Level


pg.init()
screen = pg.display.set_mode((screen_width, screen_height))
clock = pg.time.Clock()
FPS = 60
level = Level(level_map, screen)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    screen.fill('black')
    pg.display.set_caption('Adventure of John')
    level.run()
    pg.display.update()
    clock.tick(FPS)