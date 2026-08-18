from dataclasses import dataclass, field
from enum import Enum


class ZoneRole(Enum):
    REGULAR = "regular"
    START = "start"
    END = "end"

class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def movement_cost(self) -> int:
        return 2 if self is ZoneType.RESTRICTED else 1


@dataclass
class Zone:
    """A zone hub in the drone network."""

    name: str
    coordinates: tuple[int, int]
    role: ZoneRole = ZoneRole.REGULAR
    type: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = 1
    capacity: int = field(default=0, init=False)

    def increase_capacity(self, drones_to_move: int = 1) -> bool:
        """Try to add drones_to_move drones to this hub. Returns success."""
        if self.capacity + drones_to_move <= self.max_drones and self.type is not ZoneType.BLOCKED:
            self.capacity += drones_to_move
            return True
        return False

    def decrease_capacity(self, drones_to_move: int = 1) -> bool:
        """Try to remove drones_to_move drones from this hub. Returns success."""
        if self.capacity - drones_to_move >= 0:
            self.capacity -= drones_to_move
            return True
        return False

    def zone_info(self) -> None:
        print(f"Name: {self.name}")
        print(f"Type: {self.type}\nColor: {self.color}")
        print(f"Max_drones: {self.max_drones}")
        print(f"Capacity: {self.capacity}")