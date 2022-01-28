from settings import *
from menu import *
from settings import *
from level import Level
from utility import get_abs_path


class Game():
    def __init__(self):
        pg.init()
        # Creating specification variables
        self.DISPLAY_W, self.DISPLAY_H = screen_width, screen_height
        self.display = pg.Surface((self.DISPLAY_W, self.DISPLAY_H + 192))
        self.screen = pg.display.set_mode((self.DISPLAY_W, self.DISPLAY_H), pg.FULLSCREEN)
        self.results = {'kills': 0,
                        'mayo': 0}
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.paused = False, False, False, False, False
        self.BLACK, self.WHITE = (0, 0, 0), (255, 255, 255)
        self.clock = pg.time.Clock()
        self.FPS = 60
        self.level_num = 1

        # Load needed  data
        self.music = pg.mixer.Sound(get_abs_path('graph/sound/main_theme.mp3'))
        self.font_name = get_abs_path('graph/fonts/8-BIT WONDER.TTF')

        # Managing objects block
        self.start_screen = StartScreen(self)
        self.main_menu = MainMenu(self)
        self.about_game = About(self)
        self.pause_menu = PauseMenu(self)
        self.results_window = Results(self)
        self.curr_menu = self.start_screen
        self.level_first = Level(level_map, self)
        self.level_num = 2
        self.level_second = Level(level_map2, self)
        self.curr_level = self.level_first

        # Window and music settings
        pg.mouse.set_visible(False)
        pg.display.set_caption('Adventure of John')
        self.music.set_volume(0.3)

    def terminate(self):
        pg.quit()
        sys.exit()

    def restart(self):
        self.results = {'kills': 0,
                        'mayo': 0}
        self.running, self.playing = True, True
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.paused = False, False, False, False, False
        self.level_num = 1
        self.curr_level = self.level_first

    def loop(self):
        while self.playing:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    pg.quit()
                    sys.exit()
            self.curr_level.run()
            pg.display.update()
            self.clock.tick(self.FPS)

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running, self.playing = False, False
                self.curr_menu.run_display = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.START_KEY = True
                if event.key == pg.K_BACKSPACE:
                    self.BACK_KEY = True
                if event.key == pg.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pg.K_UP:
                    self.UP_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    def draw_text(self, text, size, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)

    def reset(self):
        self.__init__()
        self.running = True
        self.playing = True


game = Game()
game.music.play(5)
while game.running:
    game.curr_menu.display_menu()
    game.loop()
