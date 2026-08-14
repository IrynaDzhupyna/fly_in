from dataclasses import dataclass, field
from enum import Enum

class Zone_type(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def movement_cost(self) -> int:
        return 2 if self is Zone_type.RESTRICTED else 1


@dataclass
class Coordinates:
    x: int
    y: int


@dataclass
class Hub:
    name: str
    coordinates: Coordinates
    type: Zone_type
    color: str| None = None
    max_drones: int = 1
    # field(init=False) capacity is not a part of __init__
    # user can't send it through parameters
    capacity: int = field(default=0, init=False)

    def increase_capacity(self, drones_to_move):
        if self.capacity + drones_to_move < self.max_drones + 1:
            self.capacity += drones_to_move
        # what if capacity is full
        # what if not enough capacity

    def decrease_capacity(self, drones_to_move):
        if self.capacity - drones_to_move >= 0:
            self.capacity -= drones_to_move
        # what if capacity is 0
        # or you want to move several drones but capacity is not enough


    def hub_info(self):
        print(f"Name: {self.name}\nCoordinates: {self.coordinates}")
        print(f"Type: {self.type}\nColor: {self.color}")
        print(f"Max_drones: {self.max_drones}")
        print(f"Capacity: {self.capacity}")


coordinates = Coordinates(0, 0)
hub = Hub("start", coordinates, "normal", None, 3)
# 0
hub.hub_info()
print()
hub.increase_capacity(1)
# 1
hub.hub_info()
print()
# 3
hub.increase_capacity(2)
hub.hub_info()
# remove
# -1
print()
hub.decrease_capacity(1)
hub.hub_info()
# -1 
print()
hub.decrease_capacity(2)
hub.hub_info()

# try to remove again
print()
hub.decrease_capacity(1)
hub.hub_info()


