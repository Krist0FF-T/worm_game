
import pygame as pg
import math

import utils

class Worm:
    def __init__(self, worm_props, gen_props, display_size, map_rad):
        self.parts = []
        self.props = worm_props
        self.gen_props = gen_props
        self.rot = 0

        self.controls = {}

        for key in worm_props["controls"]:
            self.controls[key] = eval("pg.K_"+worm_props["controls"][key])

        self.alive = False
        self.map_rad = map_rad
        self.score = 0

        self.display = pg.Surface(display_size)
        self.display_size = display_size
        self.display_center = utils.list_el_scale(self.display_size, 0.5)

    def reset(self, pos):
        self.parts.clear()
        self.parts.append(pos)
        self.add_n_parts(self.gen_props["def parts"])
        self.alive = True

    def circ_on_screen(self, pos, rad):
        return (
            pos[0] > -rad-1 and
            pos[1] > -rad-1 and
            pos[0] < self.display_size[0]+rad and
            pos[1] < self.display_size[1]+rad
        )

    def update(self, dt: float, keys):
        rot_dir = (keys[self.controls["right"]] - keys[self.controls["left"]])
        self.rot += self.gen_props["rot speed"]/360*math.pi*2 * rot_dir * dt

        for part_index, part in enumerate(self.parts):

            if part_index == 0:

                if utils.get_dist((0,)*2, part) > self.map_rad:
                    self.alive = False
                    return

                for i in range(2):
                    part[i] += [math.cos, math.sin][i](self.rot)*self.gen_props["move speed"]*dt

            else:
                prev_part = self.parts[part_index-1]
                dist = utils.get_dist(part, prev_part)

                if dist > 0:

                    pos_diff = utils.list_el_sub(prev_part, part)

                    mult = min(1, dist/self.gen_props["part rad"]/1.2)

                    for i in range(2):
                        part[i] += pos_diff[i]/dist*dt*self.gen_props["move speed"]*mult

    def add_part(self):
        if len(self.parts) < self.gen_props["max parts"]:
            self.parts.append(self.parts[-1][:])

    def add_n_parts(self, n: int):
        if len(self.parts) < self.gen_props["max parts"]:
            for i in range(n):
                self.add_part()

    def would_kill(self, other):
        head = self.parts[0]

        for i in range(1, len(other.parts)):
            part = other.parts[i]
            if utils.get_dist(head, part) < self.gen_props["part rad"]*2:
                return True
        
        return False