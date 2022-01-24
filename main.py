from menu import StartScreen
import sys
import pygame as pg
from settings import *
from level import Level


pg.init()
screen = pg.display.set_mode((screen_width, screen_height))
clock = pg.time.Clock()
FPS = 60
level = Level(level_map, screen)
running = True
start_ = StartScreen()
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            pg.quit()
            sys.exit()
    screen.fill((100, 220, 120))
    pg.display.set_caption('Adventure of John')
    level.run()
    pg.display.update()
    clock.tick(FPS)