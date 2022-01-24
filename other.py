import pygame as pg
from random import choice
from utility import import_folder


class Upgrade(pg.sprite.Sprite):
    def __init__(self, player, pos):
        super().__init__()
        self.player = player.sprite
        self.type = choice(['mayo', 'heart'])
        if self.type == 'mayo':
            self.healed_hp = 100
            self.damage_up = 20
        else:
            self.healed_hp = 40
            self.damage_up = 0
        self.image = pg.transform.scale(pg.image.load('graph/upgrades/mayoMenu.png').convert_alpha(), (64, 64))
        self.rect = self.image.get_rect(center = pos)

    def get_picked(self):
        self.player.hp += self.healed_hp
        self.player.hp = 100
        self.player.damage += self.damage_up

    def check_collision(self):
        pass

    def update(self, x_shift):
        self.rect.x += x_shift


class Enemy(pg.sprite.Sprite):
    def __init__(self, player, pos):
        super().__init__()
        self.import_assets()
        self.player = player.sprite
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.particle_frame_index = 0
        self.particle_animation_speed = 0.2

        #Движение
        self.direction = pg.math.Vector2(0, 0)
        self.speed = 5
        self.gravity = 0.8
        self.jump_speed = -16

        #Состояние
        self.state = 'idle'
        self.looking_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False

        self.damage = 25

    def import_assets(self):
        self.animations = {'idle': [],
                           'death': [],
                           'attack': []}
        character_path = 'graph/enemy/ketchup_slime/'
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        animation = self.animations[self.state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        image = animation[int(self.frame_index)]
        if self.looking_right:
            self.image = image
        else:
            self.image = pg.transform.flip(image, True, False)
        if self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
        elif self.on_ground and self.on_left:
            self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
        elif self.on_ground:
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
        elif self.on_ceiling and self.on_right:
            self.rect = self.image.get_rect(topright = self.rect.topright)
        elif self.on_ceiling and self.on_left:
            self.rect = self.image.get_rect(topleft = self.rect.topleft)
        elif self.on_ceiling:
            self.rect = self.image.get_rect(midtop = self.rect.midtop)

    def give_damage(self):
        if not self.not_hittable:
            self.player.hp -= self.damamge
            if self.player.hp <= 0:
                self.player.death()
            else:
                self.player.not_hittable = True
                self.player.state = 'get_damage'

    def attack_player(self):
        pass

    def update(self, shift_x):
        self.rect.x += shift_x

