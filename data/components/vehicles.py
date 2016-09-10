from operator import attrgetter
from random import choice, randint

import pygame as pg

from .. import prepare
from .animation import Animation, Task


PX_PER_MI = 14080

def mph_to_px_per_ms(mph):
    #total px per hour / num_ms in an hour
    return (PX_PER_MI * mph) / 3600000.

def px_per_ms_to_mph(px_per_ms):
    #convert per ms speed to mph
    return px_per_ms * (3600000. / PX_PER_MI)

def px_to_miles(pixels):
    #for odometer readings
    return float(pixels) / PX_PER_MI

def miles_to_px(miles):
    return miles * PX_PER_MI


VEHICLE_STYLES = {
        #lane_change_time, deceleration, acceleration, top_speed, horn_sound, unlock_cost
        "clunker": (2500, 10, 3, 65, "oldhorn", 0),
        "produce truck": (3000, 12, 4, 75, "truck2", 2),
        "box truck": (3000, 12, 4, 75, "truck3", 2),
        "school bus": (2500, 15, 4, 75, "truck1", 5),
        "firetruck": (2500, 18, 5, 70, "firetruck", 5),
        "ambulance": (2000, 22, 6, 80, "ambulance", 5),
        "work van": (2000, 25, 7, 80, "truck4", 5),
        "sedan": (1500, 30, 8, 80, "horn3", 10),
        "coupe": (1300, 35, 8.5, 85, "horn4", 15),
        "hardtop": (1500, 30, 9.5, 90, "horn4", 20),
        "cruiser": (1200, 35, 9, 90, "police2", 25),
        "el cochino": (1000, 35, 9, 95, "horn1", 30),
        "bike": (400, 55, 10, 100, "horn2", 35),
        "sports car": (500, 50, 11, 105, "horn2", 40)
        }

VEHICLE_IMAGES = {
        "clunker": ["clunker"],
        "produce truck": ["produce-truck{}".format(x) for x in range(1, 6)],
        "box truck": ["box-truck{}".format(x) for x in range(1, 9)],
        "school bus": ["schoolbus"],
        "ambulance": ["ambulance"],
        "firetruck": ["firetruck"],
        "work van": ["work-van"],
        "sedan": ["sedan{}".format(x) for x in range(1, 10)],
        "coupe": ["coupe{}".format(x) for x in range(1, 8)],
        "hardtop": ["hardtop{}".format(x) for x in range(1, 9)],
        "el cochino": ["elcochino{}".format(x) for x in range(1, 6)],
        "cruiser": ["cruiser"],
        "bike": ["biker"],
        "sports car": ["sports-car{}".format(x) for x in range(1, 10)]}

LOOPABLE_HORNS = ["firetruck", "police2", "ambulance"]

VEHICLE_FREQUENCIES = {
        "sedan": 15,
        "coupe": 15,
        "el cochino": 2,
        "produce truck": 4,
        "box truck": 10,
        "ambulance": 1,
        "school bus": 1,
        "cruiser": 1,
        "clunker": 1,
        "bike": 3,
        "hardtop": 3,
        "firetruck": 1,
        "work van": 1,
        "sports car": 2}


class Vehicle(pg.sprite.DirtySprite):
    def __init__(self, centerpoint, cruising_speed, current_speed,
                       current_lane, preferred_lane, image, vehicle_style, *groups):
        super(Vehicle, self).__init__(*groups)
        self.cruising_speed = mph_to_px_per_ms(cruising_speed)
        self.current_speed = mph_to_px_per_ms(current_speed)
        self.current_lane = current_lane
        self.preferred_lane = preferred_lane
        self.previous_lane = None
        lane_change_time, max_decel, max_accel, top_speed, horn_sound, cost = VEHICLE_STYLES[vehicle_style]
        self.horn_sound = prepare.SFX[horn_sound]
        self.horn_loopable = True if horn_sound in LOOPABLE_HORNS else False
        self.image = prepare.GFX[image]
        self.rect = self.image.get_rect(center=centerpoint)
        self.mask = pg.mask.from_surface(self.image)
        self.x_pos, self.y_pos = centerpoint
        self.lane_change_time = lane_change_time
        self.steering = 64. / self.lane_change_time
        self.max_acceleration = mph_to_px_per_ms(max_accel) / 1000.
        self.max_deceleration = mph_to_px_per_ms(max_decel) / 1000.
        self.top_speed = mph_to_px_per_ms(top_speed)
        if self.cruising_speed > self.top_speed:
            self.cruising_speed = self.top_speed
        self.busy = False
        self.lane_time = 0
        self.crashed = False

    def accelerate(self, acceleration):
        if self.current_speed < self.top_speed:
            self.current_speed += acceleration

    def decelerate(self, deceleration):
        self.current_speed -= deceleration
        if self.current_speed < 0:
            self.current_speed = 0

    def check_open_lane(self, lanes, direction):
        current = lanes[self.current_lane]
        try:
            new_lane = lanes[self.current_lane + direction]
        except KeyError:
            return False
        cars = list(new_lane.sprites())
        cars.append(self)
        cars = sorted(cars, key=attrgetter("y_pos"))
        indx = cars.index(self)
        front = cars[:indx]
        back = cars[indx:][1:]
        left = new_lane.rect.left
        top = self.rect.top - (self.rect.h * .5)
        check_rect = pg.Rect(left, top, new_lane.rect.w, int(self.rect.h * 2))
        if front:
            if front[-1].current_speed < self.current_speed:
                speed_diff = self.current_speed - front[-1].current_speed
                if speed_diff * self.lane_change_time < self.y_pos - front[-1].y_pos:
                    return False
        if back:
            back_rect = back[0].rect.move(0, -back[0].current_speed * self.lane_change_time)
            moved = self.rect.copy()
            moved.centerx = new_lane.rect.centerx
            if back_rect.colliderect(moved):
                return False
        for car in new_lane:
            if car.rect.colliderect(check_rect):
                return False
        return True

    def set_current_lane(self, num):
        self.current_lane = num

    def toggle_busy(self):
        self.busy = not self.busy

    def change_lanes(self, direction, lanes, animations):
        current_lane = lanes[self.current_lane]
        new_lane = lanes[self.current_lane + direction]
        new_lane.add(self)
        self.busy = True
        self.previous_lane = self.current_lane
        self.current_lane = self.current_lane + direction
        self.lane_time = self.lane_change_time
        new_x = new_lane.rect.centerx
        self.destination_x = new_x

    def assess_situation(self, lanes, cars):
        home_lane = sorted((s for s in lanes[self.current_lane]),
                                     key=attrgetter("y_pos"))
        indx = home_lane.index(self)
        if indx == 0:
            situation = "no car"
            front_car = None
            front_distance = None
        else:
            front_car = home_lane[home_lane.index(self) - 1]
            front_distance = self.rect.top - front_car.rect.bottom

            if front_car.current_speed > self.current_speed:

                situation = "no car"
            elif front_distance > self.current_speed * 2500:

                situation = "no car"
            elif front_distance < self.current_speed * 700:
                situation = "close car"
            else:
                situation = "slow car"
        return situation, front_car

    def move(self, dt):
        self.y_pos = self.y_pos - (self.current_speed * dt)
        self.rect.center = self.x_pos, self.y_pos
        self.speed_ratio = min(1, self.current_speed / float(self.cruising_speed))

    def update(self, dt, lanes, cars, animations):

        if self.crashed:
            return
        if self.busy:

            if self.x_pos < self.destination_x:
                self.x_pos += min(self.steering * dt, self.destination_x - self.x_pos)
            elif self.x_pos > self.destination_x:
                self.x_pos -= min(self.steering * dt, self.x_pos - self.destination_x)
            else:
                self.busy = False
                lanes[self.previous_lane].remove(self)
            current_lane = lanes[self.current_lane]
            moved = self.rect.copy()
            moved.centerx = current_lane.rect.centerx
            for c in current_lane:
                if c is not self and c.rect.colliderect(moved):
                    if self.previous_lane < self.current_lane:
                        self.change_lanes(-1, lanes, animations)
                    elif self.previous_lane > self.current_lane:
                        self.change_lanes(1, lanes, animations)
                    break
            self.move(dt)

            return
        elif self.lane_time > 0:
            self.lane_time -= dt
        elif self.lane_time < 0:
            self.lane_time = 0
        situation, front_car = self.assess_situation(lanes, cars)

        if situation == "no car":
            if self.current_lane < self.preferred_lane and self.check_open_lane(lanes, 1) and self.lane_time <= 0:
                self.change_lanes(1, lanes, animations)
            elif self.current_lane > self.preferred_lane and self.check_open_lane(lanes, -1) and self.lane_time <= 0:
                self.change_lanes(-1, lanes, animations)
            elif self.check_open_lane(lanes, -1) and self.lane_time <= 0:
                self.change_lanes(-1, lanes, animations)
            else:
                speed_diff = self.current_speed - self.cruising_speed
                if speed_diff > 0:
                    decel = min(self.max_deceleration * dt, speed_diff)
                    self.decelerate(decel)
                elif speed_diff < 0:
                    accel = min(self.max_acceleration * dt, -(speed_diff))
                    self.accelerate(accel)
        elif situation == "close car":
            self.decelerate(self.max_deceleration * dt)
        elif situation == "slow car":
            right_open = self.check_open_lane(lanes, 1)
            left_open = self.check_open_lane(lanes, -1)
            if self.current_lane < self.preferred_lane and right_open and self.lane_time <= 0:
                self.change_lanes(1, lanes, animations)
            elif left_open and self.lane_time <= 0:
                self.change_lanes(-1, lanes, animations)
            elif right_open and self.lane_time <= 0:
                self.change_lanes(1, lanes, animations)
            else:
                target_speed = front_car.current_speed
                speed_diff = target_speed - self.current_speed
                if speed_diff < 0:
                    decel = min(self.max_deceleration * dt, -speed_diff)
                    self.decelerate(decel)
        self.move(dt)
