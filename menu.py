import pygame as pg
from math import ceil
import main
import settings

screen = main.screen

class Menu:
    def __init__(self):
        self.display = pg.Surface((settings.screen_width, settings.screen_height))
        self.state = 'start'
        pg.mouse.set_visible(False)
        self.mid_w, self.mid_h = settings.screen_width // 2, settings.screen_height // 2
        self.run_display = True
        self.cursor_rect = pg.Rect(0, 0, 20, 20)
        self.offset = -185
        self.cursor_size = 18
        self.speed = 1
        self.clock = pg.time.Clock()
        self.UP_KEY, self.DOWN_KEY, self.BACK_KEY, self.START_KEY = False, False, False, False

    def process_events(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_RETURN]:
            self.START_KEY = True
        elif keys[pg.K_UP]:
            self.UP_KEY = True
        elif keys[pg.K_DOWN]:
            self.DOWN_KEY
        elif keys[pg.K_BACKSPACE]:
            self.BACK_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.BACK_KEY, self.START_KEY = False, False, False, False

    def draw_cursor(self):
        self.draw_text('*', self.cursor_size, self.cursor_rect.x, self.cursor_rect.y)
        if self.cursor_size <= 30:
            self.cursor_size += ceil(self.speed * self.clock.tick() / 10000)
        else:
            self.cursor_size = 18

    def draw_text(self, text, size, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)

    def blit_screen(self):
        screen.blit(self.display, (0, 0))
        pg.display.update()


class MainMenu(Menu):
    def __init__(self):
        super().__init__()
        self.startx, self.starty = self.mid_w, self.mid_h + 20
        self.optionx, self.optiony = self.mid_w, self.mid_h + 65
        self.exitx, self.exity = self.mid_w, self.mid_h + 105
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.process_events()
            self.check_input()
            self.display.fill(self.game.BLACK)
            self.draw_text('Main Menu', 45, self.mid_w, 200)
            self.draw_text('Start Game', 35, self.startx, self.starty)
            self.draw_text('Options', 35, self.optionx, self.optiony)
            self.draw_text('Exit', 35, self.exitx, self.exity)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.DOWN_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.optionx + self.offset + 55, self.optiony)
                self.state = 'Options'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.exitx + self.offset + 110, self.exity)
                self.state = 'Exit'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
        elif self.UP_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.exitx + self.offset + 110, self.exity)
                self.state = 'Exit'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.optionx + self.offset + 55, self.optiony)
                self.state = 'Options'

    def check_input(self):
        self.move_cursor()
        if self.START_KEY:
            if self.state == 'Start':
                self.game.playing = True
            elif self.state == 'Options':
                self.game.curr_menu = self.game.options
            elif self.state == 'Exit':
                self.terminate()
            self.run_display = False

class OptionsMenu(Menu):
    def __init__(self):
        super().__init__()
        self.state = 'Volume'
        self.volx, self.voly = self.mid_w, self.mid_h
        self.controlsx, self.contronlsy = self.mid_w, self.mid_h + 40
        self.cursor_rect.midtop = (self.volx + self.offset + 50, self.voly)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.process_events()
            self.check_input()
            self.display.fill((0, 0, 0))
            self.draw_text('Volume', 30, self.volx, self.voly)
            self.draw_text('Controls', 30, self.controlsx, self.contronlsy)
            self.draw_text('Press Backspace', 15, 800, 600)
            self.draw_text('to go back', 15, 800, 620)
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.BACK_KEY:
            self.game.curr_menu = self.game.main_menu
            self.run_display = False
        elif self.UP_KEY or self.DOWN_KEY:
            if self.state == 'Volume':
                self.state = 'Controls'
                self.cursor_rect.midtop = (self.controlsx + self.offset + 50, self.contronlsy)
            elif self.state == 'Controls':
                self.state = 'Volume'
                self.cursor_rect.midtop = (self.volx + self.offset + 50, self.voly)
        elif self.START_KEY:
            pass


class StartScreen(Menu):
    def __init__(self):
        super().__init__()
        self.start_ticks = pg.time.get_ticks()
        self.duration = 2
        pg.mouse.set_visible(False)
        self.intro_text = ['sheisuka',
                           'presents',
                           'adventure of john']
        self.background = pg.transform.scale(pg.image.load('graph/pics/start_background.png'), (settings.screen_width, settings.screen_height))
        screen.blit(self.background, (0, 0))
        font = pg.font.Font(None, 30)
        text_coord = 100
        for line in self.intro_text:
            string_rendered = font.render(line, 40, self.game.WHITE)
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

    def show_start(self):
        self.start_run = True
        while self.start_run:
            self.process_events()
            if self.START_KEY:
                    self.start_run = False
                    self.game.display.fill((0, 0, 0))
            self.reset_keys()
            pg.display.flip()

