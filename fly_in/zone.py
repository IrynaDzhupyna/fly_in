from dataclasses import dataclass, field
from enum import Enum


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

    def increase_capacity(self) -> bool:
        """Increases occupants by 1"""

        if not self.has_capacity():
            return False
        
        self.occupants += 1
        return True

    def decrease_capacity(self) -> bool:
        """Decreases occupants by 1"""

        if self.occupants - 1 >= 0:
            self.occupants -= 1
            return True
        
        return False

    def has_capacity(self) -> bool:
        """Checks if zone has capacity for one drone"""

        if self.type is Zone_type.BLOCKED:
            return False
        
        if self.role is Zone_role.START or self.role is Zone_role.END:
            return True
        
        return self.occupants < self.max_drones
    
    # def hub_info(self) -> None:
    #     print(f"Name: {self.name}\nCoordinates: {self.coordinates}")
    #     print(f"Type: {self.type}\nColor: {self.color}")
    #     print(f"Max_drones: {self.max_drones}")
    #     print(f"Occupants: {self.occupants}")


# if __name__ == "__main__":

#     coordinates = Coordinates(0, 0)
#     hub = Zone(name="start", coordinates=coordinates, type=Zone_type.NORMAL, max_drones=3)
#     # 0
#     hub.hub_info()
#     print()
#     hub.increase_capacity(3)
#     hub.hub_info()
#     print()
#     # 3
#     hub.increase_capacity(2)
#     hub.hub_info()
#     # # remove
#     # # -1
#     # print()
#     # hub.decrease_capacity(1)
#     # hub.hub_info()
#     # # -1 
#     # print()
#     # hub.decrease_capacity(2)
#     # hub.hub_info()

#     # # try to remove again
#     # print()
#     # hub.decrease_capacity(1)
#     # hub.hub_info()
