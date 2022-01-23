from tiles import Tile
import pygame as pg
from player import Player
from settings import *
from particles import *


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.setup_level(level_data)
        self.world_shift = 0
        self.cur_playerx = None
        self.player_on_ground = False

        self.particle_sprites = pg.sprite.Group()

    def run(self):
        self.particle_sprites.update(self.world_shift)
        self.particle_sprites.draw(self.display_surface)
        # draw tiles
        self.tiles.update(self.world_shift)
        self.tiles.draw(self.display_surface)
        self.scroll_x()

        # draw player
        self.player.update()
        self.horiz_movement_collision()
        self.get_player_on_ground()
        self.vert_movement_collision()
        self.create_landing_particles()
        self.player.draw(self.display_surface)

    def create_landing_particles(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.particle_sprites:
            offset = pg.math.Vector2(10, 15)
            if not self.player.sprite.looking_right:
                offset = pg.math.Vector2(-10, 15)
            land_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.particle_sprites.add(land_particle)

    def setup_level(self, layout):
        self.tiles = pg.sprite.Group()
        self.player = pg.sprite.GroupSingle()
        for row_i, row in enumerate(layout):
            for col_i, cell in enumerate(row):
                x = col_i * tile_size
                y = row_i * tile_size
                if cell == 'X':
                    tile = Tile((x, y), tile_size)
                    self.tiles.add(tile)
                if cell == 'P':
                    player_sprite = Player((x, y), self.display_surface, self.jump_particles)
                    self.player.add(player_sprite)

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def jump_particles(self, pos):
        if self.player.sprite.looking_right:
            pos -= pg.math.Vector2(10, 5)
        else:
            pos += pg.math.Vector2(10, -5)
        jump_particle = ParticleEffect(pos, 'jump')
        self.particle_sprites.add(jump_particle)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width // 4 and direction_x < 0:
            self.world_shift = 5
            player.speed = 0
        elif player_x > screen_width - screen_width // 4 and direction_x > 0:
            self.world_shift = -5
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 5

    def horiz_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.cur_playerx = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.cur_playerx = player.rect.right

        if player.on_left and (player.rect.left < self.cur_playerx or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.cur_playerx or player.direction.x <= 0):
            player.on_right = False

    def vert_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False
