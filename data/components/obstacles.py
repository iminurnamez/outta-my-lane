import pygame as pg

from .. import prepare

OBSTACLE_NAMES = ["tree{}".format(x) for x in range(1, 13)]
OBSTACLE_NAMES.extend(["rock{}".format(x) for x in range(1, 5)])

FOOTPRINTS = {
    "tree1": (8, 2),
    "tree2": (8, 2),
    "tree3": (6, 2),
    "tree4": (6, 2),
    "tree5": (6, 2),
    "tree6": (6, 2),
    "tree7": (4, 2),
    "tree8": (4, 2),
    "tree9": (4, 2),
    "tree10": (4, 2),
    "tree11": (4, 2),
    "tree12": (4, 2),
    "rock1": (14, 3),
    "rock2": (13, 2),
    "rock3": (24, 3),
    "rock4": (24, 4)
    }


class Obstacle(pg.sprite.DirtySprite):
    def __init__(self, midbottom, image_name, *groups):
        super(Obstacle, self).__init__(*groups)
        self.image = prepare.GFX[image_name]
        self.rect = self.image.get_rect(midbottom=midbottom)
        self.footprint = pg.Rect((0, 0), FOOTPRINTS[image_name])
        self.footprint.midbottom = self.rect.midbottom
        self.y_pos = self.rect.bottom

    def update(self, y_move):
        self.y_pos += y_move
        self.rect.bottom = self.y_pos
        self.footprint.bottom = self.y_pos

    def collides_with_player(self, player):
        if self.footprint.colliderect(player.rect):
            return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect)