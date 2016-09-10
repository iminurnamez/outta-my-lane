from random import randint

import pygame as pg

from .. import tools, prepare
from ..components.animation import Animation
from ..components.labels import Label, Button, ButtonGroup
from ..components.user import load_user
from ..components.player import CONTROLS


class ControlIcon(pg.sprite.DirtySprite):
    def __init__(self, topleft, size, name, key):
        self.labels = pg.sprite.Group()
        self.name = name
        self.key = key
        self.keyname= pg.key.name(key)
        self.rect = pg.Rect(topleft, size)
        self.label = Label(name, {"midleft": (self.rect.left + 20, self.rect.centery)},
                                  self.labels, text_color="gray80", font_size=32)
        self.key_rect = pg.Rect(0, 0, 100, 40)
        self.key_rect.midleft = self.rect.left + 250, self.rect.centery
        self.key_label = Label(self.keyname, {"center": self.key_rect.center},
                                         self.labels, text_color="gray20")
        if name == "Brake":
            text = "Double-tap for hard brake"
            Label(text, {"topleft": (self.label.rect.left, self.label.rect.bottom - 5)},
                    self.labels, text_color="gray60", font_size=16)

    def change_key(self, key_constant):
        self.key = key_constant
        self.keyname = pg.key.name(self.key)
        self.key_label.set_text(self.keyname)
        CONTROLS[self.name] = self.key

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color("gray40"), self.rect)
        pg.draw.rect(surface, pg.Color("gray80"), self.key_rect)
        self.labels.draw(surface)
        pg.draw.rect(surface, pg.Color("gray60"), self.rect, 2)
        pg.draw.rect(surface, pg.Color("gray60"), self.key_rect, 2)

class ControlsScreen(tools._State):
    def __init__(self):
        super(ControlsScreen, self).__init__()
        self.next = "TITLE"

    def make_labels(self):
        sr = prepare.SCREEN_RECT
        ital_font = prepare.FONTS["weblysleekuisbi"]
        self.selecting_labels = pg.sprite.Group()
        self.entering_labels = pg.sprite.Group()
        Label("Controls", {"midtop": (sr.centerx, 0)}, self.selecting_labels,
                self.entering_labels, font_size=64, text_color="antiquewhite")
        Label("Use Arrow Keys To Navigate", {"midtop": (sr.centerx, 620)},
                self.selecting_labels, font_size=16, text_color="gray80",
                font_path=ital_font)
        Label("Press Enter To Unlock / Select", {"midtop": (sr.centerx, 640)},
                self.selecting_labels, font_size=16, text_color="gray80",
                font_path=ital_font)
        Label("Press the key you want to assign", {"midtop": (sr.centerx, 620)},
                self.entering_labels, font_size=16, text_color="gray80",
                font_path=ital_font)
        Label("Press X to return to main menu", {"midtop": (sr.centerx,680)},
                self.entering_labels, self.selecting_labels, font_size=16,
                text_color="gray80", font_path=ital_font)

    def make_icons(self):
        self.icons = []
        top = 100
        left = 50
        w, h = 500, 80
        for name in ("Accelerate", "Brake", "Steer Left", "Steer Right", "Horn"):
            icon = ControlIcon((left, top), (w, h), name, CONTROLS[name])
            self.icons.append(icon)
            top += h + 20

    def switch_icons(self, direction):
        try:
            new_icon = self.icons[self.icon_num + direction]
            self.icon_num += direction
        except IndexError:
            if direction == -1:
                self.icon_num = len(self.icons) - 1
            else:
                self.icon_num = 0

    def startup(self, persistent):
        self.persist = persistent
        self.entering = False
        self.make_labels()
        self.make_icons()
        self.icon_num = 0

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            elif event.key == pg.K_x:
                self.done = True
            if not self.entering:
                if event.key == pg.K_DOWN:
                   self.switch_icons(1)
                elif event.key == pg.K_UP:
                    self.switch_icons(-1)
                elif event.key == pg.K_RETURN:
                    self.entering = True
            else:
                if event.key == pg.K_RETURN:
                    self.entering = False
                else:
                    icon = self.icons[self.icon_num]
                    icon.change_key(event.key)
                    self.entering = False

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(pg.Color("gray5"))
        if self.entering:
            self.entering_labels.draw(surface)
        else:
            self.selecting_labels.draw(surface)
        for icon in self.icons:
            icon.draw(surface)
        pg.draw.rect(surface, pg.Color("antiquewhite"), self.icons[self.icon_num].rect.inflate(4, 4), 4)