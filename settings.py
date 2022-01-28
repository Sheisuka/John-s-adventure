from utility import get_abs_path


with open(get_abs_path('graph/levels/level1.txt'), 'r') as level_file:
    level_map = level_file.read().split('\n')
with open(get_abs_path('graph/levels/level2.txt'), 'r') as level_file:
    level_map2 = level_file.read().split('\n')

tile_size = 64
screen_width = 1920
screen_height = len(level_map) * tile_size
