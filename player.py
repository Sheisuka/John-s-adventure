import time
import pygame as pg
from utility import import_folder, get_abs_path


class Player(pg.sprite.Sprite):
    def __init__(self, pos, game, create_jump_particles):
        super().__init__()
        self.game = game
        self.delay = time.time()
        # Анимации
        self.import_run_particles()
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.particle_frame_index = 0
        self.particle_animation_speed = 0.2
        self.display_surf = self.game.screen
        self.create_jump_particles = create_jump_particles
        self.once_played_animation = ['attack', 'attack2', 'attack3', 'get_damage']

        # Статы
        self.get_damage_period = 2
        self.last_damage_time = 0
        self.max_hp = 100
        self.max_damage = 50
        self.hp = 70
        self.damage = 20

        # Хп и демедж бары
        self.bar_length = 300
        self.hp_ratio = self.max_hp / self.bar_length
        self.damage_ratio = self.max_damage / self.bar_length
        self.hp_bar_speed = 5
        self.target_health = 50

        # Движение
        self.direction = pg.math.Vector2(0, 0)
        self.speed = 26
        self.gravity = 0.8
        self.jump_speed = -17

        # Состояние
        self.state = 'idle'
        self.looking_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False
        self.not_hittable = False
        self.attack = False
        self.attack2 = False
        self.attack3 = False

    def death(self):
        self.direction.x = 0
        self.state = 'death'
        death = self.animations[self.state]
        self.frame_index += 0.05
        if self.frame_index >= len(death):
            pass
        else:
            image = death[int(self.frame_index)]
            if self.on_left:
                self.image = image
            else:
                self.image = pg.transform.flip(image, True, False)
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def health_bar(self):
        pg.draw.rect(self.display_surf, (255, 0, 0), (10, 10, int(self.hp / self.hp_ratio), 25))
        pg.draw.rect(self.display_surf, (255, 255, 255), (10, 10, self.bar_length, 25), 4)

    def damage_bar(self):
        pg.draw.rect(self.display_surf, (222, 119, 10), (10, 40, int(self.damage / self.damage_ratio), 25))
        pg.draw.rect(self.display_surf, (255, 255, 255), (10, 40, self.bar_length, 25), 4)

    def import_assets(self):
        self.animations = {'idle': [],
                           'run': [],
                           'jump': [],
                           'fall': [],
                           'attack': [],
                           'get_damage': [],
                           'death': [],
                           'attack2': [],
                           'attack3': []}
        character_path = 'graph/character/'
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(get_abs_path(full_path))

    def import_run_particles(self):
        self.run_particles = import_folder(get_abs_path('graph/character/particles/run'))

    def run_particle_animation(self):
        if self.state == 'run' and self.on_ground:
            self.particle_frame_index += self.particle_animation_speed
            if self.particle_frame_index >= len(self.run_particles):
                self.particle_frame_index = 0

            dust_particle = self.run_particles[int(self.particle_frame_index)]

            if self.looking_right:
                pos = self.rect.bottomleft - pg.math.Vector2(6, 10)
                self.display_surf.blit(dust_particle, pos)
            else:
                pos = self.rect.bottomright - pg.math.Vector2(6, 10)
                flipped_dust_particle = pg.transform.flip(dust_particle, True, False)
                self.display_surf.blit(flipped_dust_particle, pos)

    def animate(self):
        animation = self.animations[self.state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
            if self.state in self.once_played_animation:
                self.change_state()
                animation = self.animations[self.state]
        image = animation[int(self.frame_index)]
        if self.looking_right:
            self.image = image
        else:
            self.image = pg.transform.flip(image, True, False)

        if self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif self.on_ground and self.on_left:
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif self.on_ground:
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        elif self.on_ceiling and self.on_right:
            self.rect = self.image.get_rect(topright=self.rect.topright)
        elif self.on_ceiling and self.on_left:
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
        elif self.on_ceiling:
            self.rect = self.image.get_rect(midtop=self.rect.midtop)

    def change_state(self):
        self.animation_speed = 0.2
        self.state = 'gonnabechanged'
        self.get_cur_state()

    def get_damage(self, damage, cur_time):
        if (cur_time - self.last_damage_time > self.get_damage_period) \
                and self.state != 'death':
            self.hp -= damage
            if self.hp < 0:
                self.hp = 0
            if self.hp == 0:
                self.animation_speed = 0.08
                self.death()
            else:
                self.state = 'get_damage'
                self.last_damage_time = cur_time

    def get_input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            self.game.paused = True
        elif keys[pg.K_RIGHT]:
            self.direction.x = 1
            self.looking_right = True
        elif keys[pg.K_LEFT]:
            self.direction.x = -1
            self.looking_right = False
        elif keys[pg.K_q]:
            self.attack_check('onehand')
        elif keys[pg.K_w]:
            self.attack_check('twohand')
        elif keys[pg.K_e]:
            self.attack_check('spear')
        else:
            self.direction.x = 0
        if keys[pg.K_SPACE]:
            if self.on_ground:
                self.jump()
                self.create_jump_particles(self.rect.midbottom)

    def update(self):
        self.health_bar()
        self.damage_bar()
        if self.state == 'death' and self.game.pause_menu.wanna_see:
            self.death()
            keys = pg.key.get_pressed()
            if keys[pg.K_ESCAPE]:
                self.game.paused = True
        elif self.state == 'death':
            self.death()
            self.game.paused = True
            self.game.pause_menu.run('You died')
        else:
            self.get_input()
            self.get_cur_state()
            self.animate()
            self.run_particle_animation()

    def jump(self):
        self.direction.y = self.jump_speed

    def attack_check(self, type='onehand'):
        self.animation_speed = 0.12
        if type == 'twohand':
            self.attack = True
            self.state = 'attack'
        elif type == 'spear':
            self.attack2 = True
            self.state = 'attack2'
        else:
            self.attack3 = True
            self.state = 'attack3'
        self.delay = time.time()

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y
        if self.rect.y > 3000:
            self.death()

    def get_cur_state(self):
        if self.direction.y < 0:
            self.state = 'jump'
        elif self.direction.y > 1:
            self.state = 'fall'
        else:
            if self.state in self.once_played_animation:
                pass
            elif self.direction.x == 0:
                self.state = 'idle'
            elif self.direction.x != 0:
                self.state = 'run'
