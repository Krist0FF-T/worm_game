
import json, sys, os, math, random
import pygame as pg
from datetime import datetime, timedelta

import utils, worm

class Game:
    def __init__(self):
        with open("config.json", 'r', encoding="utf-8") as f:
            self.config = json.load(f)

        self.config["worms"] = []

        for i, name in enumerate(self.config["players"]):
            for worm_config in self.config["worm configs"]:
                if worm_config["name"] == name:
                    self.config["worms"].append(worm_config)
                    self.config["worms"][i]["controls"] = self.config["worm controls"][i%len(self.config["worm controls"])]


        self.def_win_size = [1280, 720]
        self.def_win_center = [i//2 for i in self.def_win_size]

        self.win_size = self.config["win size"]
        self.win_center = [self.win_size[i]//2 for i in range(2)]
        self.scale = self.win_size[1]/self.def_win_size[1]
        
        self.screenshot_key = eval("pg.K_"+self.config["screenshot key"])

        pg.font.init()
        self.fonts = {}

        self.clock = pg.time.Clock()

        self.foods = []
        self.worms = []
        self.worm_props = self.config["worms"]
        self.gen_worm_props = self.config["gen worm props"]
        self.player_count = len(self.worm_props)

        self.map_rad = self.config["map radius"]

        self.worm_display_size = [self.win_size[0]//self.player_count, self.win_size[1]]

        # init worms
        for i in range(self.player_count):
            c_worm = worm.Worm(self.worm_props[i], self.gen_worm_props, self.worm_display_size, self.map_rad)

            self.worms.append(c_worm)

        self.reset_worms()

    def restart_game(self):
        self.reset_worms()
        self.foods.clear()

        for i in range(self.config["foods"]):
            self.add_food()

    def reset_worm(self, i):
        c_worm = self.worms[i]

        radians = i/self.player_count*2*math.pi
        radius = self.map_rad*0.7

        pos = [
            [math.cos, math.sin][j](radians)*radius
            for j in range(2)
        ]

        c_worm.reset(pos)

        c_worm.rot = radians-math.pi

    def reset_worms(self):
        for i in range(self.player_count):
            self.reset_worm(i)

    def add_food(self):
        radian = random.random()*math.pi*2
        radius = random.random()*self.map_rad

        c_food = [
            [math.cos, math.sin][i](radian)*radius
            for i in range(2)
        ]

        self.foods.append(c_food)

    def close(self):
        pg.quit()
        sys.exit()

    def run(self):

        self.screen = pg.display.set_mode(
            self.win_size,
            pg.FULLSCREEN if self.config["fullscreen"] else 0
        )

        self.main_menu()

        self.restart_game()

        food_spawn_timer = 0

        run = True
        while run:
            dt = self.clock.tick(self.config["fps"])*0.001
            if len(self.foods) < self.config["foods"]:
                food_spawn_timer += dt

            while food_spawn_timer > self.config["food spawn time"]:
                food_spawn_timer -= self.config["food spawn time"]
                self.add_food()

            # === U P D A T E ===

            # handle events
            events = pg.event.get()

            for ev in events:
                if ev.type == pg.QUIT:
                    self.close()
                
                if ev.type == pg.KEYDOWN:

                    if ev.key == self.screenshot_key:
                        self.screenshot()

                    elif ev.key == pg.K_r:
                        self.restart_game()
            
            keys = pg.key.get_pressed()

            # update worms
            for c_worm in self.worms:
                c_worm.update(dt, keys)

            # check for kills
            for i in range(self.player_count):
                a = self.worms[i]
                for j in range(self.player_count):
                    if i == j:
                        continue

                    b = self.worms[j]
                    if a.would_kill(b):
                        b.score += 1
                        self.reset_worms()
                        #a.alive = False

            # respawn dead players
            for i in range(self.player_count):
                if not self.worms[i].alive:
                    self.reset_worm(i)

            # eat
            for w in self.worms:
                for f in self.foods:

                    dist = utils.get_dist(w.parts[0], f)

                    if dist < w.gen_props["part rad"]-self.config["food rad"] and f in self.foods:
                        self.foods.remove(f)
                        w.add_part()
                    
                    elif dist < self.gen_worm_props["part rad"]*3:
                        diff_vec = utils.list_el_sub(w.parts[0], f)
                        
                        for i in range(2):
                            mult = 1/dist**2
                            f[i] += diff_vec[i]/dist * mult * dt * w.gen_props["part rad"] * (0b1 << 13)

            # ==== D R A W ===
            self.screen.fill((0,)*3)

            # update player screens
            for w_i, c_worm in enumerate(self.worms):
                # c_worm.draw(self.screen, self.scale, self.get_font())    

                cam = list(map(int, utils.list_el_sub(
                    c_worm.parts[0],
                    utils.list_el_scale(c_worm.display_center, 1/self.scale)
                )))

                screen_pos = lambda p: utils.list_el_scale(utils.list_el_sub(p, cam), self.scale)

                circ_on_screen = lambda pos, rad: (
                    pos[0] > -rad-1 and
                    pos[1] > -rad-1 and
                    pos[0] < self.worm_display_size[0]+rad and
                    pos[1] < self.worm_display_size[1]+rad
                )

                # clear display
                c_worm.display.fill((0,)*3)

                # draw grid
                for grid_i in range(self.worm_display_size[1]//self.config["tile size"]):
                    for grid_j in range(self.worm_display_size[0]//self.config["tile size"]):
                        p = [[grid_j,grid_i][i]*self.config["tile size"]-cam[i]%self.config["tile size"] for i in range(2)]
                        p = utils.list_el_scale(p, self.scale)
                        rect = (*p, *((self.config["tile size"]-2)*self.scale,)*2)
                        #print(rect)
                        pg.draw.rect(c_worm.display, self.config["grid color"], rect, 1)

                # draw map border
                pg.draw.circle(
                    c_worm.display, self.config["border color"], screen_pos((0,0)),
                    self.map_rad*self.scale, int(3*self.scale)
                )

                # scaled radius
                radius = c_worm.gen_props["part rad"]*self.scale

                # draw foods
                food_rad = self.config["food rad"]*self.scale
                for c_food in self.foods:
                    sp = screen_pos(c_food)
                    if circ_on_screen(sp, food_rad):
                        pg.draw.circle(c_worm.display, self.config["food color"], sp, food_rad)

                # draw worms
                for o_w in self.worms:

                    # draw parts in reverse order
                    for i in range(len(o_w.parts)-1, -1, -1):
                        c_part = o_w.parts[i]
                        center = c_part

                        part_color = o_w.props["colors"][i%len(o_w.props["colors"])]
                        sp = screen_pos(center)
                        if not circ_on_screen(sp, radius):
                            continue

                        pg.draw.circle(c_worm.display, part_color, sp, radius)
                        pg.draw.circle(c_worm.display, (0,)*3, sp, radius, int(1*self.scale))

                        # if it is the head
                        if i == 0:
                            # draw eye
                            eye_radius = c_worm.gen_props["part rad"]*0.3*self.scale
                            eye_centers = [
                                [
                                    center[i]+[math.cos, math.sin][i](o_w.rot+d*math.pi/2*0.6)*0.7*radius*0.5
                                    for i in range(2)
                                ]
                                for d in [1, -1]
                            ]

                            for eye_center in eye_centers:
                                sp = screen_pos(eye_center)
                                pg.draw.circle(c_worm.display, (255,)*3, sp, eye_radius)
                                pg.draw.circle(c_worm.display, (0,)*3, sp, eye_radius, int(1*self.scale))

                    # draw name
                    name_size = int(8*self.scale)
                    name_pos = [center[0],center[1]-self.gen_worm_props["part rad"]-name_size]
                    utils.draw_text(c_worm.display, o_w.props["name"], self.get_font(name_size), (255,)*3, screen_pos(name_pos), True)

                # -- draw worms

                # draw infos

                infos = {
                    "kills": c_worm.score,
                    "length": len(c_worm.parts)-1,
                    "clock": (math.atan2(c_worm.parts[0][1], c_worm.parts[0][0])/math.pi*6-9)%12,
                    "dfc": utils.get_length(c_worm.parts[0])/self.map_rad*100,
                    "foods": len(self.foods),
                    "fps": int(round(1/dt/5)*5),
                    #"e": int(round((self.map_rad/self.config["tile size"])**2 * math.pi))
                }

                for inf_i, inf_key in enumerate(infos):
                    inf_val = infos[inf_key]

                    if type(inf_val) == float:
                        inf_val = "{:.1f}".format(inf_val)

                    font_size = int(15*self.scale)
                    margin = int(10*self.scale)
                    pos = [
                        margin,
                        margin+font_size*inf_i*1.6
                    ]
                    utils.draw_text(c_worm.display, "{}: {}".format(inf_key, inf_val), self.get_font(font_size), (255,)*3, pos, False)

                # draw display to main screen
                self.screen.blit(c_worm.display, (w_i*self.worm_display_size[0], 0))

                # draw display separator line
                if w_i < self.player_count-1:
                    x = (w_i+1)*self.worm_display_size[0]-1
                    pg.draw.line(self.screen, (255,)*3, (x, 0), (x, self.win_size[1]), 2)

            # update screen
            pg.display.update()

    def get_font(self, size: int) -> pg.font.Font:
        
        if size not in self.fonts:
            self.fonts[size] = pg.font.Font(self.config["font file name"], size)
        
        return self.fonts[size]

    def draw_button(self, size, pos, centered: bool, text: str, events) -> bool:

        tsize = utils.list_el_scale(size, self.scale)
        tpos  = utils.list_el_scale(pos,  self.scale)

        if centered:
            tpos[0] -= tsize[0]/2
            tpos[1] -= tsize[1]/2

        rect = pg.Rect(tpos, tsize)
        hover = rect.collidepoint(pg.mouse.get_pos())

        color = self.config["gui colors"]["button"][hover]

        bord_rad = int(30*self.scale)

        pg.draw.rect(self.screen, color, rect, border_radius=bord_rad)

        font_size = int(tsize[1]/4*(1+int(hover)*0.1))
        text_outline = int((hover*3+1)*self.scale)

        txt_color = self.config["gui colors"]["text"]

        font = self.get_font(font_size)
        txt_surf = font.render(text, 1, txt_color)

        self.screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))

        click = False
        for ev in events:
            if ev.type == pg.MOUSEBUTTONDOWN:
                if ev.button == pg.BUTTON_LEFT:
                    click = True
                    break

        return (click and hover)
    
    def screenshot(self):
        img = self.screen.copy()

        infos = {
            "date": "{}-{}-{} {}:{}:{}".format(*[str(int(i)) for i in datetime.now().timetuple()[:6]])
        }

        font_size = int(10*self.scale)
        font = self.get_font(font_size)
        margin = 10

        for i, key in enumerate(infos):
            val = infos[key]

            pos = [
                margin,
                margin + i*font_size*2
            ]

            text = "{}: {}".format(key, val)

            utils.draw_text(img, text, font, (255,)*3, pos, False)
        
        fname = ""
        f_ind = 0

        while not f_ind or os.path.exists(fname):
            f_ind += 1
            fname = self.config["screenshot file name"].format(datetime.now().date(), f_ind)

        pg.image.save(img, fname)

    def main_menu(self):
        title = "PGWG"

        gui_colors = self.config["gui colors"]
        bg_color = gui_colors["background"]
        text_color = gui_colors["text"]

        button_size = [320, 150]
        button_sep = 20
        buttons_texts = ["Play", "Exit"]
        button_count = len(buttons_texts)

        mm = True
        while mm:
            events = pg.event.get()
            self.clock.tick(self.config["fps"])

            self.screen.fill(bg_color)

            for i in range(button_count):

                pos = [
                    self.def_win_center[0],
                    self.def_win_center[1] - (button_count-1) * (button_size[1]+button_sep) / 2 +
                    i*(button_size[1]+button_sep)
                ]

                if self.draw_button(button_size, pos, True, buttons_texts[i], events):
                    if i == 0:
                        mm = False
                    
                    elif i == 1:
                        self.close()

            title_rect = utils.draw_text(self.screen, title, self.get_font(int(40*self.scale)), text_color, [self.win_center[0], self.win_size[1]//8], True)

            # pg.draw.circle(self.screen, (255,0,0), self.win_center, 10)

            pg.display.update()

            for ev in events:
                
                if ev.type == pg.QUIT:
                    self.close()
                
                elif ev.type == pg.KEYDOWN:
                    if ev.key == pg.K_RETURN:
                        mm = False
                    
                    elif ev.key == self.screenshot_key:
                        self.screenshot()

        
