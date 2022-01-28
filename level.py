import time

from other import Upgrade, Enemy, Spike, Box, Exit
from particles import *
from player import Player
from settings import *
from tiles import Tile


class Level():
    def __init__(self, level_data, game):
        self.game = game
        self.display_surface = self.game.screen
        self.setup_level(level_data)
        self.world_shift = 0
        self.total_world_shift = 0
        self.cur_playerx = None
        self.player_on_ground = False
        self.border_range = tile_size * 3.2

        self.particle_sprites = pg.sprite.Group()

    def run(self):
        if self.game.paused:
            self.game.pause_menu.run()
        else:
            self.tile_background.draw(self.display_surface)
            self.tile_background.update(self.world_shift)
            self.tiles.update(self.world_shift)
            self.tiles.draw(self.display_surface)
            self.particle_sprites.update(self.world_shift)
            self.particle_sprites.draw(self.display_surface)
            # draw tiles
            self.upgrade_sprites.update(self.world_shift, self.display_surface)
            self.upgrade_sprites.draw(self.display_surface)

            self.enemy_sprites.update(self.world_shift, self.player.sprite.rect.midbottom, self.total_world_shift,
                                      self.player)
            self.enemy_sprites.draw(self.display_surface)

            self.trap_sprites.update(self.world_shift)
            self.trap_sprites.draw(self.display_surface)

            self.terrain_sprites.update(self.world_shift)
            self.terrain_sprites.draw(self.display_surface)

            self.exit_level.update(self.world_shift)
            self.exit_level.draw(self.display_surface)

            # draw player
            self.player.update()
            self.horiz_movement_collision()
            self.get_player_on_ground()
            self.vert_movement_collision()
            self.create_landing_particles()
            self.scroll_x()
            self.player.draw(self.display_surface)

    def create_landing_particles(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.particle_sprites:
            offset = pg.math.Vector2(10, 15)
            if not self.player.sprite.looking_right:
                offset = pg.math.Vector2(-10, 15)
            land_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.particle_sprites.add(land_particle)

    def setup_level(self, layout):
        self.layout = layout
        self.blocks_path = {1: {'B': [get_abs_path('graph/blocks/brick_solid.png'), 'solid'],
                                '-': [get_abs_path('graph/blocks/brick_back.png'), 'back']},
                            2: {'B': [get_abs_path('graph/blocks/dirt_block.png'), 'solid'],
                                'b': [get_abs_path('graph/blocks/under_grass_block.png'), 'solid']}}
        self.enemy_sprites = pg.sprite.Group()
        self.tiles = pg.sprite.Group()
        self.tile_background = pg.sprite.GroupSingle()
        if self.game.level_num == 1:
            self.tile_background.add(Tile(get_abs_path('graph/blocks/brick_background.png'), (-512, -192)))
        else:
            self.tile_background.add(Tile(get_abs_path('graph/blocks/forest_background.png'), (-512, -192)))
        self.player = pg.sprite.GroupSingle()
        self.upgrade_sprites = pg.sprite.Group()
        self.trap_sprites = pg.sprite.Group()
        self.terrain_sprites = pg.sprite.Group()
        self.exit_level = pg.sprite.GroupSingle()

        for row_i, row in enumerate(self.layout):
            for col_i, cell in enumerate(row):
                x = col_i * tile_size
                y = row_i * tile_size
                if cell in self.blocks_path[self.game.level_num]:
                    path = self.blocks_path[self.game.level_num][cell][0]
                    tile = Tile(path, (x, y))
                    if self.blocks_path[self.game.level_num][cell][1] == 'solid':
                        self.tiles.add(tile)
                if cell == 'P':
                    player_sprite = Player((x, y), self.game, self.jump_particles)
                    self.player.add(player_sprite)
                elif cell == 'U':
                    upgrade = Upgrade(self.player,
                                      (col_i * tile_size + tile_size // 2, row_i * tile_size + tile_size // 2),
                                      self.game.results)
                    self.upgrade_sprites.add(upgrade)
                elif cell == 'K':
                    enemy = Enemy('ketchup_slime', (x, y + tile_size), self.upgrade_sprites, self.game.results)
                    self.enemy_sprites.add(enemy)
                elif cell == 'C':
                    enemy = Enemy('chest', (x, y + tile_size), self.upgrade_sprites, self.game.results)
                    self.enemy_sprites.add(enemy)
                elif cell == 'T':
                    if layout[row_i + 1][col_i] == ' ':
                        trap = Spike((x, y + 39), self.player, True)
                    else:
                        trap = Spike((x, y + tile_size), self.player)
                    self.trap_sprites.add(trap)
                elif cell == 'L':
                    box = Box((x, y + tile_size), self.player, self.upgrade_sprites, self.game.results)
                    self.terrain_sprites.add(box)
                elif cell == '@':
                    ladder = Exit((x, y))
                    self.exit_level.add(ladder)
                elif cell == 'S':
                    enemy = Enemy('sprout', (x, y + tile_size), self.upgrade_sprites, self.game.results)
                    self.enemy_sprites.add(enemy)

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
        if player_x < screen_width // 3 and direction_x < 0:
            self.world_shift = 5
            player.speed = 0
        elif player_x > screen_width - screen_width // 3 and direction_x > 0:
            self.world_shift = -5
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 5
        self.total_world_shift += self.world_shift

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
        for sprite in self.enemy_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                cur_time = time.time()
                if not 'attack' in self.player.sprite.state and sprite.state != 'death':
                    self.player.sprite.get_damage(sprite.damage, cur_time)
                if sprite.state != 'death':
                    sprite.take_damage(self.player)
        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.rect) and 'attack' in self.player.sprite.state:
                sprite.now_crushing = True
        for sprite in self.trap_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                cur_time = time.time()
                self.player.sprite.get_damage(sprite.damage, cur_time)

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
        for upgrade in self.upgrade_sprites.sprites():
            if upgrade.rect.colliderect(player.rect) and 'attack' not in player.state:
                upgrade.get_picked()
                self.upgrade_sprites.remove(upgrade)
        if self.exit_level.sprite.rect.colliderect(player.rect):
            self.game.level_num += 1
            if self.game.curr_level == self.game.level_first:
                self.game.curr_level = self.game.level_second
            elif self.game.curr_level == self.game.level_second:
                self.game.curr_level = self.game.results_window
