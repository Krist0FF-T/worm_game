import pygame as pg
import random

# if not pg.font.get_init():
#     pg.font.init()

# fonts = {}

# def get_font(size: int, fname: str):

#     if not fname in fonts:
#         fonts[fname] = {}

#     if not size in fonts[fname]:
#         fonts[fname][size] = pg.font.Font(fname, size)

#     return fonts[fname][size]

def random_list(length, a, b):
    return [random.randint(a,b) for i in range(length)]

def draw_text(surf: pg.Surface, text: str, font: pg.font.Font, color, pos, centered: bool):
    text_surf = font.render(text, 1, color)
    text_surf_size = text_surf.get_size()
    text_pos = [pos[i]-text_surf_size[i]//2 if centered else pos[i] for i in range(2)]
    text_rect = pg.Rect(*text_pos, *text_surf_size)

    surf.blit(text_surf, text_rect)

    return text_rect

def draw_outlined_circle(surf: pg.Surface, color, outline_color, center, radius, outline_width):
    pg.draw.circle(surf, outline_color, center, radius+outline_width)
    pg.draw.circle(surf, color, center, radius)

# faster than x**2
square = lambda x: x*x

get_length = lambda v: sum([square(v[i]) for i in range(len(v))])**0.5

get_dist = lambda p1, p2: get_length([p1[i]-p2[i] for i in range(len(p1))])

list_el_sub = lambda l1, l2: [l1[i]-l2[i] for i in range(min(len(l1), len(l2)))]

list_el_add = lambda *lists: [sum([c_l[i] for c_l in lists]) for i in range(min([len(l) for l in lists]))]

list_el_scale = lambda l, m: [i*m for i in l]
