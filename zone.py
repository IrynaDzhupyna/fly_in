from dataclasses import dataclass, field
from enum import Enum


print("Hello from zone.py")

class Zone_role(Enum):
    START = "start"
    END = "end"
    HUB = "hub"


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

print("WSecond")

@dataclass
class Zone:
    """ A Zone hub in the drone network"""
    
    name: str
    coordinates: Coordinates
    role: Zone_role = Zone_role.HUB
    type: Zone_type = Zone_type.NORMAL
    color: str | None = None
    max_drones: int = 1

    occupants: int = field(default=0, init=False)
    connections: list[str] = field(default_factory=list, init=False)

    def increase_capacity(self, drones_to_move) -> bool:
        if self.type is Zone_type.BLOCKED:
            return False
        if self.occupants + drones_to_move < self.max_drones + 1:
            self.occupants += drones_to_move
            return True
        return False

    def decrease_capacity(self, drones_to_move):
        if self.occupants - drones_to_move >= 0:
            self.occupants -= drones_to_move
            return True
        return False

    def hub_info(self):
        print(f"Name: {self.name}\nCoordinates: {self.coordinates}")
        print(f"Type: {self.type}\nColor: {self.color}")
        print(f"Max_drones: {self.max_drones}")
        print(f"Capacity: {self.capacity}")


if __name__ == "__main__":

    coordinates = Coordinates(0, 0)
    hub = Zone("start", coordinates, "normal", None, 3)
    # 0
    hub.hub_info()
    print()
    hub.increase_capacity(3)
    hub.hub_info()
    print()
    # 3
    hub.increase_capacity(2)
    hub.hub_info()
    # # remove
    # # -1
    # print()
    # hub.decrease_capacity(1)
    # hub.hub_info()
    # # -1 
    # print()
    # hub.decrease_capacity(2)
    # hub.hub_info()

    # # try to remove again
    # print()
    # hub.decrease_capacity(1)
    # hub.hub_info()
