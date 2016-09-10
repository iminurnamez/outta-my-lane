from random import choice, randint, uniform, sample
from operator import attrgetter

import pygame as pg

from .. import tools, prepare
from ..components.angles import get_angle, project
from ..components.animation import Animation
from ..components.vehicles import Vehicle, px_to_miles, VEHICLE_IMAGES, VEHICLE_FREQUENCIES
from ..components.player import Player
from ..components.ui import Speedometer
from ..components.obstacles import Obstacle, OBSTACLE_NAMES
from ..components.achievements import Achievement, ACHIEVEMENTS

LANE_WIDTH = 48


VEHICLE_BAG = []
for v in VEHICLE_FREQUENCIES:
    for x in range(VEHICLE_FREQUENCIES[v]):
        VEHICLE_BAG.append(v)


class Lane(pg.sprite.Group):
    def __init__(self, num, rect):
        super(Lane, self).__init__()
        self.num = num
        self.rect = rect


class Gameplay(tools._State):
    def __init__(self):
        super(Gameplay, self).__init__()
        self.bg_color = pg.Color("gray5")
        self.chunk_length = 2500
        self.crash_sounds = [prepare.SFX["crash{}".format(x)] for x in range(1, 8)]

    def startup(self, persistent):
        self.persist = persistent
        self.user = self.persist["user"]
        sr = prepare.SCREEN_RECT
        self.all_cars = pg.sprite.Group()
        self.other_cars = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.lanes = {}
        self.lane_rects = []
        self.lanes_left = 160
        for i in range(6):
            rect = pg.Rect(self.lanes_left + (i * LANE_WIDTH), 0, LANE_WIDTH, 720)
            self.lanes[i] = Lane(i, rect)
        self.lanes_right = self.lanes[len(self.lanes) - 1].rect.right
        player_lane = 1
        road_bottom = 2000
        road_top = -2000
        self.player = Player((self.lanes_left + 32, road_bottom + 200),
                                    60, 60, player_lane, player_lane, self.persist["vehicle_image"],
                                    self.persist["style"], self.all_cars, self.lanes[player_lane])
        self.speedometer = Speedometer((0, 560))
        self.elapsed = 0

        self.map_surf = pg.Surface((72, 360))
        self.map_rect = self.map_surf.get_rect(topleft=(3, 100))
        self.animations = pg.sprite.Group()
        self.make_markings_image()
        self.markings_points = [
                ((self.lanes_left - 1, 0), (self.lanes_left - 1, sr.bottom)),
                ((self.lanes_right - 1, 0), (self.lanes_right - 1, sr.bottom))]
        self.make_road_edges()
        self.collisions_active = False
        self.player_crashed = False
        self.cover = None
        self.crashes = 0
        self.make_achievements()
        self.car_total = 80

    def make_markings_image(self):
        w, h = prepare.SCREEN_SIZE
        marking_length = 32
        space = marking_length * 3
        total = marking_length + space
        num, rem = divmod(h, total)
        if rem:
            num += 1
        num += 1
        surf = pg.Surface((2, num * total))
        surf.fill(self.bg_color)
        for y in range(num * total):
            pg.draw.rect(surf, pg.Color("antiquewhite"),
                              (0, y * total, 2, marking_length))
        self.markings_image = surf
        self.markings_y = -total
        self.markings_reset = self.markings_y

    def draw_lane_markings(self, surface):
        for p1, p2 in self.markings_points:
            pg.draw.line(surface, pg.Color("antiquewhite"), p1, p2, 2)
        for x in range(len(self.lanes) - 1):
            lane = self.lanes[x]
            left = lane.rect.right - 1
            surface.blit(self.markings_image, (left, self.markings_y))

    def make_road_edges(self):
        left_topleft = 0, 0
        left_surf = pg.Surface((160, 736))
        img = prepare.GFX["grass_tile"]
        for y in range(46):
            left_surf.blit(prepare.GFX["dirt_tile"], (16 * 7, y * 16))
            left_surf.blit(prepare.GFX["dirt_tile"], (16* 8, y * 16))

        for y in range(46):
            left_surf.blit(prepare.GFX["dirt_tile_right"], (16*9, y * 16))
        for x in range(8):
            if x == 7:
                img = prepare.GFX["grass_tile_right"]
            for y in range(46):
                left = left_topleft[0] + (16 * x)
                top = left_topleft[1] + (16 * y)
                left_surf.blit(img, (left, top))
        self.left_edge = (left_surf, [0, -16])
        l = self.lanes[len(self.lanes) - 1].rect.right
        r_surf = pg.transform.flip(left_surf, True, False)
        self.right_edge = (r_surf, [l, -16])

    def make_cars(self, num_cars, bottom, top):
        lane_speeds = {
            0: (65, 80),
            1: (65, 75),
            2: (60, 70),
            3: (60, 70),
            4: (55, 65),
            5:(50, 60)}
        vert_space = 128
        num_rows, rem = divmod(num_cars, len(self.lanes))
        if rem:
            num_rows += 1
        num_rows += 3
        total_vert = max(num_rows * vert_space, bottom - top)
        spots = [(lane, y) for lane in range(len(self.lanes))
                     for y in range(bottom - total_vert, bottom, vert_space)]
        spots = [s for s in spots
                     if not any((pg.Rect(self.lanes[s[0]].rect.centerx - 16, s[1] - 32, 32, vert_space).colliderect(car.rect)
                     for car in self.all_cars))]
        if len(spots) <= num_cars:
            num_cars = len(spots)
        spots = sample(spots, num_cars)
        for spot in spots:
            preferred_lane = randint(0, len(self.lanes) - 1)
            current_lane = spot[0]
            cruise_speed = randint(*lane_speeds[preferred_lane])
            vehicle_style = choice(VEHICLE_BAG)
            current_speed = cruise_speed
            centerx = self.lanes[current_lane].rect.centerx
            centery = spot[1]
            rect = pg.Rect(centerx - 16, centery - 32, 32, vert_space)
            img_name = choice(VEHICLE_IMAGES[vehicle_style])
            Vehicle((centerx, centery), cruise_speed, current_speed,
                       current_lane, preferred_lane, img_name, vehicle_style,
                       self.all_cars, self.other_cars, self.lanes[current_lane])


    def add_cars(self):
        py = self.player.y_pos
        top = sorted((x for x in self.other_cars.sprites()),
                            key=attrgetter("rect.bottom"))

        for c in top:
            if py - c.y_pos > 2000:
                c.kill()
        top = sorted((x for x in self.all_cars.sprites()),
                           key=attrgetter("rect.bottom"))
        indx = top.index(self.player)
        below = top[indx + 1:]
        killed = 0
        if len(below) < 10:
            num = 10 - len(below)
            dist = max(150, num * 80)
            top = int(py + 2000)
            self.make_cars(num, top, int(py + 600))
        elif len(below) > 25:
            for car in below[25:]:
                car.kill()
        if len(self.all_cars) < self.car_total:
            num = self.car_total - len(self.all_cars)
            top = sorted((x for x in self.all_cars.sprites()),
                               key=attrgetter("rect.top"))[0]
            self.make_cars(num, self.player.rect.top - 450, top.rect.top)

    def generate_obstacles(self, y_dist):
        if randint(0, 999) < int(y_dist * 15):
            img_name = choice(OBSTACLE_NAMES)
            Obstacle((self.lanes_left - randint(48, 160), -10),
                         img_name, self.obstacles)
        if randint(0, 999) < int(y_dist * 15):
            img_name = choice(OBSTACLE_NAMES)
            Obstacle((self.lanes_right + randint(48, 160), -10),
                         img_name, self.obstacles)

    def draw_car_map(self):
        self.map_surf.fill(pg.Color("gray5"))
        ys = [car.rect.top for car in self.all_cars]
        top = min(ys)
        bottom = max(ys)
        total = bottom - top
        try:
            y_scale = float(self.map_rect.h) / total
        except ZeroDivisionError:
            y_scale = 1
        x_scale = y_scale
        speed = self.player.current_speed
        for car in self.all_cars:
            car_top = int((car.rect.top - top)* y_scale)
            car_left = (car.rect.left - self.lanes_left) * x_scale
            if car.current_speed > speed:
                color = "blue"
            elif car.current_speed < speed:
                color = "red"
            else:
                color = "antiquewhite"
            pg.draw.rect(self.map_surf, pg.Color(color),
                              ((car_left, car_top), (1, 2)))

    def update_user(self):
        miles = px_to_miles(self.player.distance)
        earned = float("{:.1f}".format(miles * (int(miles) + 1)))
        self.user.mileage_earned += earned
        self.user.mileage += earned
        if self.user.best_trip < miles:
            self.user.best_trip = miles

    def check_player_crash(self):
        crashes = pg.sprite.spritecollide(self.player, self.other_cars, False,
                                                     collided=pg.sprite.collide_mask)
        if crashes:
            self.collisions_active = True
            self.player_crashed = True
            self.player.engine_sound.stop()
            self.player.horn_sound.stop()
            self.player.tires_sound.stop()
            self.update_user()
            self.fade_out()

    def check_crashes(self):
        collided = set()
        py = self.player.y_pos
        group = self.all_cars
        for car in group:
            if car not in collided and not car.crashed:
                crashed = pg.sprite.spritecollide(car, group, False)
                if len(crashed) > 1:
                    choice(self.crash_sounds).play()
                    for c in crashed:
                        if c not in collided:
                            self.crashes += 1
                        c.rect.move_ip(randint(-8, 8), randint(-8, 0))
                        c.crashed = True
                        collided.add(c)

    def leave_state(self):
        self.done = True
        self.next = "CHOOSE_VEHICLE"

    def fade_out(self):
        self.cover = pg.Surface(prepare.SCREEN_SIZE)
        self.cover.fill((1, 1, 1))
        self.cover_alpha = 0
        ani = Animation(cover_alpha=255, duration=9000)
        ani.start(self)
        ani.callback = self.leave_state
        self.animations.add(ani)

    def make_achievements(self):
        self.achievements = pg.sprite.Group()
        for name, text, validator in ACHIEVEMENTS:
            if name not in self.user.achievements:
                Achievement(name, text, validator, self.achievements)

    def check_achievements(self):
        if not any((x.active for x in self.achievements)):
            for a in self.achievements:
                if a.validator(self):
                    a.active = True
                    self.user.achievements.append(a.name)
                    a.fade_in(self.animations)
                    break

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
            self.user.save()
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
                self.user.save()
        if not self.player_crashed:
            self.player.get_event(event)

    def update(self, dt):
        self.elapsed += dt
        self.animations.update(dt)
        keys = pg.key.get_pressed()
        last_y = self.player.y_pos
        if not self.player_crashed:
            self.player.update(dt, keys, self.lanes)
        y_diff = last_y - self.player.y_pos
        self.obstacles.update(y_diff * 1.5)
        self.generate_obstacles(y_diff)
        for ob in self.obstacles:
            if ob.y_pos > prepare.SCREEN_RECT.bottom + 64:
                ob.kill()
        self.markings_y += y_diff * 1.5
        self.left_edge[1][1] += y_diff * 1.5
        self.right_edge[1][1] += y_diff * 1.5
        if self.markings_y > 0:
            self.markings_y = self.markings_reset + self.markings_y
        if self.left_edge[1][1] >= 0:
            self.left_edge[1][1] -= 16
            self.right_edge[1][1] -= 16
        self.other_cars.update(dt, self.lanes, self.all_cars, self.animations)
        self.speedometer.update(self.player)
        #self.draw_car_map()
        if not self.player_crashed:
            self.check_player_crash()
        if self.collisions_active:
            self.check_crashes()
        if self.cover:
            self.cover.set_alpha(self.cover_alpha)
        self.add_cars()
        self.check_achievements()
        self.achievements.update()

    def draw(self, surface):
        surface.fill(self.bg_color)
        self.draw_lane_markings(surface)
        surface.blit(self.left_edge[0],
                         (int(self.left_edge[1][0]), int(self.left_edge[1][1])))
        surface.blit(self.right_edge[0],
                         (int(self.right_edge[1][0]), int(self.right_edge[1][1])))
        for ob in self.obstacles:
            if -10 < ob.y_pos:
                ob.draw(surface)
        offset = 0, 400 - self.player.rect.centery
        for car in self.all_cars:
            rect = car.rect.move(offset)
            if -30 <  rect.centery < prepare.SCREEN_SIZE[1] + 30:
                surface.blit(car.image, rect)
        self.speedometer.draw(surface)
        #surface.blit(self.map_surf, self.map_rect)
        #pg.draw.rect(surface, pg.Color("antiquewhite"),
        #                   self.map_rect.inflate(6, 6), 3)
        if self.cover:
            surface.blit(self.cover, (0, 0))
        for a in self.achievements:
            if a.active:
                a.draw(surface)