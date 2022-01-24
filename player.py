import pygame as pg
from utility import import_folder


class Player(pg.sprite.Sprite):
    def __init__(self, pos, surf, create_jump_particles):
        super().__init__()
        #Аниме
        self.import_run_particles()
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.particle_frame_index = 0
        self.particle_animation_speed = 0.2
        self.display_surf = surf
        self.create_jump_particles = create_jump_particles

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
        self.not_hittable = False

        #Характеристики
        self.hp = 70
        self.damage = 20

    def death(self):
        self.state = 'death'

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
            self.animations[animation] = import_folder(full_path)

    def import_run_particles(self):
        self.run_particles = import_folder('graph/character/particles/run')

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

    def get_input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_RIGHT]:
            self.direction.x = 1
            self.looking_right = True
        elif keys[pg.K_LEFT]:
            self.direction.x = -1
            self.looking_right = False
        else:
            self.direction.x = 0
        if keys[pg.K_SPACE]:
            if self.on_ground:
                self.jump()
                self.create_jump_particles(self.rect.midbottom)

    def update(self):
        self.get_input()
        self.get_cur_state()
        self.animate()
        self.run_particle_animation()

    def jump(self):
        self.direction.y = self.jump_speed

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def get_cur_state(self):
        if self.direction.y < 0:
            self.state = 'jump'
        elif self.direction.y > 1:
            self.state = 'fall'
        else:
            if self.direction.x == 0:
                self.state = 'idle'
            elif self.direction.x != 0:
                self.state = 'run'
