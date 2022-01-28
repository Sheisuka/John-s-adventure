import time
from random import randint, choice
import pygame as pg
from utility import import_folder, get_abs_path


class Upgrade(pg.sprite.Sprite):
    def __init__(self, player, pos, results):
        super().__init__()
        self.player = player.sprite
        self.results = results
        if randint(0, 100) > 80:
            self.type = 'mayo'
        else:
            self.type = 'heart'
        self.def_size = 24
        self.levitate_range = 4
        self.full_path = self.levitate_range * 2
        self.up = False
        self.down = True

        if self.type == 'mayo':
            self.healed_hp = 100
            self.damage_up = 20
        else:
            self.healed_hp = 40
            self.damage_up = 0
        if self.type == 'heart':
            self.size = (self.def_size * 1.5, self.def_size * 1.5)
        else:
            self.size = (self.def_size, self.def_size * 1.5)
        self.image = pg.transform.scale(pg.image.load(get_abs_path(f'graph/upgrades/{self.type}.png')).convert_alpha(),
                                        self.size)
        self.rect = self.image.get_rect(center=pos)

    def get_picked(self):
        self.player.hp += self.healed_hp
        if self.player.hp > self.player.max_hp:
            self.player.hp = self.player.max_hp
        self.player.damage += self.damage_up
        if self.player.damage > 50:
            self.player.damage = 50
        if self.type == 'mayo':
            self.results['mayo'] += 1

    def animate(self):
        if self.up:
            if self.levitate_range != self.full_path:
                self.levitate_range += 1
                self.rect.y += 1
            else:
                self.down, self.up = True, False
        elif self.down:
            if self.levitate_range != -self.full_path:
                self.levitate_range -= 1
                self.rect.y -= 1
            else:
                self.down, self.up = False, True

    def update(self, x_shift, screen):
        self.rect.x += x_shift
        self.animate()


class Enemy(pg.sprite.Sprite):
    def __init__(self, name, pos, drop_upg_group, results):
        super().__init__()
        self.drop_group = drop_upg_group
        self.results = results
        self.name = name
        self.import_assets()
        self.x_pos = pos[0]
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(bottomleft=pos)
        if self.name == 'chest':
            self.go_range = 50
        else:
            self.go_range = 200
        self.full_path_len = self.go_range * 2
        self.get_damage_period = 1
        self.last_damage = 0
        self.unseen = True
        self.attack_range = range(self.x_pos - self.full_path_len // 2, self.x_pos + self.full_path_len // 2)

        # Движение
        self.direction = pg.math.Vector2(0, 0)
        self.speed = 3
        self.gravity = 0.8
        self.jump_speed = -16

        # Состояние
        self.state = 'idle'
        self.aim = 'none'
        self.on_ground = True
        self.on_left = True
        self.on_right = False
        self.not_hittable = False

        self.damage = 25
        self.hp = 60

    def import_assets(self):
        self.animations = {'idle': [],
                           'death': [],
                           'attack': []}
        character_path = f'graph/enemy/{self.name}/'
        for animation in self.animations.keys():
            full_path = get_abs_path(character_path + animation)
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        animation = self.animations[self.state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        image = animation[int(self.frame_index)]
        if self.on_left:
            self.image = image
        else:
            self.image = pg.transform.flip(image, True, False)
        if self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif self.on_ground and self.on_left:
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif self.on_ground:
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def die(self, player_obj):
        self.state = 'death'
        death = self.animations[self.state]
        self.frame_index += 0.08
        if self.frame_index >= len(death):
            if self.name == 'ketchup_slime':
                self.results['kills'] += 1
            self.kill()
            if randint(0, 100) > 65:
                upgrade = Upgrade(player_obj, (self.rect.x + 64, self.rect.y - 10), self.results)
                self.drop_group.add(upgrade)
        else:
            image = death[int(self.frame_index)]
            if self.on_left:
                self.image = image
            else:
                self.image = pg.transform.flip(image, True, False)
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def go_to_player(self, player_x, player_obj):
        if not player_obj.sprite.state == 'death':
            self.attack_player()
            if self.rect.x > player_x:
                self.on_left, self.on_right = True, False
                self.rect.x -= self.speed
            elif self.rect.x < player_x:
                self.rect.x += self.speed
                self.on_left, self.on_right = False, True

    def attack_player(self):
        self.state = 'attack'

    def inspection(self):
        if self.on_right:
            if self.go_range <= 0:
                self.on_right, self.on_left = False, True
                self.go_range = self.full_path_len
            else:
                self.rect.x += self.speed
                self.go_range -= self.speed
        else:
            if self.go_range <= 0:
                self.on_left, self.on_right = False, True
                self.go_range = self.full_path_len
            else:
                self.rect.x -= self.speed
                self.go_range -= self.speed

    def change_aim(self, player_x, player_y, total_world_shift, player_obj):
        if self.rect.midbottom[1] == player_y and player_x - total_world_shift in \
                self.attack_range:
            self.aim = 'kill_player'
            self.unseen = False
            self.full_path_len = 400
        elif player_obj.sprite.state == 'death':
            self.aim = 'none'
            self.inspection()
        elif not player_x - total_world_shift in \
                 self.attack_range:
            self.aim = 'none'
        else:
            self.state = 'idle'

    def update(self, shift_x, player_rect, total_world_shift, player_obj):
        player_x, player_y = player_rect[0], player_rect[1]
        if player_x not in self.attack_range:
            self.aim = 'none'
        self.rect.x += shift_x
        if not self.state == 'death':
            self.change_aim(player_x, player_y, total_world_shift, player_obj)
            if self.aim == 'none':
                if self.name == 'chest' and not self.unseen or self.name != 'chest':
                    self.inspection()
            else:
                self.go_to_player(player_x, player_obj)
            self.animate()
        else:
            self.die(player_obj)

    def take_damage(self, player_obj):
        if self.unseen:
            self.unseen = False
            self.state = 'attack'
        current_time = time.time()
        if current_time - self.last_damage > self.get_damage_period:
            if player_obj.sprite.looking_right:
                p_direction_x_vector = 1
            else:
                p_direction_x_vector = -1
            if (p_direction_x_vector * (player_obj.sprite.rect.centerx - self.rect.centerx)) < 0:
                if 'attack' in player_obj.sprite.state:
                    self.hp -= player_obj.sprite.damage
                    self.unseen = False
                if self.hp <= 0:
                    self.frame_index = 0
                    self.die(player_obj)
                self.last_damage = current_time


class Spike(pg.sprite.Sprite):
    def __init__(self, pos, player, on_ceil=False):
        super().__init__()
        self.player = player.sprite
        self.last_hit_time = time.time()
        self.damage = 30
        self.image = pg.transform.scale(pg.image.load(get_abs_path('graph/traps/spikes.png')), (64, 40))
        self.rect = self.image.get_rect(bottomleft=pos)
        if on_ceil:
            self.image = pg.transform.flip(self.image, False, True)

    def update(self, x_shift):
        self.rect.x += x_shift


class Box(pg.sprite.Sprite):
    def __init__(self, pos, player_obj, upgrades_group, results):
        super().__init__()
        self.import_animations()
        self.results = results
        self.player = player_obj
        self.upgrades = upgrades_group
        self.image = pg.transform.scale(pg.image.load(get_abs_path(f'graph/terrain/box/idle/{choice(["1.png", "2.png"])}')), (48, 48))
        self.rect = self.image.get_rect(bottomright=pos)
        self.frame_index = 0
        self.animation_speed = 0.3
        self.now_crushing = False

    def import_animations(self):
        self.animations = {'idle': [],
                           'crushing': []}
        for animation in self.animations.keys():
            full_path = get_abs_path('graph/terrain/box/' + animation)
            self.animations[animation] = import_folder(full_path)

    def crush(self):
        crush_anim = self.animations['crushing']
        self.frame_index += self.animation_speed
        if self.frame_index >= len(crush_anim):
            self.kill()
            if randint(0, 1) > 0.8:
                upgrade = Upgrade(self.player, (self.rect.x + 64, self.rect.y), self.results)
                self.upgrades.add(upgrade)
        else:
            self.image = pg.transform.scale(crush_anim[int(self.frame_index)], (48, 48))

    def update(self, x_shift):
        self.rect.x += x_shift
        if self.now_crushing:
            self.crush()


class Exit(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.transform.scale(pg.image.load(get_abs_path('graph/terrain/ladder/1.png')), (64, 192))
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift
