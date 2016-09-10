import os
import json


def load_user():
    p = os.path.join("resources", "player_save.json")
    try:
        with open(p, "r") as f:
            d = json.load(f)
    except IOError:
        d = {"mileage earned": 0,
               "mileage": 0,
               "miles travelled": 0,
               "total_time": 0,
               "best trip": 0,
               "crashes": 0,
               "unlocked": [],
               "achievements": []}
    return User(d)


class User(object):
    def __init__(self, user_dict):
        self.mileage_earned = user_dict["mileage earned"]
        self.mileage = user_dict["mileage"]
        self.best_trip = user_dict["best trip"]
        self.crashes = user_dict["crashes"]
        self.unlocked = user_dict["unlocked"]
        self.achievements = user_dict["achievements"]

    def to_dict(self):
        d = {"mileage earned": self.mileage_earned,
               "mileage": self.mileage,
               "best trip": self.best_trip,
               "crashes": self.crashes,
               "unlocked": self.unlocked,
               "achievements": self.achievements}
        return d

    def save(self):
        with open(os.path.join("resources", "player_save.json"), "w") as f:
            json.dump(self.to_dict(), f)
