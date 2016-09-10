import pygame as pg

from .. import tools, prepare
from ..components.labels import Label
from ..components.vehicles import Vehicle, VEHICLE_STYLES, VEHICLE_IMAGES


class ChooseVehicle(tools._State):
    def __init__(self):
        super(ChooseVehicle, self).__init__()
        self.click_sound = prepare.SFX["click_2"]
        self.negative_sound = prepare.SFX["negative_2"]
        self.icon_index = [0, 0]
        
    def startup(self, persistent):
        self.persist = persistent
        self.user = self.persist["user"]
        self.make_labels()
        self.make_vehicle_icons()
        self.cheat_code = list("cheat")[::-1]

    def make_labels(self):
        sr = prepare.SCREEN_RECT
        self.labels = pg.sprite.Group()
        ital_font = prepare.FONTS["weblysleekuisbi"]
        self.miles_label = Label("Miles: {:.1f}".format(self.user.mileage),
                                           {"midtop": (sr.centerx, -10)}, self.labels,
                                           font_size=32, text_color="antiquewhite")
        Label("Spend Miles To Unlock New Vehicles", {"midtop": (sr.centerx, 23)},
                 self.labels, font_size=16, text_color="gray80", font_path=ital_font)
        text = "Use Arrow Keys To Navigate - Press Enter To Unlock / Select"
        Label(text, {"midtop": (sr.centerx, 700)}, self.labels, font_size=16,
                 text_color="gray80", font_path=ital_font)


    def make_vehicle_icons(self):
        self.icons = []
        self.icons.append([])
        icon_index = 0
        left = 10
        top = 50
        h_space = 60
        v_space = 110
        x = left
        y = top
        for style in sorted(VEHICLE_STYLES.keys(), key=lambda x: VEHICLE_STYLES[x][5]):
            for img_name in VEHICLE_IMAGES[style]:
                rect = pg.Rect(0, 0, 48, 80)
                img = prepare.GFX[img_name]
                img_rect = img.get_rect()
                img_rect.center = rect.center
                icon = pg.Surface(rect.size)
                unlock_cost = VEHICLE_STYLES[style][5]
                if img_name not in self.user.unlocked:
                    if self.user.mileage >= unlock_cost:
                        icon.fill(pg.Color("gray20"))
                        text_color = "gray80"
                    else:
                        icon.fill(pg.Color("gray10"))
                        text_color = "gray60"
                    text = "{} mi".format(unlock_cost)
                else:
                    text_color = "antiquewhite"
                    text = "Unlocked"
                    icon.fill(pg.Color("gray40"))
                icon.blit(img, img_rect)
                pg.draw.rect(icon, pg.Color("gray60"), rect, 2)
                rect.topleft = x, y
                self.icons[icon_index].append((icon, rect, style, img_name))
                n = Label(style.title(), {"midtop": (rect.centerx, rect.bottom)},
                               self.labels, text_color=text_color, font_size=8)
                Label(text, {"midtop": (n.rect.centerx, n.rect.bottom - 2)},
                         self.labels, text_color=text_color, font_size=8)

                x += h_space
                if x > 600:
                    x = left
                    y += v_space
                    self.icons.append([])
                    icon_index += 1

    def choose_car(self, style, image_name):
        if image_name in self.user.unlocked:
            self.persist["style"] = style
            self.persist["vehicle_image"] = image_name
            self.done = True
            self.next = "GAMEPLAY"
            self.user.save()
        elif self.user.mileage >= VEHICLE_STYLES[style][5]:
            self.user.mileage -= VEHICLE_STYLES[style][5]
            self.user.unlocked.append(image_name)
            self.persist["style"] = style
            self.persist["vehicle_image"] = image_name
            self.done = True
            self.next = "GAMEPLAY"
            self.user.save()
        else:
            self.negative_sound.play()        

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.unicode == self.cheat_code[-1]:
                self.cheat_code.pop()
                if not self.cheat_code:
                    self.user.mileage += 100
                    self.miles_label.set_text("Miles: {:.1f}".format(self.user.mileage))
                    self.make_vehicle_icons()
                    self.cheat_code = list("cheat")[::-1]
            else:
                self.cheat_code = list("cheat")[::-1]
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            elif event.key == pg.K_DOWN:
                if self.icon_index[1] < len(self.icons) - 1:
                    self.icon_index[1] += 1
                else:
                    self.icon_index[1] = 0
                if self.icon_index[0] > len(self.icons[self.icon_index[1]]) - 1:
                    self.icon_index[0] = len(self.icons[self.icon_index[1]]) - 1
                self.click_sound.play()
            elif event.key == pg.K_UP:
                if self.icon_index[1] > 0:
                    self.icon_index[1] -= 1
                else:
                    self.icon_index[1] = len(self.icons) - 1
                    if self.icon_index[0] > len(self.icons[self.icon_index[1]]) - 1:
                        self.icon_index[0] = len(self.icons[self.icon_index[1]]) - 1
                self.click_sound.play()
            elif event.key == pg.K_LEFT:
                if self.icon_index[0] > 0:
                    self.icon_index[0] -= 1
                else:
                    self.icon_index[0] = len(self.icons[self.icon_index[1]]) - 1
                self.click_sound.play()
            elif event.key == pg.K_RIGHT:
                if self.icon_index[0] < len(self.icons[self.icon_index[1]]) - 1:
                    self.icon_index[0] += 1
                else:
                    self.icon_index[0] = 0
                self.click_sound.play()    
            elif event.key == pg.K_RETURN:
                current = self.icons[self.icon_index[1]][self.icon_index[0]]
                self.choose_car(current[2], current[3])


    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(pg.Color("gray5"))
        self.labels.draw(surface)
        for row in self.icons:
            for icon, rect, style, image_name in row:
                surface.blit(icon, rect)
        current = self.icons[self.icon_index[1]][self.icon_index[0]]
        pg.draw.rect(surface, pg.Color("antiquewhite"), current[1], 2)
