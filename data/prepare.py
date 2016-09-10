import os
import pygame as pg
from . import tools


SCREEN_SIZE = (608, 720)
ORIGINAL_CAPTION = "Outta My Lane!!!"
GRASS = (39, 124, 48)

pg.mixer.pre_init(44100, 16, 1, 512)

pg.init()
os.environ['SDL_VIDEO_CENTERED'] = "TRUE"
pg.display.set_caption(ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(SCREEN_SIZE)
SCREEN_RECT = SCREEN.get_rect()


FONTS = tools.load_all_fonts(os.path.join("resources", "fonts"))
MUSIC = tools.load_all_music(os.path.join("resources", "music"))
SFX   = tools.load_all_sfx(os.path.join("resources", "sound"))
GFX   = tools.load_all_gfx(os.path.join("resources", "graphics"))

SFX["horn4"].set_volume(.3)
SFX["horn3"].set_volume(.5)
SFX["horn2"].set_volume(.5)
SFX["horn1"].set_volume(.5)
SFX["truck1"].set_volume(.5)
SFX["truck2"].set_volume(.7)
SFX["truck3"].set_volume(.5)
SFX["truck4"].set_volume(2)
SFX["oldhorn"].set_volume(.5)
SFX["ambulance"].set_volume(.4)
SFX["firetruck"].set_volume(.5)
SFX["police2"].set_volume(.5)