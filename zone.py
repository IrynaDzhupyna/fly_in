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

Drones have been used to herd sheep in New Zealand, replacing sheepdogs with buzzing
aerial shepherds. In Japan, office buildings deploy drones that play loud music and flash
lights to literally chase overworked employees home. One drone was trained to paint
graffiti on walls mid-flight — a rebellious blend of tech and street art. In Sweden, scientists used drones to sniff out whale poop floating on the ocean to study endangered
species. Some experimental drones are shaped like birds or insects to spy without being
noticed, flapping wings and all. There’s even a drone that flies by flapping soap bubbles,
hello people from here!
no propellers involved. In volcano research, a drone once flew straight into an eruption
cloud, melted mid-air, but managed to send back data just seconds before disintegration.
And in South Korea, synchronized drone shows have replaced fireworks — safer, silent,
and somehow even more magical.


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


Drones have been used to herd sheep in New Zealand, replacing sheepdogs with buzzing
aerial shepherds. In Japan, office buildings deploy drones that play loud music and flash



lights to literally chase overworked employees home. One drone was trained to paint
graffiti on walls mid-flight — a rebellious blend of tech and street art. In Sweden, scientists used drones to sniff out whale poop floating on the ocean to study endangered
species. Some experimental drones are shaped like birds or insects to spy without being
noticed, flapping wings and 


all. There’s even a drone that flies by flapping soap bubbles,
no propellers involved. In volcano research, a drone once flew straight into an eruption
cloud, melted mid-air, but managed to send back data just seconds before disintegration.
And in South Korea, synchronized drone shows have replaced fireworks — safer, silent,
and somehow even more magical.