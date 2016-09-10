


from random import randint

import pygame as pg

from .. import tools, prepare
from ..components.animation import Animation
from ..components.labels import Label, Button, ButtonGroup
from ..components.user import load_user



class TitleScreen(tools._State):
    def __init__(self):
        super(TitleScreen, self).__init__()
        self.animations = pg.sprite.Group()
        self.labels = pg.sprite.Group()
        self.buttons = ButtonGroup()
        self.make_title()
        self.make_buttons()
        self.pair_num = 1
        self.switch_buttons(-1)
        self.buttons_joined = False
        self.help_labels = pg.sprite.Group()
        sr = prepare.SCREEN_RECT
        ital_font = prepare.FONTS["weblysleekuisbi"]
        Label("Use Arrow Keys To Navigate", {"midtop": (sr.centerx, 660)},
                self.help_labels, font_size=16, text_color="gray80",
                font_path=ital_font)
        Label("Press Enter To Unlock / Select", {"midtop": (sr.centerx, 680)},
                self.help_labels, font_size=16, text_color="gray80",
                font_path=ital_font)
        self.click_sound = prepare.SFX["click_2"]        

    def make_title(self):
        sound = prepare.SFX["crash3"]
        cx = prepare.SCREEN_RECT.centerx
        dist = 5000
        dur = 4500
        top = 50
        title1 = Label("OUTTA M", {"topright": (cx-dist, top)}, self.labels,
                            font_size=96, font_path=prepare.FONTS["OstrichSans-Heavy"])
        ani1 = Animation(right=cx, duration=dur, transition="linear",
                                  round_values=True)
        ani1.start(title1.rect)
        title2 = Label("Y LANE!!!", {"topleft": (cx + dist, top)}, self.labels,
                            font_size=96, font_path=prepare.FONTS["OstrichSans-Heavy"])
        ani2 = Animation(left=cx, duration=dur, transition="linear",
                                  round_values=True)
        ani2.start(title2.rect)
        ani2.callback = sound.play
        self.animations.add(ani1, ani2)

    def make_buttons(self):
        cx = prepare.SCREEN_RECT.centerx
        top = 250
        delay = 2000
        dist = 5000
        dur = 4500
        b_size = (300, 80)
        self.button_pairs = []
        for name, callback in [("PLAY", self.to_game), ("CONTROLS", self.to_controls)]:
            sound_num = randint(1, 7)
            sound = prepare.SFX["crash{}".format(sound_num)]
            label = Label(name, {"topleft": (0, 0)}, font_size=48,
                                fill_color="gray60", text_color="antiquewhite")
            surf = pg.Surface(b_size)
            surf.fill(pg.Color("gray60"))
            surf_rect = surf.get_rect()
            label.rect.center = surf_rect.center
            label.draw(surf)
            pg.draw.rect(surf, pg.Color("gray80"), surf_rect, 3)
            left = surf.subsurface((0, 0, b_size[0] // 2, b_size[1]))
            lw = left.get_width()
            right = surf.subsurface((lw, 0, b_size[0] - lw, b_size[1]))

            b1 = Button((cx - (lw + dist), top), self.buttons,
                               button_size=left.get_size(), idle_image=left,
                               call=callback, active=False,
                               bindings=(pg.K_RETURN,))
            ani1 = Animation(right=cx, duration=dur, delay=delay,
                                      round_values=True)
            ani1.start(b1.rect)
            b2 = Button((cx + dist, top), self.buttons, button_size=right.get_size(),
                               idle_image=right, call=callback, active=False, 
                               bindings=(pg.K_RETURN,))
            ani2 = Animation(left=cx, duration=dur, delay=delay, round_values=True)
            ani2.callback = sound.play
            ani2.start(b2.rect)
            self.animations.add(ani1, ani2)
            self.button_pairs.append((b1, b2))

            top += 200
            delay += 1000



    def startup(self, persistent):
        self.persist = persistent
        if not pg.mixer.music.get_busy():
            pg.mixer.music.load(prepare.MUSIC["DST-RailJet-LongSeamlessLoop"])
            pg.mixer.music.play(-1)


    def switch_buttons(self, direction):
        old_pair = self.button_pairs[self.pair_num]
        try:
            new_pair = self.button_pairs[self.pair_num + direction]
            self.pair_num += direction
        except IndexError:
            if direction == -1:
                self.pair_num = len(self.button_pairs) -1
            else:
                self.pair_num = 0
            new_pair = self.button_pairs[self.pair_num]
        for button in old_pair:
            button.active = False
        for button in new_pair:
            button.active = True



    def to_game(self, *args):
        self.done = True
        self.next = "CHOOSE_VEHICLE"
        self.persist["user"] = load_user()

    def to_controls(self, *args):
        self.done  = True
        self.next = "CONTROLS_SCREEN"

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            elif event.key == pg.K_DOWN:
                self.switch_buttons(1)
                self.click_sound.play()
            elif event.key == pg.K_UP:
                self.switch_buttons(-1)
                self.click_sound.play()
        self.buttons.get_event(event)

    def update(self, dt):
        self.animations.update(dt)
        self.buttons.update(pg.mouse.get_pos())
        if self.button_pairs[-1][0].rect.right == prepare.SCREEN_RECT.centerx:
            self.buttons_joined = True
        b1, b2 = self.button_pairs[self.pair_num]
        self.pair_rect = pg.Rect(b1.rect.left, b1.rect.top, b1.rect.w + b2.rect.w, b1.rect.h).inflate(4, 4)

    def draw(self, surface):
        surface.fill(pg.Color("gray5"))
        self.labels.draw(surface)
        self.buttons.draw(surface)
        if self.buttons_joined:
            pg.draw.rect(surface, pg.Color("antiquewhite"), self.pair_rect, 4)
            self.help_labels.draw(surface)
