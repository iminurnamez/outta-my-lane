import pygame as pg

from ..components.animation import Animation, Task
from ..components.labels import Label
from ..components.vehicles import miles_to_px


class Achievement(pg.sprite.Sprite):
    def __init__(self, name, text, validator, *groups):
        super(Achievement, self).__init__(*groups)
        self.active = False
        self.name = name
        self.alpha = 0
        self.validator = validator
        self.image = pg.Surface((250, 40))
        self.image.fill(pg.Color("gray20"))
        self.rect = self.image.get_rect()
        label = Label(name, {"midtop": (self.rect.centerx, self.rect.top)},
                            font_size=16, text_color="gray80")
        label2 = Label(text, {"midbottom": (self.rect.centerx, self.rect.bottom)},
                              font_size=12, text_color="gray60")
        label.draw(self.image)
        label2.draw(self.image)
        pg.draw.rect(self.image, pg.Color("gray60"), self.rect, 3)
        self.image.set_alpha(self.alpha)

    def fade_in(self, animations):
        duration = 3500
        ani = Animation(alpha=240, duration=duration)
        self.active = True
        ani.start(self)
        delay = duration + 5000
        task = Task(self.fade_out, delay, args=(animations,))
        animations.add(ani, task)

    def fade_out(self, animations):
        ani = Animation(alpha=0, duration=2000)
        ani.callback = self.kill
        ani.start(self)
        animations.add(ani)

    def update(self):
        self.image.set_alpha(self.alpha)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


ACHIEVEMENTS = [
        ("The First Mile Is The Hardest", "Travel one mile without crashing",
        lambda x: x.player.distance > miles_to_px(1)),
        ("Revved Up Like A Deuce", "Travel two miles without crashing",
        lambda x: x.player.distance > miles_to_px(2)),
        ("Third Mile's A Charm", "Travel three miles without crashing",
        lambda x: x.player.distance > miles_to_px(3)),
        ("Four From The Floor", "Travel four miles without crashing",
        lambda x: x.player.distance > miles_to_px(4)),
        ("Alive For Five", "Travel five miles without crashing",
        lambda x: x.player.distance > miles_to_px(5)),
        ("AtTENtive Driver", "Travel ten miles without crashing",
        lambda x: x.player.distance > miles_to_px(10)),
        ("You Gotta Start Somewhere", "Purchase a Clunker",
        lambda x: "clunker" in x.user.unlocked),
        ("For The Long Haul", "Purchase a Box Truck",
        lambda x: any(("box-truck" in name for name in x.user.unlocked))),
        ("Crossover Appeal", "Purchase an El Cochino",
        lambda x: any(("elcochino" in name for name in x.user.unlocked))),
        ("Hey, Timmy, Nice Backpack", "Purchase a School Bus",
        lambda x: any(("school-bus" in name for name in x.user.unlocked))),
        ("Cheese It, The Fuzz", "Pruchase a Cruiser",
        lambda x: any(("cruiser" in name for name in x.user.unlocked))),
        ("No Cat Left Behind", "Purchase a Firetruck",
        lambda x: any(("firetruck" in name for name in x.user.unlocked))),
        ("A Sensible Choice", "Purchase a Sedan",
        lambda x: any(("sedan" in name for name in x.user.unlocked))),
        ("An Even More Sensible Choice", "Purchase a Coupe",
        lambda x: any(("coupe" in name for name in x.user.unlocked))),
        ("Pyg Went To Market", "Purchase a Produce Truck",
        lambda x: any(("produce-truck" in name for name in x.user.unlocked))),
        ("Style For Miles", "Purchase a Hardtop",
        lambda x: any(("hardtop" in name for name in x.user.unlocked))),
        ("Crisis Management", "Purchase a Sports Car",
        lambda x: any(("sports car" in name for name in x.user.unlocked))),
        ("Help Is On The Way", "Purchase an Ambulance ",
        lambda x: any(("ambulance" in name for name in x.user.unlocked))),
        ("Hi Ho, Hi Ho", "Purchase a Work Van ",
        lambda x: any(("work-van" in name for name in x.user.unlocked))),
        ("Sturgis Deployer", "Purchase a Bike",
        lambda x: any(("bike" in name for name in x.user.unlocked))),
        ("Two-Car Garage", "Purchase two vehicles",
        lambda x: len(x.user.unlocked) > 1),
        ("Motorhead", "Purchase five vehicles",
        lambda x: len(x.user.unlocked) >= 5),
        ("Collectour", "Purchase ten vehicles",
        lambda x: len(x.user.unlocked) >= 10),
        ("Carficionado", "Purchase twenty vehicles",
        lambda x: len(x.user.unlocked) >= 20)
        ]