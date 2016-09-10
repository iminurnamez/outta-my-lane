import pygame as pg

from .. import prepare
from .labels import Label
from .vehicles import px_per_ms_to_mph, px_to_miles


class Speedometer(pg.sprite.DirtySprite):
    def __init__(self, topleft):
        self.dial_img = prepare.GFX["dial"]
        self.dial_rect = self.dial_img.get_rect(topleft=topleft)
        self.needle_img = prepare.GFX["needle"]
        self.make_odom_labels()
        self.low_speed = 0
        self.high_speed = 110
        self.low_angle = 194
        self.high_angle = -14
        self.speed_range = self.high_speed - self.low_speed
        self.needle_center = self.dial_rect.centerx, self.dial_rect.top + 100
        self.needle_arc = self.low_angle - self.high_angle
        self.initial_angle = 90
        self.draw_dial_numbers()

    def draw_dial_numbers(self):
        angle_span = self.low_angle - self.high_angle
        for x in range(self.low_speed, self.high_speed + 1, 10):
             ratio = x / float(self.high_speed)
             img = pg.Surface(self.dial_rect.size).convert_alpha()
             img.fill((0, 0, 0, 0))
             label = Label("{}".format(x), {"midtop": (img.get_width() // 2, 5)},
                                 font_size=10, text_color="antiquewhite")
             label.draw(img)
             angle = (self.low_angle - (ratio * angle_span)) - 90
             rot = pg.transform.rotate(img, angle)
             dial_rect = self.dial_img.get_rect()
             rect = rot.get_rect(center=dial_rect.center)
             self.dial_img.blit(rot, rect)



    def make_odom_labels(self):
        self.odom_labels = []
        left, top = self.dial_rect.left + 45, self.dial_rect.top + 120
        self.bg_rects = []
        for x in range(7):
            style = {
                "text_color": "antiquewhite",
                "fill_color": "gray5",
                "font_size": 10}

            if x == 6:
                style = {"text_color": "gray5",
                            "fill_color": "antiquewhite",
                            "font_size": 10}
            label = Label("0", {"topleft": (left, top)}, **style)
            self.odom_labels.append(label)
            bg = pg.Surface(label.rect.size)
            bg.fill(pg.Color(style["fill_color"]))
            self.bg_rects.append((bg, (left, top)))
            left += 10

    def get_needle_angle(self, mph):
        if mph <= self.low_speed:
            angle = self.low_angle - self.initial_angle
        elif mph >=  self.high_speed:
            angle = self.high_angle - self.initial_angle
        else:
            spd_ratio = (mph - self.low_speed) / float(self.speed_range)
            angle = (self.low_angle - (spd_ratio * self.needle_arc)) - self.initial_angle
        return angle

    def update(self, player):
        mph = px_per_ms_to_mph(player.current_speed)
        dist = px_to_miles(player.distance)
        odom_dist = [x for x in str(int(dist * 10))]
        for new_val, label in zip(odom_dist[::-1], self.odom_labels[::-1]):
            label.set_text(new_val)
        needle_angle = self.get_needle_angle(mph)
        self.needle = pg.transform.rotate(self.needle_img, needle_angle)
        self.needle_rect = self.needle.get_rect(center=self.needle_center)

    def draw(self, surface):
        surface.blit(self.dial_img, self.dial_rect)
        for bg, bg_rect in self.bg_rects:
            surface.blit(bg, bg_rect)
        for label in self.odom_labels:
            label.draw(surface)
        surface.blit(self.needle, self.needle_rect)