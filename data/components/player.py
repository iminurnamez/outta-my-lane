import pygame as pg

from .. import prepare
from .vehicles import Vehicle, mph_to_px_per_ms

CONTROLS = {
    "Accelerate": pg.K_UP,
    "Brake": pg.K_DOWN,
    "Steer Left": pg.K_LEFT,
    "Steer Right": pg.K_RIGHT,
    "Horn": pg.K_SPACE}


class Player(Vehicle):
    def __init__(self, centerpoint, cruising_speed, current_speed, current_lane,
                      preferred_lane, vehicle_style, *groups):
        super(Player, self).__init__(centerpoint, cruising_speed, current_speed,
                                                current_lane, preferred_lane, vehicle_style,
                                                *groups)
        self.x_velocity = 0
        self.steering = .0002
        self.distance = 0
        self.accel_rate = self.max_acceleration / 1000.
        self.decel_rate = self.max_deceleration / 1000.
        self.deceleration = 0
        self.drag = mph_to_px_per_ms(.5) / 1000.
        self.last_slowdown = 0
        self.last_speedup = 0
        self.engine_sound = prepare.SFX["engine0"]
        self.engine_sound_no = 0
        self.engine_started = False
        self.tires_sound = prepare.SFX["tires"]
        self.direction_stack = []

    def add_direction(self, direction):
        if direction in self.direction_stack:
            self.direction_stack.remove(direction)
        self.direction_stack.append(direction)

    def remove_direction(self, direction):
        if direction in self.direction_stack:
            self.direction_stack.remove(direction)

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == CONTROLS["Brake"]:
                now = pg.time.get_ticks()
                if now - self.last_slowdown < 350:
                    self.deceleration = self.max_deceleration
                    self.tires_sound.play()
                self.last_slowdown = now
            elif event.key == CONTROLS["Horn"]:
                if self.horn_loopable:
                    self.horn_sound.play(-1)
                else:
                    self.horn_sound.play()
            elif event.key == CONTROLS["Steer Left"]:
                self.add_direction(-1)
            elif event.key == CONTROLS["Steer Right"]:
                self.add_direction(1)
        elif event.type == pg.KEYUP:
            if event.key == CONTROLS["Horn"]:
                if self.horn_loopable:
                    self.horn_sound.stop()
            elif event.key == CONTROLS["Steer Left"]:
                self.remove_direction(-1)
            elif event.key == CONTROLS["Steer Right"]:
                self.remove_direction(1)

    def update(self, dt, keys, lanes):
        if not self.engine_started:
            self.engine_sound.play(-1)
            self.engine_started = True
        else:
            eng_sound = int((self.current_speed / float(self.top_speed)) * 10)
            if eng_sound != self.engine_sound_no:
                self.engine_sound.stop()
                self.engine_sound = prepare.SFX["engine{}".format(eng_sound)]
                self.engine_sound.set_volume(.125)
                self.engine_sound.play(-1)
                self.engine_sound_no = eng_sound
        centered = self.rect.copy()
        centered.centery = 400
        for lane in lanes.values():
            if centered.colliderect(lane.rect):
                lane.add(self)
            else:
                lane.remove(self)
        if keys[CONTROLS["Brake"]]:
            self.acceleration = 0
            self.deceleration += self.decel_rate * dt
            if self.deceleration > self.max_deceleration:
                self.deceleration = self.max_deceleration
            self.decelerate(self.deceleration * dt)
        else:
            self.deceleration = 0
            self.tires_sound.stop()
            if keys[CONTROLS["Accelerate"]]:
                self.accelerate(self.max_acceleration * dt)
            else:
                self.acceleration = 0
        left = keys[CONTROLS["Steer Left"]]
        right = keys[CONTROLS["Steer Right"]]
        if self.direction_stack:
            current = self.direction_stack[-1]
            if current == -1:
                self.x_velocity -= self.steering * dt
                if self.x_velocity < -self.steering * 1500:
                    self.x_velocity = -self.steering * 1500
            elif current == 1:
                self.x_velocity += self.steering * dt
                if self.x_velocity > self.steering * 1500:
                    self.x_velocity = self.steering * 1500
        else:
            if self.x_velocity > 0:
                self.x_velocity -= min(self.decel_rate * 4000 * dt, self.x_velocity)
            elif self.x_velocity < 0:
                self.x_velocity += min(self.decel_rate * 4000 * dt, -self.x_velocity)
        self.current_speed -= self.drag * dt
        if self.current_speed < 0:
            self.current_speed = 0
        if self.rect.left < lanes[0].rect.left or self.rect.right > lanes[len(lanes) - 1].rect.right:
            self.current_speed *= .995
        y_dist = (self.current_speed * dt)
        self.distance += y_dist
        self.x_pos = self.x_pos + (self.x_velocity * dt)
        self.y_pos = self.y_pos - y_dist
        self.rect.center = self.x_pos, self.y_pos
