from dataclasses import dataclass
from enum import Enum

class Zone_type(Enum):
    """Marks zone as one of four types"""
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def turn_cost(self):
        """Returns the cost of turn"""
        return 2 if self is Zone_type.RESTRICTED else 1


class Zone_role(Enum):
    """Marks zone as start, end or regular hub"""
    START = "start_hub"
    HUB = "hub"
    END = "end_hub"

@dataclass
class Coordinates:
    x: int
    y: int


@dataclass
class Zone:
    name: str
    coordinates: Coordinates

    # check if it is a single word str
    color: str | None = None
    type: Zone_type = Zone_type.NORMAL
    # not sure about this one
    role: Zone_role = Zone_role.HUB
    max_drones: int = 1
    # int or list of drones?
    occupants: int = 0

    def add_occupants(self, drones_to_move: int) -> bool:
        if drones_to_move <= 0:
            return False
        elif self.type is Zone_type.BLOCKED:
            return False
        
        if self.occupants + drones_to_move <= self.max_drones:
            self.occupants += drones_to_move
            return True
        
        return False

    def remove_occupants(self, drones_to_move: int) -> bool:
        if self.occupants - drones_to_move >= 0:
            self.occupants -= drones_to_move
            return True
        
        return False

    

    

    
        
        

