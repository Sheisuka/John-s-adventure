import sys
import time
from math import ceil
import pygame as pg


class Menu():
    def __init__(self, game):
        self.game = game
        self.run_display = True

        # Menu specifications
        self.cursor_rect = pg.Rect(0, 0, 20, 20)
        self.mid_w, self.mid_h = self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2
        self.offset = -185
        self.speed = 1
        self.cursor_size = 18

    def draw_cursor(self):
        self.game.draw_text('*', self.cursor_size, self.cursor_rect.x, self.cursor_rect.y)
        if self.cursor_size <= 30:
            self.cursor_size += ceil(self.speed * self.game.clock.tick() / 10000)
        else:
            self.cursor_size = 18

    def blit_screen(self):
        self.game.screen.blit(self.game.display, (0, 0))
        pg.display.update()
        self.game.reset_keys()


class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        # Btn coordinates
        self.startx, self.starty = self.mid_w, self.mid_h + 20
        self.aboutsx, self.aboutsy = self.mid_w, self.mid_h + 65
        self.exitx, self.exity = self.mid_w, self.mid_h + 105
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
        # Selected button
        self.state = "Start"

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text('Main Menu', 45, self.mid_w, 200)
            self.game.draw_text('Start Game', 35, self.startx, self.starty)
            self.game.draw_text('About', 35, self.aboutsx, self.aboutsy)
            self.game.draw_text('Exit', 35, self.exitx, self.exity)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.aboutsx + self.offset, self.aboutsy)
                self.state = 'About'
            elif self.state == 'About':
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity)
                self.state = 'Exit'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
        elif self.game.UP_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity)
                self.state = 'Exit'
            elif self.state == 'About':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.aboutsx + self.offset, self.aboutsy)
                self.state = 'About'

    def check_input(self):
        self.move_cursor()
        if self.game.START_KEY:
            if self.state == 'Start':
                self.game.playing = True
                self.run_display = False
            if self.state == 'About':
                self.run_display = False
                self.game.curr_menu = self.game.about_game
            elif self.state == 'Exit':
                sys.exit()


class StartScreen(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.start_time = time.time()
        self.duration = 2
        pg.mouse.set_visible(False)

    def display_menu(self):
        while self.game.curr_menu == self.game.start_screen:
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text('ADVENTURE OF JOHN', 50, self.game.DISPLAY_W / 2, 240)
            self.game.draw_text('created by sheisuka', 15, self.game.DISPLAY_W / 2, 920)
            self.game.draw_text('2022', 15, self.game.DISPLAY_W / 2, 940)
            if time.time() - self.start_time > self.duration:
                self.game.draw_text('press any key to start', 30, self.game.DISPLAY_W / 2, 500)
            self.blit_screen()
            self.check_input()

    def check_input(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.terminate()
            elif event.type == pg.KEYDOWN:
                if time.time() - self.start_time > self.duration:
                    self.game.curr_menu = self.game.main_menu


class About(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.def_y = 400
        self.distance = 60
        self.text = ['Use arrows to walk ',
                     'space to jump and QWE to attack '
                     'with spear one handed and two handed sword ',
                     'Eat mayo to increase your damage and hp ']

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.check_input()
            self.game.display.fill((0, 0, 0))
            for line_i, line in enumerate(self.text):
                self.game.draw_text(line, 20, self.game.DISPLAY_W / 2, self.def_y + self.distance * line_i)
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.terminate()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    self.game.curr_menu = self.game.main_menu
                    self.run_display = False


class PauseMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.state = 'Continue'
        self.offset -= 25
        self.conx, self.cony = self.mid_w, self.mid_h + 20
        self.exitx, self.exity = self.mid_w, self.mid_h + 100
        self.restartx, self.restarty = self.mid_w, self.mid_h + 60
        self.cursor_rect.midtop = (self.conx + self.offset, self.cony)
        self.wanna_see = False

    def run(self, text='Game is paused'):
        while self.game.paused:
            self.text = text
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text(text, 45, self.mid_w, 200)
            if text == 'You died':
                self.game.draw_text('see dead Nikita', 35, self.conx, self.cony)
            else:
                self.game.draw_text('Continue', 35, self.conx, self.cony)
            self.game.draw_text('Restart', 35, self.restartx, self.restarty)
            self.game.draw_text('Exit game', 35, self.exitx, self.exity)
            self.draw_cursor()
            self.blit_screen()
            self.game.reset_keys()

    def check_input(self):
        if self.game.DOWN_KEY:
            if self.state == 'Continue':
                self.state = 'Restart'
                self.cursor_rect.midtop = (self.restartx + self.offset, self.restarty)
            elif self.state == 'Restart':
                self.state = 'Exit'
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity)
            elif self.state == 'Exit':
                self.state = 'Continue'
                self.cursor_rect.midtop = (self.conx + self.offset, self.cony)
        elif self.game.UP_KEY:
            if self.state == 'Continue':
                self.state = 'Exit'
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity)
            elif self.state == 'Exit':
                self.state = 'Restart'
                self.cursor_rect.midtop = (self.restartx + self.offset, self.restarty)
            elif self.state == 'Restart':
                self.state = 'Continue'
                self.cursor_rect.midtop = (self.conx + self.offset, self.cony)
        elif self.game.START_KEY:
            if self.state == 'Continue':
                self.game.paused = False
                if self.text == 'You died':
                    self.wanna_see = True
            elif self.state == 'Exit':
                self.game.terminate()
            elif self.state == 'Restart':
                self.game.reset()


class Results(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.time = time.time()

    def run(self):
        while self.game.playing:
            curr_time = time.time()
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text('You completed all levels', 45, self.mid_w, 200)
            self.game.draw_text('Results', 40, self.mid_w, 300)
            self.game.draw_text('Ketchup slimes were killed', 35, self.mid_w, 450)
            self.game.draw_text(f'{self.game.results["kills"]}', 35, self.mid_w, 500)
            self.game.draw_text('Jars of mayo were eaten', 35, self.mid_w, 600)
            self.game.draw_text(f'{self.game.results["mayo"]}', 35, self.mid_w, 650)
            if curr_time - self.time > 5:
                self.game.draw_text('Press enter to exit', 35, self.mid_w, 800)
            self.blit_screen()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game.terminate()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        self.game.terminate()
