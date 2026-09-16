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

    def __hash__(self):
        return hash(self.name)

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

    def info_zone(self) -> None:
        print(f"Name: {self.name}")
        print(f"Role: {self.role}")
        print(f"Type: {self.type}")
